"""``pull``: the objects of a service as files, read from the server over what is there."""

import enum
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from pydantic import BaseModel, Field

from ycli.yandex.core.endpoint import Endpoint, Paged
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

    path: str = Field(description="The file of the object, from the root of the repository.")
    kind: str = Field(description="The kind that read it.")
    action: Action = Field(
        description="Written (would be, when nothing is written), already the same, or skipped."
    )
    detail: str | None = Field(default=None, description="Why an object was skipped.")


class ScopeError(ValueError):
    """A path that names nothing ``pull`` can fetch; the message says what to name."""


def _ask(sender: Sender, operation: Operation, named: dict[str, Any]) -> Any:
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


def _documents(
    kind: Kind[Any, Any], senders: Callable[[str], Sender], scope: PurePosixPath
) -> Iterator[tuple[PurePosixPath, Document[Any, Any] | None]]:
    """Every object of ``kind`` under ``scope`` as its file; ``None`` for one the kind skips."""
    if kind.find is None:
        raise ScopeError(f"the API cannot list the objects of {kind.name}")
    tree = tree_of(kind)
    held = _under(tree, scope)
    # Asked for last: a path that names nothing to fetch needs no credentials to be refused.
    sender = senders(tree.service)
    found, read = arguments_of(kind.find), arguments_of(kind.read)
    places = dict(zip(read.container, held, strict=False))
    identity = fields_marked(kind.link, Identity)
    (version,) = fields_marked(kind.link, Version) or [None]
    for item in _ask(sender, kind.find, dict(zip(found.container, held, strict=True))):
        ids = [getattr(item, name) for name in identity]
        named = places | dict(zip(read.identity, ids, strict=True))
        reply: BaseModel = _ask(sender, kind.read, named)
        leaf = [getattr(reply, name) for name in fields_marked(type(reply), Place)] or [
            getattr(reply, name) for name in identity
        ]
        path = tree.path(held if tree.resource else (), "/".join(map(str, leaf)))
        if kind.only and not kind.only(reply):
            yield path, None
            continue
        taken = set(kind.content.model_fields) | {
            info.alias for info in kind.content.model_fields.values() if info.alias
        }
        given = reply.model_dump(mode="json", by_alias=True, exclude_none=True)
        content = kind.content.model_validate({key: given[key] for key in given if key in taken})
        link = {name: getattr(reply, name) for name in identity} | {"hash": fingerprint(content)}
        if version:
            link[version] = kind.version.current(
                reply, version, lambda operation, named=named: _ask(sender, operation, named)
            )
        yield path, Document(path=path, link=kind.link(**link), content=content)


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
    within = scope.with_suffix("")
    for kind in mine:
        for path, document in _documents(kind, senders, scope):
            if within != path.with_suffix("") and within not in path.parents:
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
    return sorted(done, key=lambda outcome: outcome.path)
