"""Where the files of a kind lie: a path from an object, and an object's place from a path."""

from dataclasses import dataclass
from functools import partial
from pathlib import PurePosixPath
from typing import Any, get_args, get_type_hints

from pydantic import BaseModel

from ycli.yandex.sync.document import UnreadableFile
from ycli.yandex.sync.kind import Kind, Operation
from ycli.yandex.sync.marks import Container, Place


@dataclass(frozen=True)
class Tree:
    """The layout of one kind's files under the directory of its service.

    A kind whose object says where it lies (a field marked ``Place``: the ``slug`` of a page)
    has ``resource=None`` and its files lie along that field: ``wiki/team/onboarding.md``. Any
    other kind lies under its containers and its own resource:
    ``tracker/queues/DE/triggers/16.yaml``.

    Examples:
        >>> triggers = Tree("tracker", ("queues",), "triggers", ".yaml")
        >>> triggers.path(("DE",), "16")
        PurePosixPath('tracker/queues/DE/triggers/16.yaml')
        >>> triggers.split(PurePosixPath("tracker/queues/DE/triggers/16.yaml"))
        (('DE',), '16')
        >>> Tree("wiki", (), None, ".md").split(PurePosixPath("wiki/team/onboarding.md"))
        ((), 'team/onboarding')
    """

    service: str
    containers: tuple[str, ...]
    resource: str | None
    suffix: str

    def path(self, containers: tuple[str, ...], leaf: str) -> PurePosixPath:
        """The path of the file of one object.

        Args:
            containers: The value of each container, outermost first.
            leaf: What names the object under them: its place, or its identity.

        Returns:
            The path, from the root of the repository.
        """
        held = [part for pair in zip(self.containers, containers, strict=True) for part in pair]
        own = [self.resource] if self.resource else []
        return PurePosixPath(self.service, *held, *own, leaf + self.suffix)

    def split(self, path: PurePosixPath) -> tuple[tuple[str, ...], str]:
        """Take the path of a file apart: the values of its containers, and its leaf.

        Args:
            path: The path of a file, from the root of the repository.

        Returns:
            The values of the containers, outermost first, and the leaf.

        Raises:
            UnreadableFile: The path does not lie where files of the kind lie.
        """
        frame = self.path(tuple("*" for _ in self.containers), "*").with_suffix("").parts
        parts = path.with_suffix("").parts
        fits = (
            path.suffix == self.suffix
            # A place may be several parts long; an identity is one.
            and (len(parts) >= len(frame) if self.resource is None else len(parts) == len(frame))
            and all(want in ("*", got) for want, got in zip(frame, parts, strict=False))
        )
        if not fits:
            where = "/".join(frame) + self.suffix
            raise UnreadableFile(path, 1, f"a file of this kind lies at {where}")
        values = tuple(got for want, got in zip(frame[:-1], parts, strict=False) if want == "*")
        return values, "/".join(parts[len(frame) - 1 :])


def _described(operation: Operation) -> Any:
    return operation.func if isinstance(operation, partial) else operation


def _resource(module: str) -> str:
    """The name of the resource a module belongs to: the directory that holds it."""
    return module.rpartition(".")[0].rpartition(".")[2]


def tree_of(kind: Kind[Any, Any]) -> Tree:
    """Where the files of ``kind`` lie, from the marks of its read operation and its reply.

    Args:
        kind: A declared kind.

    Returns:
        The layout of its files.
    """
    read = _described(kind.read)
    hints = get_type_hints(read, include_extras=True)
    reply = next(iter(get_args(hints.get("return"))), None)
    marks = [mark for hint in hints.values() for mark in getattr(hint, "__metadata__", ())]
    placed = isinstance(reply, type) and issubclass(reply, BaseModel) and _marked(reply, Place)
    return Tree(
        service=kind.name.partition("/")[0],
        containers=tuple(
            mark.of.__name__.rpartition(".")[2] for mark in marks if isinstance(mark, Container)
        ),
        resource=None if placed else _resource(read.__module__),
        suffix=kind.layout.suffix,
    )


def _marked(model: type[BaseModel], mark: type) -> bool:
    return any(
        isinstance(held, mark) for info in model.model_fields.values() for held in info.metadata
    )
