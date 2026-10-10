"""The plan of a ``push``: each file beside the object it stands for, as the server has it now.

``diff`` prints the plan; ``push`` carries it out.
"""

import difflib
from collections.abc import Callable, Sequence
from pathlib import Path, PurePosixPath
from typing import Annotated, Any

from pydantic import BaseModel, Field

from ycli.yandex.errors import YandexNotFoundError
from ycli.yandex.models import APIModel, secret_keys
from ycli.yandex.sync.document import (
    Document,
    UnreadableFile,
    as_sent,
    fields_marked,
    fingerprint,
    parts_of,
)
from ycli.yandex.sync.files import State, files_under, offline_state, read_file
from ycli.yandex.sync.kind import Kind
from ycli.yandex.sync.marks import Identity, Version
from ycli.yandex.sync.paths import tree_of
from ycli.yandex.sync.pull import ScopeError, Sender, documents_under, read_one

MASK = "***"


class Planned(APIModel):
    """One file, or one object that has no file, and what ``push`` would do with it."""

    path: Annotated[str, Identity()] = Field(
        description="The file, from the root of the repository."
    )
    kind: str | None = Field(default=None, description="The kind of the file.")
    state: State = Field(description="What `push` would do with the file.")
    detail: str | None = Field(default=None, description="Why, where the state alone does not say.")
    diff: str | None = Field(
        default=None, description="From the object on the server to the file, as a unified diff."
    )


def _masked(value: Any, secrets: frozenset[str]) -> Any:
    """``value`` with every secret in it replaced by a mask, at any depth."""
    if isinstance(value, dict):
        return {
            key: MASK if key in secrets and held is not None else _masked(held, secrets)
            for key, held in value.items()
        }
    return [_masked(held, secrets) for held in value] if isinstance(value, list) else value


def _text(kind: Kind[Any, Any], document: Document[Any, Any], content: BaseModel) -> str:
    """``content`` laid out as the file of ``document``: under its link, so only content differs."""
    shown = document.model_copy(update={"content": content})
    return kind.layout.write(parts_of(shown, kind=kind.name))


def difference(
    kind: Kind[Any, Any],
    local: Document[Any, Any],
    server: Document[Any, Any],
    *,
    show_secrets: bool = False,
) -> tuple[str, list[str]]:
    """What sending the file would change on the server.

    Both sides are laid out as the same file under the same link, so the link itself never
    shows up as a change. A secret is masked on both sides: whether it differs is said by its
    name alone.

    Args:
        kind: The kind of the file.
        local: The file, read.
        server: The object as its file would be now.
        show_secrets: Show secrets as they are.

    Returns:
        A unified diff from the server's content to the file's, and the names of the secrets
        that differ.
    """
    secrets = frozenset() if show_secrets else secret_keys(kind.content)
    sides = []
    for side in (server, local):
        sent = as_sent(side.content)
        sides.append(_text(kind, local, kind.content.model_validate(_masked(sent, secrets))))
    path = str(local.path)
    lines = difflib.unified_diff(
        sides[0].splitlines(keepends=True),
        sides[1].splitlines(keepends=True),
        fromfile=f"server/{path}",
        tofile=f"local/{path}",
    )
    theirs, ours = as_sent(server.content), as_sent(local.content)
    changed = sorted(key for key in secrets if theirs.get(key) != ours.get(key))
    return "".join(lines), changed


def compared(
    kind: Kind[Any, Any],
    local: Document[Any, Any],
    server: Document[Any, Any],
    *,
    show_secrets: bool,
) -> Planned:
    """Say what ``push`` would do with a file whose object was read, and the difference.

    Args:
        kind: The kind of the file.
        local: The file, read.
        server: The object as its file would be now.
        show_secrets: Show secrets as they are in the difference.

    Returns:
        The entry of the plan for the file.
    """
    state, detail = offline_state(kind, local)
    version = next(iter(fields_marked(kind.link, Version)), None)
    moved = server.link.hash != local.link.hash or (
        version is not None and getattr(server.link, version) != getattr(local.link, version)
    )
    if state is not State.UNTRACKED and moved:
        state, detail = State.CHANGED_ON_SERVER, "the object changed since the file was read"
    text, secrets = "", []
    if fingerprint(server.content) != fingerprint(local.content):
        text, secrets = difference(kind, local, server, show_secrets=show_secrets)
    if secrets:
        detail = "; ".join(filter(None, [detail, f"secret changed: {', '.join(secrets)}"]))
    return Planned(
        path=str(local.path), kind=kind.name, state=state, detail=detail, diff=text or None
    )


