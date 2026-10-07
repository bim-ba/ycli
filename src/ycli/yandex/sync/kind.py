"""How a resource declares itself a kind of file: one declaration, and marks on its operations."""

import inspect
import sys
from collections.abc import Callable
from dataclasses import dataclass, fields
from functools import partial
from types import NoneType
from typing import Any, Protocol, get_args, get_type_hints

from pydantic import BaseModel, Field

from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.models import APIModel
from ycli.yandex.sync.document import Link
from ycli.yandex.sync.formats import FileFormat
from ycli.yandex.sync.marks import Container, Identity, Version

#: An operation of a resource: a function of its ``endpoints.py`` that describes a request,
#: whole or with the arguments a kind always gives it already set (``functools.partial``).
type Operation = Callable[..., Endpoint[Any] | Paged[Any, Any]]


class Proof(Protocol):
    """One way a write proves the version it worked from, beside the fingerprint of the file."""

    def describe(self) -> str:
        """What ``ycli sync kinds`` says of it."""
        ...


@dataclass(frozen=True)
class SentVersion:
    """The write carries the version (its argument marked :class:`Version`); the server checks."""

    def describe(self) -> str:
        """What ``ycli sync kinds`` says of it.

        Returns:
            One line.
        """
        return "sent with the write: the server refuses a stale one"


@dataclass(frozen=True)
class CheckedVersion:
    """The server takes no version: the newest one is read and compared before a write.

    Args:
        newest: The operation that lists the versions of an object, newest first.
    """

    newest: Operation

    def describe(self) -> str:
        """What ``ycli sync kinds`` says of it.

        Returns:
            One line.
        """
        return "read and compared before the write"


@dataclass(frozen=True)
class NoVersion:
    """The service has no version: the fingerprint of the content alone guards a write."""

    def describe(self) -> str:
        """What ``ycli sync kinds`` says of it.

        Returns:
            One line.
        """
        return "none: the fingerprint of the content alone"


@dataclass(frozen=True)
class Arguments:
    """What the marks of one operation say about its arguments, by name.

    ``left_out`` are the arguments nobody names that may be ``None``: the engine passes
    ``None``, as a field of a body that is not named is not sent. ``undecided`` are those
    nobody names that must have a value: a declaration with one cannot be called.
    """

    identity: tuple[str, ...] = ()
    container: tuple[str, ...] = ()
    version: str | None = None
    body: str | None = None
    left_out: tuple[str, ...] = ()
    undecided: tuple[str, ...] = ()


def arguments_of(operation: Operation) -> Arguments:
    """Read the marks of ``operation``: which argument is what.

    The body is the argument whose type is a model; it needs no mark. An argument that a
    ``partial`` has set, or that has a default, is decided already.

    Args:
        operation: A function of ``endpoints.py``, or a ``partial`` of one.

    Returns:
        The names of its arguments, by what each is.

    Raises:
        TypeError: Two arguments are marked as the version, or two take a model.

    Examples:
        >>> from typing import Annotated
        >>> import ycli.yandex.sync as queues
        >>> def update(
        ...     queue_id: Annotated[str, Container(queues)],
        ...     trigger_id: Annotated[int, Identity()],
        ...     body: Link,
        ...     *,
        ...     version: Annotated[int | None, Version()],
        ...     notify: bool | None,
        ... ): ...
        >>> found = arguments_of(update)
        >>> found.identity, found.container, found.version, found.body, found.left_out
        (('trigger_id',), ('queue_id',), 'version', 'body', ('notify',))
    """
    declared = operation.func if isinstance(operation, partial) else operation
    hints = get_type_hints(declared, include_extras=True)
    marked: dict[type, list[str]] = {Identity: [], Container: [], Version: [], BaseModel: []}
    left_out: list[str] = []
    undecided: list[str] = []
    for name, parameter in inspect.signature(operation).parameters.items():
        hint = hints.get(name)
        marks = [mark for mark in getattr(hint, "__metadata__", ()) if type(mark) in marked]
        for mark in marks:
            marked[type(mark)].append(name)
        if isinstance(hint, type) and issubclass(hint, BaseModel):
            marked[BaseModel].append(name)
        elif not marks and parameter.default is inspect.Parameter.empty:
            (left_out if NoneType in get_args(hint) else undecided).append(name)
    for what in (Version, BaseModel):
        if len(marked[what]) > 1:
            raise TypeError(f"{operation}: more than one {what.__name__} argument")
    return Arguments(
        identity=tuple(marked[Identity]),
        container=tuple(marked[Container]),
        version=next(iter(marked[Version]), None),
        body=next(iter(marked[BaseModel]), None),
        left_out=tuple(left_out),
        undecided=tuple(undecided),
    )


@dataclass(frozen=True)
class Kind[L: Link, C: BaseModel]:
    """One kind of object that becomes one file: what a resource tells the engine about itself.

    The content is the body of the request that changes the object (``content``), so a file
    holds what that request can carry and nothing is written twice. An operation the API does
    not have is ``None``: the engine says so when a file asks for it.

    Args:
        name: What a file of the kind carries under ``ycli``, e.g. ``wiki/page``.
        layout: How its file is laid out.
        link: The keys that tie a file to its object, declared in the kind's own module:
            the first line of that module's docstring is what ``ycli sync kinds`` says of it.
        content: The model of the request that changes the object.
        read: The operation that reads one object.
        find: The operation that lists the objects of a container.
        create: The operation that creates an object.
        update: The operation that changes an object.
        delete: The operation that deletes an object.
        version: How a write proves the version it worked from, beside the fingerprint every
            file carries.
    """

    name: str
    layout: FileFormat
    link: type[L]
    content: type[C]
    read: Operation
    find: Operation | None = None
    create: Operation | None = None
    update: Operation | None = None
    delete: Operation | None = None
    version: Proof = NoVersion()

    def operations(self) -> dict[str, Operation]:
        """The operations the kind has, by the name of the field that holds each.

        Returns:
            ``read`` and whichever of ``find``, ``create``, ``update``, ``delete`` the API has.
        """
        held = {field.name: getattr(self, field.name) for field in fields(self)}
        return {
            name: value
            for name, value in held.items()
            if callable(value) and not isinstance(value, type)
        }


class KindSummary(APIModel):
    """One kind as ``ycli sync kinds`` lists it."""

    name: str = Field(description="What a file of the kind carries under `ycli`.")
    file: str = Field(description="The suffix of its files.")
    operations: list[str] = Field(description="What the API can do with an object of the kind.")
    version: str = Field(description="How a write proves the version it worked from.")
    about: str = Field(description="What the kind is, in the words of its declaration.")


def summary_of(kind: Kind[Any, Any]) -> KindSummary:
    """``kind`` as one row of the listing.

    Args:
        kind: A declared kind.

    Returns:
        Its name, the suffix of its files, the operations it has, what guards a write, and
        the first line of the docstring of the module that declares it.
    """
    declared_in = sys.modules[kind.link.__module__]
    return KindSummary(
        name=kind.name,
        file=kind.layout.suffix,
        operations=[*kind.operations()],
        version=kind.version.describe(),
        about=(declared_in.__doc__ or "").partition("\n")[0],
    )
