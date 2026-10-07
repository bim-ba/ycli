"""One file of a repository as the object it stands for: its link and its content."""

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_core import to_jsonable_python

from ycli.yandex.models import WIRE, APIModel

#: The key of a file that names its kind.
KIND_KEY = "ycli"


@dataclass(frozen=True)
class Body:
    """Marks the field of a content model that is the text under a Markdown header.

    ``content: Annotated[str | None, Body()] = None``: the field is not a key of the header,
    it is everything below it.
    """


class UnreadableFile(Exception):  # noqa: N818  # named for what it is, as the API's errors are
    """A file that is not a file of a kind: where it stops being one, and why.

    Args:
        path: The file.
        line: The line the reason points at, counted from one.
        reason: What is wrong, without the value that was there.

    Examples:
        >>> from pathlib import PurePosixPath
        >>> print(UnreadableFile(PurePosixPath("wiki/team.md"), 3, "no closing `---`"))
        wiki/team.md:3: no closing `---`
    """

    def __init__(self, path: PurePosixPath, line: int, reason: str) -> None:
        super().__init__(f"{path}:{line}: {reason}")
        self.path = path
        self.line = line
        self.reason = reason


@dataclass(frozen=True)
class Parts:
    """A file taken apart, before any model reads it.

    ``kind`` is what its ``ycli`` key names, ``keys`` its other keys in the order written,
    ``text`` what lies under a Markdown header (``None`` for a file that has no such place).
    ``lines`` says on which line each key stands, for an error that points at it.
    """

    path: PurePosixPath
    kind: str
    keys: Mapping[str, Any]
    text: str | None = None
    lines: Mapping[str, int] = field(default_factory=dict, compare=False)


class Link(APIModel):
    """What ties a file to its object, written by ycli and not edited by hand.

    ``hash`` is the fingerprint of the content as it was read from the server
    (:func:`fingerprint`); a file written by hand for an object that does not exist yet has
    none. A kind's own link adds what identifies its object and, where the service has one, the
    version it was read at, each under the key the service calls it by.

    Examples:
        >>> class PageLink(Link):
        ...     id: int | None = None
        ...     revision: int | None = None
        >>> PageLink(id=4821, revision=9917, hash="9f2c").revision
        9917
    """

    model_config = ConfigDict(frozen=True)

    hash: str | None = Field(
        default=None, description="Fingerprint of the content as read from the server."
    )


class Document[L: Link, C: BaseModel](APIModel):
    """One file, read: where it lies, its link, and its content as the kind's own model."""

    model_config = ConfigDict(frozen=True)

    path: PurePosixPath = Field(description="Where the file lies in the repository.")
    link: L = Field(description="What ties the file to its object.")
    content: C = Field(description="What a person edits and a push sends.")


def fields_marked(model: type[BaseModel], mark: type) -> list[str]:
    """The fields of ``model`` that carry a mark of the type ``mark``, in the order declared.

    Args:
        model: A model whose fields may be marked in ``Annotated``.
        mark: The class of the mark.

    Returns:
        The names of the marked fields.

    Examples:
        >>> from typing import Annotated
        >>> class Page(BaseModel):
        ...     title: str
        ...     content: Annotated[str | None, Body()] = None
        >>> fields_marked(Page, Body)
        ['content']
    """
    return [
        name
        for name, info in model.model_fields.items()
        if any(isinstance(held, mark) for held in info.metadata)
    ]


def body_field(content: type[BaseModel]) -> str | None:
    """The name of the field of ``content`` marked :class:`Body`, if it has one.

    Args:
        content: A kind's content model.

    Returns:
        The field's name; ``None`` for a model with no such field.

    Raises:
        TypeError: The model marks more than one field.

    Examples:
        >>> from typing import Annotated
        >>> class Page(BaseModel):
        ...     title: str
        ...     content: Annotated[str | None, Body()] = None
        >>> body_field(Page)
        'content'
        >>> body_field(Link) is None
        True
    """
    marked = fields_marked(content, Body)
    if len(marked) > 1:
        raise TypeError(f"{content.__name__} marks more than one field as its body: {marked}")
    return marked[0] if marked else None


