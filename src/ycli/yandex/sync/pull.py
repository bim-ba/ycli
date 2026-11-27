"""``pull``: the objects of a service as files, read from the server over what is there."""

import enum
from collections import Counter
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Protocol

from pydantic import BaseModel, Field

from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.errors import YandexError
from ycli.yandex.models import APIModel
from ycli.yandex.sync.document import Document, fields_marked, fingerprint, parts_of
from ycli.yandex.sync.kind import Kind, Operation, arguments_of
from ycli.yandex.sync.marks import Identity, Place, Version
from ycli.yandex.sync.paths import Tree, tree_of


class Sender(Protocol):
    """What sends the requests of one service: its client (``DomainClient``)."""

    def send[T](self, endpoint: Endpoint[T]) -> T:
        """Send one request and return its parsed reply."""
        ...

    def iterate[P, I](self, paged: Paged[P, I], *, limit: int | None = None) -> Iterator[I]:
        """Yield the items of a listing, page by page."""
        ...


class Action(enum.StrEnum):
    """What ``pull`` did with one object."""

    WRITTEN = "written"
    WOULD_WRITE = "would write"
    UNCHANGED = "unchanged"
    SKIPPED = "skipped"


class Pulled(APIModel):
    """One object ``pull`` met, and what became of it."""

    path: Annotated[str, Identity()] = Field(
        description="The file of the object, from the root of the repository."
    )
    kind: str = Field(description="The kind that read it.")
    action: Action = Field(
        description="Written (would be, when nothing is written), already the same, or skipped."
    )
    detail: str | None = Field(default=None, description="Why an object was skipped.")


class ScopeError(ValueError):
    """A path that names nothing ``pull`` can fetch; the message says what to name."""


def ask(sender: Sender, operation: Operation, named: dict[str, Any]) -> Any:
    """Call ``operation`` with ``named``; what nobody names and may be nothing goes as ``None``."""
    request = operation(**named, **dict.fromkeys(arguments_of(operation).left_out))
    return sender.iterate(request) if isinstance(request, Paged) else sender.send(request)


def _under(tree: Tree, scope: PurePosixPath) -> tuple[str, ...]:
    """The value of each container that ``scope`` names, for the listing of a kind."""
    parts = scope.with_suffix("").parts[1:]
    if tree.resource is None:
        if not parts:
            raise ScopeError(f"name what to pull: {tree.service}/<place>")
        return ("/".join(parts),)
    frame = tree.path(tuple("*" for _ in tree.containers), "*").with_suffix("").parts[1:-1]
    if len(parts) < len(frame) - 1 or any(
        want not in ("*", got) for want, got in zip(frame, parts, strict=False)
    ):
        where = "/".join((tree.service, *frame[:-1]))
        raise ScopeError(f"name where to pull from: {where}")
    return tuple(got for want, got in zip(frame, parts, strict=False) if want == "*")


def names(scope: PurePosixPath, path: PurePosixPath) -> bool:
    """Whether ``scope`` names the file ``path``: it is that file, or a directory above it.

    Args:
        scope: What a run was given: a file or a directory.
        path: The file of an object.

    Returns:
        Whether the run covers that file.

    Examples:
        >>> names(PurePosixPath("wiki/team"), PurePosixPath("wiki/team/onboarding.md"))
        True
        >>> names(PurePosixPath("wiki/team/gone.md"), PurePosixPath("wiki/team/onboarding.md"))
        False
    """
    within = scope.with_suffix("")
    return within == path.with_suffix("") or within in path.parents


def _path_of(
    kind: Kind[Any, Any], tree: Tree, held: tuple[str, ...], reply: BaseModel
) -> PurePosixPath:
    """Where the file of the object ``reply`` lies: along its place, or under its identity."""
    leaf = [getattr(reply, name) for name in fields_marked(type(reply), Place)] or [
        getattr(reply, name) for name in fields_marked(kind.link, Identity)
    ]
    return tree.path(held if tree.resource else (), "/".join(map(str, leaf)))


def documents_under(
    kind: Kind[Any, Any],
    senders: Callable[[str], Sender],
    scope: PurePosixPath,
    passed: Counter[str],
) -> Iterator[tuple[PurePosixPath, Document[Any, Any] | None]]:
    """Every object of ``kind`` under ``scope`` as its file; ``None`` for one the kind skips.

    An object the kind passes over is not read; ``passed`` counts it under the reason.
    """
    if kind.find is None:
        raise ScopeError(f"the API cannot list the objects of {kind.name}")
    tree = tree_of(kind)
    held = _under(tree, scope)
    # Asked for last: a path that names nothing to fetch needs no credentials to be refused.
    sender = senders(tree.service)
    found, read = arguments_of(kind.find), arguments_of(kind.read)
    places = dict(zip(read.container, held, strict=False))
    identity = fields_marked(kind.link, Identity)
    for item in ask(sender, kind.find, dict(zip(found.container, held, strict=True))):
        if kind.passes_over and (reason := kind.passes_over(item)):
            passed[reason] += 1
            continue
        ids = [getattr(item, name) for name in identity]
        named = places | dict(zip(read.identity, ids, strict=True))
        reply, version = _read(kind, sender, named)
        path = _path_of(kind, tree, held, reply)
        yield path, _as_document(kind, path, reply, version)


