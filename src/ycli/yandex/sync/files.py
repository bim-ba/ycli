"""The files of a repository as the engine sees them, with no network: what each is now."""

import enum
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.sync.document import Document, UnreadableFile, document_of, fingerprint
from ycli.yandex.sync.kind import Kind
from ycli.yandex.sync.paths import tree_of


class State(enum.StrEnum):
    """What a file is, compared with what it was read from."""

    UNCHANGED = "unchanged"
    EDITED = "edited"
    NEW = "new"
    UNREADABLE = "unreadable"


class FileState(APIModel):
    """One file of a repository and what it is now."""

    path: str = Field(description="Where the file lies, from the root of the repository.")
    kind: str | None = Field(default=None, description="The kind the file names.")
    state: State = Field(description="Unchanged, edited since it was read, new, or unreadable.")
    detail: str | None = Field(default=None, description="Why a file is unreadable.")


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
    tree_of(kind).split(path)
    return kind, document_of(parts, link=kind.link, content=kind.content)


def _files(root: Path, scope: PurePosixPath, suffixes: set[str]) -> Iterator[PurePosixPath]:
    """The files under ``scope`` that a kind could keep, by path."""
    start = root / scope
    found = [start] if start.is_file() else sorted(start.rglob("*")) if start.is_dir() else []
    for path in found:
        if path.is_file() and path.suffix in suffixes:
            yield PurePosixPath(path.relative_to(root).as_posix())


def examine(
    root: Path, scopes: Sequence[PurePosixPath], kinds: Sequence[Kind[Any, Any]]
) -> list[FileState]:
    """Say what each file under ``scopes`` is now, reading nothing but the files.

    A file is edited when the fingerprint of its content is not the ``hash`` it carries, and
    new when it carries none: it was written by hand and never read from the server.

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
        for path in _files(root, scope, suffixes):
            try:
                kind, document = read_file(path, (root / path).read_text("utf-8"), by_name)
            except UnreadableFile as refusal:
                detail = f"line {refusal.line}: {refusal.reason}"
                states.append(FileState(path=str(path), state=State.UNREADABLE, detail=detail))
                continue
            if document.link.hash is None:
                state = State.NEW
            elif document.link.hash == fingerprint(document.content):
                state = State.UNCHANGED
            else:
                state = State.EDITED
            states.append(FileState(path=str(path), kind=kind.name, state=state))
    return states