type Entry = tuple[Planned, Kind[Any, Any] | None, Document[Any, Any] | None]


def plan(
    root: Path,
    scopes: Sequence[PurePosixPath],
    kinds: Sequence[Kind[Any, Any]],
    senders: Callable[[str], Sender],
    *,
    show_secrets: bool = False,
) -> list[Planned]:
    """Compare each file under ``scopes`` with the object it stands for, reading the server.

    Args:
        root: The root of the repository.
        scopes: The files and directories to look at; none means the directory of every
            service that has a kind.
        kinds: The declared kinds.
        senders: Gives the client of a service by its name.
        show_secrets: Show secrets as they are in a difference.

    Returns:
        One entry per file and per object without a file, by path.
    """
    found = entries(root, scopes, kinds, senders, show_secrets=show_secrets)
    return [planned for planned, _, _ in found]


def entries(
    root: Path,
    scopes: Sequence[PurePosixPath],
    kinds: Sequence[Kind[Any, Any]],
    senders: Callable[[str], Sender],
    *,
    show_secrets: bool = False,
) -> list[Entry]:
    """The plan with what ``push`` needs to carry it out: the kind and the file, read.

    A file that names no object is read from nowhere. A path that names a container and is
    no file has the container listed too, and an object in it that has no file is said.

    Args:
        root: The root of the repository.
        scopes: The files and directories to look at; none means the directory of every
            service that has a kind.
        kinds: The declared kinds.
        senders: Gives the client of a service by its name.
        show_secrets: Show secrets as they are in a difference.

    Returns:
        One entry per file and per object without a file, by path, each with its kind and
        its file where there is one.
    """
    by_name = {kind.name: kind for kind in kinds}
    suffixes = {kind.layout.suffix for kind in kinds}
    everything = sorted({PurePosixPath(tree_of(kind).service) for kind in kinds})
    planned: dict[str, Entry] = {}
    for scope in scopes or everything:
        listed: dict[PurePosixPath, tuple[Kind[Any, Any], Document[Any, Any] | None]] = {}
        if not (root / scope).is_file():
            for kind in kinds:
                if tree_of(kind).service != scope.parts[0]:
                    continue
                try:
                    listed |= {
                        path: (kind, document)
                        for path, document in documents_under(kind, senders, scope)
                    }
                except ScopeError:  # the directory names no container of this kind
                    continue
        for path in files_under(root, scope, suffixes):
            try:
                kind, local = read_file(path, (root / path).read_text("utf-8"), by_name)
            except UnreadableFile as refusal:
                detail = f"line {refusal.line}: {refusal.reason}"
                unreadable = Planned(path=str(path), state=State.UNREADABLE, detail=detail)
                planned[str(path)] = (unreadable, None, None)
                continue
            state, detail = offline_state(kind, local)
            if state in {State.CREATE, State.UNSUPPORTED} and local.link.hash is None:
                # It names no object: there is nothing on the server to read.
                new = Planned(path=str(path), kind=kind.name, state=state, detail=detail)
                planned[str(path)] = (new, kind, local)
                continue
            try:
                server = (
                    listed[path][1]
                    if path in listed
                    else read_one(kind, senders(tree_of(kind).service), local)
                )
            except YandexNotFoundError:
                gone = Planned(path=str(path), kind=kind.name, state=State.GONE)
                planned[str(path)] = (gone, kind, local)
                continue
            if server is None:
                why = f"the object is not one a {kind.name} file keeps"
                other = Planned(path=str(path), kind=kind.name, state=State.UNSUPPORTED, detail=why)
                planned[str(path)] = (other, kind, local)
                continue
            both = compared(kind, local, server, show_secrets=show_secrets)
            planned[str(path)] = (both, kind, local)
        for path, (kind, document) in listed.items():
            if document is not None and str(path) not in planned:
                absent = Planned(
                    path=str(path),
                    kind=kind.name,
                    state=State.NO_FILE,
                    detail="`ycli sync pull` writes it",
                )
                planned[str(path)] = (absent, kind, None)
    return [planned[path] for path in sorted(planned)]
