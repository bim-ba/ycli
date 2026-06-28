"""Pydantic models for Tracker issue links (LinkObject + Link + LinkList)."""

from __future__ import annotations

from pydantic import RootModel

from ycli.models import APIModel
from ycli.yandex.tracker._models import _IdRef


class LinkObject(APIModel):
    """The ``object`` sub-model in a ``Link`` — carries ``key`` and ``display``.

    Example:
        >>> LinkObject.model_validate({"key": "DE-2", "display": "Other"}).key
        'DE-2'
    """

    key: str | None = None
    display: str | None = None


class Link(APIModel):
    """A linked issue reference (``/issues/{key}/links`` item).

    Example:
        >>> Link.model_validate(
        ...     {"id": 7, "type": {"id": "relates"}, "object": {"key": "DE-2"}}
        ... ).type_id
        'relates'
    """

    id: int | str | None = None
    type: _IdRef | None = None
    direction: str | None = None
    object: LinkObject | None = None

    @property
    def type_id(self) -> str | None:
        """``type.id`` or ``None``."""
        return self.type.id if self.type else None

    @property
    def object_key(self) -> str | None:
        """``object.key`` or ``None``."""
        return self.object.key if self.object else None

    @property
    def object_display(self) -> str | None:
        """``object.display`` or ``None``."""
        return self.object.display if self.object else None


class LinkList(RootModel[list[Link]]):
    """A bare JSON array of links.

    Example:
        >>> LinkList.model_validate([{"direction": "outward"}]).root[0].direction
        'outward'
    """
