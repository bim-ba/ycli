"""``push``: the plan carried out, one file at a time, each write read back and compared."""

import enum
import subprocess
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, get_type_hints

from pydantic import BaseModel, Field, ValidationError

from ycli.yandex.errors import YandexError
from ycli.yandex.models import APIModel, field_error
from ycli.yandex.sync.document import Document, UnreadableFile, as_sent, fields_marked, parts_of
from ycli.yandex.sync.files import State, read_file
from ycli.yandex.sync.kind import Kind, Operation, arguments_of
from ycli.yandex.sync.marks import Identity, Place, Version
from ycli.yandex.sync.paths import tree_of
from ycli.yandex.sync.plan import Planned, entries
from ycli.yandex.sync.pull import ScopeError, Sender, ask, read_one


class Result(enum.StrEnum):
    """What ``push`` did with one file."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    UNCHANGED = "unchanged"
    STOPPED = "stopped"
    FAILED = "failed"


class OnError(enum.StrEnum):
    """What a run does after a file fails."""

    FAIL = "fail"
    ABORT = "abort"


class Pushed(APIModel):
    """One file and what ``push`` did with it."""

    path: Annotated[str, Identity()] = Field(
        description="The file, from the root of the repository."
    )
    kind: str | None = Field(default=None, description="The kind of the file.")
    state: State = Field(description="What the plan said of the file.")
    result: Result = Field(description="What was done.")
    detail: str | None = Field(default=None, description="Why a file stopped or failed.")
    added: bool = Field(
        default=False,
        description="The file now also holds what the service added to what was sent.",
    )


#: The states that stop a file: it and its object went apart, and a pull comes first.
APART = {
    State.CHANGED_ON_SERVER: "the object changed on the server: pull, then push",
    State.UNTRACKED: "the file was never read from its object: pull, then push",
    State.GONE: "the server has no such object",
}


class _RefusedError(Exception):
    """A file that cannot be pushed; the message says why."""


def lost(sent: Any, saved: Any, at: str = "") -> list[str]:
    """Where ``saved`` does not hold what was ``sent``, as dotted paths.

    What the server adds of its own is no loss: only what was sent is looked for.

    Args:
        sent: What the request carried.
        saved: What reading the object back answered.
        at: The path of the two values (for the recursion).

    Returns:
        The paths of the values that were sent and are not there.

    Examples:
        >>> lost({"name": "A", "actions": [{"type": "x"}]}, {"name": "A", "actions": []})
        ['actions.0']
        >>> lost({"name": "A"}, {"name": "A", "order": "0.1"})
        []
    """
    if isinstance(sent, dict) and isinstance(saved, dict):
        return [
            path
            for key, value in sent.items()
            for path in lost(value, saved.get(key), f"{at}.{key}" if at else key)
        ]
    if isinstance(sent, list) and isinstance(saved, list):
        return [
            path
            for index, value in enumerate(sent)
            for path in lost(
                value, saved[index] if index < len(saved) else None, f"{at}.{index}".lstrip(".")
            )
        ]
    return [] if sent == saved else [at]


def _body(operation: Operation, content: BaseModel, place: str | None = None) -> dict[str, Any]:
    """The body argument of ``operation`` from the content of a file, by the name it takes.

    ``place`` is where a new file lies: it fills the field of the body marked ``Place``.
    """
    name = arguments_of(operation).body
    assert name is not None  # the check of every declared kind refuses a write with no body
    model: type[BaseModel] = get_type_hints(getattr(operation, "func", operation))[name]
    placed = dict.fromkeys(fields_marked(model, Place), place) if place else {}
    try:
        return {name: model.model_validate(as_sent(content) | placed)}
    except ValidationError as refusal:
        raise _RefusedError("; ".join(map(field_error, refusal.errors()))) from None


def _write(
    root: Path, kind: Kind[Any, Any], old: PurePosixPath, document: Document[Any, Any]
) -> None:
    """Write ``document`` as its file; a file that lay under another name is moved."""
    target = root / document.path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(kind.layout.write(parts_of(document, kind=kind.name)), encoding="utf-8")
    if old != document.path:
        (root / old).unlink()


def _saved(
    root: Path,
    kind: Kind[Any, Any],
    sender: Sender,
    local: Document[Any, Any],
    named: Document[Any, Any],
) -> bool:
    """Read back what was written, compare it with what was sent, and write the file anew.

    Returns whether the service added something of its own, which the file now holds.
    """
    saved = read_one(kind, sender, named)
    if saved is None:
        raise _RefusedError(
            f"written, and what the server holds now is not one a {kind.name} keeps"
        )
    missing = lost(as_sent(local.content), as_sent(saved.content))
    if missing:
        # The header keeps the old link, so the next `diff` shows the file against the server.
        raise _RefusedError(f"written, and the server did not keep: {', '.join(missing)}")
    # What the server added of its own is in the file from now on, as `pull` would write it.
    _write(root, kind, local.path, saved)
    return as_sent(saved.content) != as_sent(local.content)


def _create(
    root: Path, kind: Kind[Any, Any], sender: Sender, local: Document[Any, Any]
) -> tuple[str, bool]:
    """Create the object of a file that names none; the file gets its link.

    Returns the path of the file from now on, and whether the service added something.
    """
    assert kind.create is not None  # the plan says `unsupported` otherwise
    tree = tree_of(kind)
    held, leaf = tree.split(local.path)
    call = dict(zip(arguments_of(kind.create).container, held, strict=False))
    reply = ask(sender, kind.create, call | _body(kind.create, local.content, leaf))
    keys = fields_marked(kind.link, Identity)
    link = kind.link(**{key: getattr(reply, key) for key in keys})
    # A file that lies under its identity is named by it: a new one is moved there.
    named = "/".join(str(getattr(link, key)) for key in keys)
    path = tree.path(held, named) if tree.resource else local.path
    linked = local.model_copy(update={"link": link, "path": path})
    return str(path), _saved(root, kind, sender, local, linked)


def _update(root: Path, kind: Kind[Any, Any], sender: Sender, local: Document[Any, Any]) -> bool:
    """Send the content of an edited file to its object and write the new link.

    Returns whether the service added something of its own.
    """
    assert kind.update is not None
    update = arguments_of(kind.update)
    held, _ = tree_of(kind).split(local.path)
    ids = [getattr(local.link, key) for key in fields_marked(kind.link, Identity)]
    call = dict(zip(update.container, held, strict=False)) | dict(
        zip(update.identity, ids, strict=True)
    )
    version = next(iter(fields_marked(kind.link, Version)), None)
    if update.version and version:
        call[update.version] = getattr(local.link, version)
    ask(sender, kind.update, call | _body(kind.update, local.content))
    return _saved(root, kind, sender, local, local)


def push(
    root: Path,
    scopes: Sequence[PurePosixPath],
    kinds: Sequence[Kind[Any, Any]],
    senders: Callable[[str], Sender],
    *,
    on_error: OnError = OnError.FAIL,
) -> Iterator[Pushed]:
    """Send every file under ``scopes`` that differs from its object, one at a time.

    Each write is read back: the file gets the link of what the server holds now, and a
    value that was sent and was not kept fails the file aloud. A file whose object changed
    on the server, is gone, or was never read is stopped and nothing of it is sent.

    Args:
        root: The root of the repository.
        scopes: The files and directories to push; none means the directory of every
            service that has a kind.
        kinds: The declared kinds.
        senders: Gives the client of a service by its name.
        on_error: ``fail`` goes on to the next file after a failure; ``abort`` ends the run.

    Yields:
        Pushed: What was done with each file, by path.
    """
    for planned, kind, local in entries(root, scopes, kinds, senders):
        said: dict[str, Any] = {
            "path": planned.path,
            "kind": planned.kind,
            "state": planned.state,
        }
        if planned.state is State.NO_FILE:
            continue  # `pull` writes it; `push` has nothing to send
        if planned.state is State.UNCHANGED:
            done = Pushed(**said, result=Result.UNCHANGED)
        elif planned.state in APART:
            done = Pushed(**said, result=Result.STOPPED, detail=APART[planned.state])
        elif kind is None or local is None or planned.state is State.UNSUPPORTED:
            done = Pushed(**said, result=Result.FAILED, detail=planned.detail)
        else:
            sender = senders(tree_of(kind).service)
            try:
                if planned.state is State.CREATE:
                    said["path"], added = _create(root, kind, sender, local)
                    done = Pushed(**said, result=Result.CREATED, added=added)
                else:
                    added = _update(root, kind, sender, local)
                    done = Pushed(**said, result=Result.UPDATED, added=added)
            except (YandexError, _RefusedError) as failure:
                done = Pushed(**said, result=Result.FAILED, detail=str(failure))
        yield done
        if done.result is Result.FAILED and on_error is OnError.ABORT:
            return


type Candidate = tuple[Planned, Kind[Any, Any], dict[str, Any]]


def _deleted_since(
    root: Path, commit: str, scopes: Sequence[PurePosixPath]
) -> list[tuple[str, str]]:
    """The files git says were deleted since ``commit``, each with what it held then."""
    names = ["git", "diff", "--name-only", "--diff-filter=D", "-z", commit, "--", *map(str, scopes)]
    try:
        told = subprocess.check_output(names, cwd=root, text=True, stderr=subprocess.DEVNULL)
        return [
            (
                path,
                subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=root, text=True),
            )
            for path in told.split("\0")
            if path
        ]
    except (OSError, subprocess.CalledProcessError):
        raise ScopeError(f"--prune reads git: no commit {commit!r} in a repository here") from None


def prunable(
    root: Path, commit: str, scopes: Sequence[PurePosixPath], kinds: Sequence[Kind[Any, Any]]
) -> list[Candidate]:
    """The objects whose files were deleted since ``commit``; uses no network.

    The identity of each is what its file held at that commit; an object that never had a
    file is never a candidate. Outside a git repository, or with no such commit, the refusal
    is a ``ScopeError``.

    Args:
        root: The root of the repository.
        commit: The commit since which a deleted file means "delete the object".
        scopes: The files and directories to look under; none means everything.
        kinds: The declared kinds.

    Returns:
        Each candidate as an entry of the plan, with its kind and the arguments that name it.
    """
    by_name = {kind.name: kind for kind in kinds}
    suffixes = {kind.layout.suffix for kind in kinds}
    found: list[Candidate] = []
    for name, text in _deleted_since(root, commit, scopes):
        path = PurePosixPath(name)
        if path.suffix not in suffixes:
            continue
        try:
            kind, was = read_file(path, text, by_name)
        except UnreadableFile:
            continue  # it was no file of a kind then: deleting it deletes nothing
        ids = [getattr(was.link, key) for key in fields_marked(kind.link, Identity)]
        if not ids or None in ids:
            continue  # it named no object: there is nothing to delete
        if kind.delete is None:
            why = f"the API cannot delete a {kind.name}"
            unsupported = Planned(path=name, kind=kind.name, state=State.UNSUPPORTED, detail=why)
            found.append((unsupported, kind, {}))
            continue
        delete = arguments_of(kind.delete)
        held, _ = tree_of(kind).split(path)
        call = dict(zip(delete.container, held, strict=False)) | dict(
            zip(delete.identity, ids, strict=True)
        )
        found.append((Planned(path=name, kind=kind.name, state=State.DELETE), kind, call))
    return found


def prune(candidates: Sequence[Candidate], senders: Callable[[str], Sender]) -> Iterator[Pushed]:
    """Delete the objects ``candidates`` name.

    Args:
        candidates: What :func:`prunable` found.
        senders: Gives the client of a service by its name.

    Yields:
        Pushed: What was done with each, by path.
    """
    for planned, kind, call in candidates:
        said: dict[str, Any] = {
            "path": planned.path,
            "kind": planned.kind,
            "state": planned.state,
        }
        if kind.delete is None or planned.state is not State.DELETE:
            yield Pushed(**said, result=Result.FAILED, detail=planned.detail)
            continue
        try:
            ask(senders(tree_of(kind).service), kind.delete, call)
        except YandexError as failure:
            yield Pushed(**said, result=Result.FAILED, detail=str(failure))
            continue
        yield Pushed(**said, result=Result.DELETED)