def as_sent(content: BaseModel) -> dict[str, Any]:
    """``content`` as the body of a request carries it: the one form a file and a fingerprint use.

    A file is the body of the request that changes its object, so it is dumped the way a body
    is (``WIRE``): under the API's names, without what a request leaves out, and with a
    ``null`` the API requires (``NoDropNull``) kept.

    Args:
        content: The content of a document.

    Returns:
        Its keys and values, ready for JSON.

    Examples:
        >>> from typing import Annotated
        >>> from ycli.yandex.models import NoDropNull, RequestBody
        >>> class Settings(RequestBody):
        ...     interval: Annotated[int | None, NoDropNull()] = None
        ...     title: str | None = None
        >>> as_sent(Settings())
        {'interval': None}
    """
    return to_jsonable_python(content, context=WIRE)


def fingerprint(content: BaseModel) -> str:
    """The fingerprint of ``content``: the same for the same values, whatever their order.

    It is taken from the content as a request would send it (:func:`as_sent`), so two files
    that differ in layout only have one fingerprint, and what a request leaves out does not
    count.

    Args:
        content: The content of a document.

    Returns:
        Its SHA-256, as 64 hexadecimal digits.

    Examples:
        >>> from ycli.yandex.models import RequestBody
        >>> class Trigger(RequestBody):
        ...     name: str
        ...     active: bool | None = None
        >>> fingerprint(Trigger(name="Assign")) == fingerprint(Trigger(active=None, name="Assign"))
        True
        >>> fingerprint(Trigger(name="Assign")) == fingerprint(Trigger(name="Assign", active=True))
        False
    """
    canonical = json.dumps(
        as_sent(content), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def document_of[L: Link, C: BaseModel](
    parts: Parts, *, link: type[L], content: type[C]
) -> Document[L, C]:
    """``parts`` as a document of one kind: its link keys go to ``link``, the rest to ``content``.

    Args:
        parts: The file, taken apart by its format.
        link: The kind's link model.
        content: The kind's content model.

    Returns:
        The document.

    Raises:
        UnreadableFile: A key does not fit its model; the line is the key's.
    """
    held = {info.alias or name for name, info in link.model_fields.items()}
    told = {key: value for key, value in parts.keys.items() if key in held}
    rest = {key: value for key, value in parts.keys.items() if key not in held}
    body = body_field(content)
    if body is not None:
        rest[content.model_fields[body].alias or body] = parts.text
    elif parts.text:
        raise UnreadableFile(parts.path, 1, f"a {parts.kind} file keeps no text under its header")
    try:
        read = Document(
            path=parts.path, link=link.model_validate(told), content=content.model_validate(rest)
        )
    except ValidationError as error:
        first = error.errors(include_input=False)[0]
        key = str(first["loc"][0]) if first["loc"] else ""
        where = f"{'.'.join(map(str, first['loc']))}: " if first["loc"] else ""
        raise UnreadableFile(parts.path, parts.lines.get(key, 1), where + first["msg"]) from None
    return read


def parts_of(document: Document[Any, Any], *, kind: str) -> Parts:
    """``document`` as the parts of its file: the link keys first, then the content in its order.

    Args:
        document: The document to write.
        kind: The name of its kind, written under ``ycli``.

    Returns:
        The parts a format writes.
    """
    keys = document.link.model_dump(mode="json", by_alias=True, exclude_none=True)
    values = as_sent(document.content)
    body = body_field(type(document.content))
    if body is None:
        return Parts(document.path, kind, {**keys, **values})
    text = values.pop(type(document.content).model_fields[body].alias or body, "")
    return Parts(document.path, kind, {**keys, **values}, text)