def _read(kind: Kind[Any, Any], sender: Sender, named: dict[str, Any]) -> tuple[BaseModel, Any]:
    """Read an object and the version it is at, in the order its kind's proof needs.

    The version may be asked before the read says whether the kind keeps the object at all (a
    grid among Wiki pages): a refusal to answer it then fails only an object the kind keeps.
    """
    (key,) = fields_marked(kind.link, Version) or [None]
    refused: list[YandexError] = []

    def reading() -> BaseModel:
        return ask(sender, kind.read, named)

    def asking(operation: Operation) -> Iterator[Any]:
        try:
            yield from ask(sender, operation, named)
        except YandexError as refusal:
            refused.append(refusal)

    if key is None:
        return reading(), None
    reply, version = kind.version.current(reading, key, asking)
    if refused and (kind.only is None or kind.only(reply)):
        raise refused[0]
    return reply, version


def _as_document(
    kind: Kind[Any, Any], path: PurePosixPath, reply: BaseModel, version: Any
) -> Document[Any, Any] | None:
    """What reading an object answered, as its file; ``None`` for one the kind does not keep."""
    if kind.only and not kind.only(reply):
        return None
    # A key the link holds is never content, whatever the content model declares.
    link = {key for name, info in kind.link.model_fields.items() for key in (name, info.alias)}
    taken = (
        set(kind.content.model_fields)
        | {info.alias for info in kind.content.model_fields.values() if info.alias}
    ) - link
    given = reply.model_dump(mode="json", by_alias=True, exclude_none=True)
    content = kind.content.model_validate({key: given[key] for key in given if key in taken})
    identity = fields_marked(kind.link, Identity)
    (key,) = fields_marked(kind.link, Version) or [None]
    link = {name: getattr(reply, name) for name in identity} | {"hash": fingerprint(content)}
    if key:
        link[key] = version
    held = kind.holds(reply) if kind.holds else None
    return Document(path=path, link=kind.link(**link), content=content, held=held)


def read_one(
    kind: Kind[Any, Any], sender: Sender, document: Document[Any, Any]
) -> Document[Any, Any] | None:
    """Read from the server the object that the file ``document`` stands for.

    Args:
        kind: The kind of the file.
        sender: The client of the kind's service.
        document: The file, read; its link names the object.

    Returns:
        The object as its file would be now, where the object says it lies (a copy of a file
        under another name holds an object that lies elsewhere); ``None`` when the kind does not
        keep it.
    """
    tree = tree_of(kind)
    read = arguments_of(kind.read)
    held, _ = tree.split(document.path)
    ids = [getattr(document.link, name) for name in fields_marked(kind.link, Identity)]
    named = dict(zip(read.container, held, strict=False)) | dict(
        zip(read.identity, ids, strict=True)
    )
    reply, version = _read(kind, sender, named)
    return _as_document(kind, _path_of(kind, tree, held, reply), reply, version)


def pull(
    root: Path,
    scope: PurePosixPath,
    kinds: Sequence[Kind[Any, Any]],
    senders: Callable[[str], Sender],
    *,
    write: bool = True,
) -> list[Pulled]:
    """Read the objects under ``scope`` from the server and write each as its file.

    A file is written over whatever is there: git is what protects a local edit. An object
    that no kind keeps is named and skipped.

    Args:
        root: The root of the repository.
        scope: What to pull: the directory of a container (``wiki/team``,
            ``tracker/queues/DE``) or a file under it.
        kinds: The declared kinds.
        senders: Gives the client of a service by its name.
        write: ``False`` reads everything and writes nothing.

    Returns:
        One outcome per object, by path.

    Raises:
        ScopeError: The path names no service that has a kind, or not enough to list from.
    """
    mine = [kind for kind in kinds if scope.parts and tree_of(kind).service == scope.parts[0]]
    if not mine:
        raise ScopeError(f"no kind keeps files under {scope}")
    done: list[Pulled] = []
    for kind in mine:
        passed: Counter[str] = Counter()
        for path, document in documents_under(kind, senders, scope, passed):
            if not names(scope, path):
                continue
            if document is None:
                skipped = Pulled(path=str(path), kind=kind.name, action=Action.SKIPPED)
                done.append(skipped.model_copy(update={"detail": "not an object this kind keeps"}))
                continue
            text = kind.layout.write(parts_of(document, kind=kind.name))
            target = root / path
            same = target.is_file() and target.read_text("utf-8") == text
            if write and not same:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            changed = Action.WRITTEN if write else Action.WOULD_WRITE
            action = Action.UNCHANGED if same else changed
            done.append(Pulled(path=str(path), kind=kind.name, action=action))
        # One line per reason, not per object: the listing names no file for what is not read.
        done += [
            Pulled(path=str(scope), kind=kind.name, action=Action.SKIPPED, detail=f"{n} {why}")
            for why, n in sorted(passed.items())
        ]
    return sorted(done, key=lambda outcome: outcome.path)
