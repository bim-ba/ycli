"""The files of a repository as the engine sees them, with no network: what each is now."""

import enum
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Annotated, Any

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.sync.document import (
    Document,
    UnreadableFile,
    document_of,
    fields_marked,
    fingerprint,
)
from ycli.yandex.sync.kind import Kind
from ycli.yandex.sync.marks import Identity
from ycli.yandex.sync.paths import tree_of


class State(enum.StrEnum):
    """What ``push`` would do with a file: one vocabulary for ``status``, ``diff`` and ``push``.

    ``status`` reads nothing but the files, so it says the first six; the rest need the server.
    """

    UNCHANGED = "unchanged"
    UPDATE = "update"
    CREATE = "create"
    UNTRACKED = "untracked"
    UNSUPPORTED = "unsupported"
    UNREADABLE = "unreadable"
    CHANGED_ON_SERVER = "changed-on-server"
    GONE = "gone"
    NO_FILE = "no-file"
    DELETE = "delete"


#: What can be said of a file with no network.
OFFLINE = (
    State.UNCHANGED,
    State.UPDATE,
    State.CREATE,
    State.UNTRACKED,
    State.UNSUPPORTED,
    State.UNREADABLE,
)


class FileState(APIModel):
    """One file of a repository and what it is now."""

    path: Annotated[str, Identity()] = Field(
        description="Where the file lies, from the root of the repository."
    )
    kind: str | None = Field(default=None, description="The kind the file names.")
    state: State = Field(description="What `push` would do with the file.")
    detail: str | None = Field(
        default=None, description="Why a file is unreadable, or what its kind cannot do."
    )


def read_file(
    path: PurePosixPath, text: str, kinds: Mapping[str, Kind[Any, Any]]
) -> tuple[Kind[Any, Any], Document[Any, Any]]:
    """Read one file as a document of the kind it names.

    Args:
        path: Where the file lies, from the root of the repository.
        text: What the file holds.
        kinds: The declared kinds, by name.

    Returns:
        The kind and the document.

    Raises:
        UnreadableFile: The file is not a file of a declared kind, or lies where files of its
            kind do not.
    """
    layouts = {kind.layout.suffix: kind.layout for kind in kinds.values()}
    if path.suffix not in layouts:
        raise UnreadableFile(path, 1, f"no kind keeps a file that ends in {path.suffix!r}")
    parts = layouts[path.suffix].read(path, text)
    kind = kinds.get(parts.kind)
    if kind is None:
        raise UnreadableFile(path, parts.lines.get("ycli", 1), f"no such kind: {parts.kind}")
    tree = tree_of(kind)
    _, leaf = tree.split(path)
    document = document_of(parts, link=kind.link, content=kind.content)
    keys = fields_marked(kind.link, Identity)
    held = [str(value) for key in keys if (value := getattr(document.link, key)) is not None]
    # A file that lies under its identity is named by it: a copy keeps the name of its own.
    if tree.resource and held and "/".join(held) != leaf:
        line = parts.lines.get(keys[0], 1)
        raise UnreadableFile(path, line, f"the file is named {leaf} and holds {'/'.join(held)}")
    return kind, document


def offline_state(kind: Kind[Any, Any], document: Document[Any, Any]) -> tuple[State, str | None]:
    """What ``push`` would do with ``document``, as far as the file alone says.

    Args:
        kind: The kind of the file.
        document: The file, read.

    Returns:
        The state, and what the kind cannot do when that is why.
    """
    named = any(getattr(document.link, key) for key in fields_marked(kind.link, Identity))
    if document.link.hash is None:
        state = State.UNTRACKED if named else State.CREATE
    elif document.link.hash == fingerprint(document.content):
        state = State.UNCHANGED
    else:
        state = State.UPDATE
    needed = {State.CREATE: kind.create, State.UPDATE: kind.update}
    if state in needed and needed[state] is None:
        return State.UNSUPPORTED, f"the API cannot {state} a {kind.name}"
    if state is State.CREATE:
        # Said beforehand: `push` writes into the file, and may move it.
        moved = " and the name of its object" if tree_of(kind).resource else ""
        return state, f"once created, the file gets its identity{moved}"
    return state, None


def files_under(root: Path, scope: PurePosixPath, suffixes: set[str]) -> Iterator[PurePosixPath]:
    """The files that ``scope`` names and that a kind could keep, by path.

    A directory names the files under it and the file beside it of the same name: the page
    ``wiki/team.md`` and the pages under ``wiki/team/``, as ``pull wiki/team`` writes them.
    """
    start = root / scope
    if start.is_file():
        found = [start]
    else:
        beside = [start.with_name(start.name + suffix) for suffix in sorted(suffixes)]
        found = [*beside, *(sorted(start.rglob("*")) if start.is_dir() else [])]
    for path in found:
        if path.is_file() and path.suffix in suffixes:
            yield PurePosixPath(path.relative_to(root).as_posix())


def examine(
    root: Path, scopes: Sequence[PurePosixPath], kinds: Sequence[Kind[Any, Any]]
) -> list[FileState]:
    """Say what each file under ``scopes`` is now, reading nothing but the files.

    A file is to ``update`` when the fingerprint of its content is not the ``hash`` it
    carries. One that carries none was written by hand: to ``create`` when it names no object,
    ``untracked`` when it names one that it was never read from. Where the API of its kind
    cannot create or update, the file is ``unsupported``.

    Args:
        root: The root of the repository.
        scopes: The files and directories to look at; none means the directory of every
            service that has a kind.
        kinds: The declared kinds.

    Returns:
        One state per file, by path.
    """
    by_name = {kind.name: kind for kind in kinds}
    suffixes = {kind.layout.suffix for kind in kinds}
    everything = sorted({PurePosixPath(tree_of(kind).service) for kind in kinds})
    states = []
    for scope in scopes or everything:
        for path in files_under(root, scope, suffixes):
            try:
                kind, document = read_file(path, (root / path).read_text("utf-8"), by_name)
            except UnreadableFile as refusal:
                detail = f"line {refusal.line}: {refusal.reason}"
                states.append(FileState(path=str(path), state=State.UNREADABLE, detail=detail))
                continue
            state, detail = offline_state(kind, document)
            states.append(FileState(path=str(path), kind=kind.name, state=state, detail=detail))
    return states
