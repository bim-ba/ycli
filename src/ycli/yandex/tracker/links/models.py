"""Pydantic models for Tracker issue links (LinkObject + Link + ItemList[Link])."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import (
    APIModel,
    DisplayStr,
    IdStr,
    KeyStr,
    RequestBody,  # pydantic resolves field types via get_type_hints() at runtime
)

#: The link verbs ``POST /issues/{key}/links`` documents.
Relationship = (
    Literal[
        "depends on",
        "is dependent by",
        "relates",
        "duplicates",
        "is duplicated by",
        "subtask",
        "parent",
    ]
    | str
)


class LinkObject(APIModel):
    """The ``object`` sub-model in a ``Link`` — carries ``key`` and ``display``.

    Examples:
        >>> LinkObject.model_validate({"key": "DE-2", "display": "Other"}).key
        'DE-2'
    """

    key: str | None = None
    display: str | None = None


class Link(APIModel):
    """A linked issue reference (``/issues/{key}/links`` item).

    Examples:
        >>> Link.model_validate(
        ...     {"id": 7, "type": {"id": "relates"}, "object": {"key": "DE-2"}}
        ... ).type
        'relates'
    """

    id: int | str | None = None
    type: IdStr = None
    direction: str | None = None
    object: LinkObject | None = None
    created_by: DisplayStr = Field(default=None, alias="createdBy")
    updated_by: DisplayStr = Field(default=None, alias="updatedBy")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    assignee: DisplayStr = None
    status: KeyStr = None

    @property
    def object_key(self) -> str | None:
        """``object.key`` or ``None``."""
        return self.object.key if self.object else None

    @property
    def object_display(self) -> str | None:
        """``object.display`` or ``None``."""
        return self.object.display if self.object else None


class LinkPage(APIModel):
    """One page of ``POST /issues/{key}/links/_list``: the links under a ``links`` key.

    Examples:
        >>> LinkPage.model_validate({"links": [{"id": 1}]}).links[0].id
        1
    """

    links: list[Link] = Field(default_factory=list, description="The page's links.")


class LinkCreate(RequestBody):
    """Typed request body for ``POST /issues/{key}/links`` (link to another issue).

    Examples:
        >>> LinkCreate(relationship="relates", issue="DE-2").model_dump(exclude_none=True)
        {'relationship': 'relates', 'issue': 'DE-2'}
    """

    relationship: str = Field(
        description="Link type from linktypes_list, e.g. relates, depends on, is subtask for."
    )
    issue: str = Field(description="Key of the issue to link to.")
