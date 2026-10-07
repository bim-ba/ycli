"""The marks a resource puts on its operations and models for the file engine.

Kept apart from the engine itself, so an ``endpoints.py`` or a ``models.py`` imports a mark
and nothing that reads or writes a file.
"""

from dataclasses import dataclass
from types import ModuleType


@dataclass(frozen=True)
class Identity:
    """Marks the argument of an operation that says which object it is.

    ``trigger_id: Annotated[int, Identity()]``. An object addressed by several arguments has
    several; one that is the only one of its container has none.
    """


@dataclass(frozen=True)
class Container:
    """Marks the argument of an operation that says where the object lies.

    ``queue_id: Annotated[str, Container(queues)]``: the queue of a trigger, where ``queues`` is
    the package of the resource that holds it (``from ycli.yandex.tracker import queues``). The
    resource is named by the object, so a path such as ``tracker/queues/DE/triggers/16.yaml``
    takes ``queues`` from it and nothing is spelled twice.

    Args:
        of: The package of the resource the argument identifies.
    """

    of: ModuleType


@dataclass(frozen=True)
class Version:
    """Marks the argument of a write that carries the version the write worked from.

    ``version: Annotated[int | None, Version()] = None``: the server refuses a stale one.
    """


@dataclass(frozen=True)
class Place:
    """Marks the field that says where the file of an object lies, under its service.

    ``slug: Annotated[str, Place()]``: the page ``team/onboarding`` is the file
    ``wiki/team/onboarding.md``. A kind with no such field lies under its container and its
    identity.
    """
