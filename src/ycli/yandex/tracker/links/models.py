"""Pydantic models for Tracker issue links (LinkObject + Link + LinkList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    IdStr,
)


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
        ... ).type
        'relates'
    """

    id: int | str | None = None
    type: IdStr = None
    direction: str | None = None
    object: LinkObject | None = None

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


class LinkCreate(APIModel):
    """Typed request body for ``POST /issues/{key}/links`` (link to another issue).

    Example:
        >>> LinkCreate(relationship="relates", issue="DE-2").model_dump(exclude_none=True)
        {'relationship': 'relates', 'issue': 'DE-2'}
    """

    relationship: str = Field(
        description="Link type from linktypes_list, e.g. relates, depends on, is subtask for."
    )
    issue: str = Field(description="Key of the issue to link to.")
