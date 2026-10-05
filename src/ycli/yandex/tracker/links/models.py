"""Pydantic models for Tracker issue links (LinkObject + Link + ItemList[Link])."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import (
    APIModel,
    DisplayStr,
    IDStr,
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

    key: str | None = Field(default=None, description="Key of the linked issue.")
    display: str | None = Field(default=None, description="Display name of the linked issue.")


class Link(APIModel):
    """A linked issue reference (``/issues/{key}/links`` item).

    Examples:
        >>> Link.model_validate(
        ...     {"id": 7, "type": {"id": "relates"}, "object": {"key": "DE-2"}}
        ... ).type
        'relates'
    """

    id: int | str | None = Field(default=None, description="Link identifier.")
    type: IDStr = Field(default=None, description="Identifier of the link type, e.g. ``relates``.")
    direction: str | None = Field(
        default=None,
        description="Link direction relative to the requested issue: ``outward`` or ``inward``.",
    )
    object: LinkObject | None = Field(default=None, description="The linked issue.")
    created_by: DisplayStr = Field(
        default=None,
        alias="createdBy",
        description="Display name of the user who created the link.",
    )
    updated_by: DisplayStr = Field(
        default=None,
        alias="updatedBy",
        description="Display name of the user who last changed the linked issue.",
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="When the link was created (ISO 8601)."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="When the link was last changed (ISO 8601)."
    )
    assignee: DisplayStr = Field(
        default=None, description="Display name of the linked issue's assignee."
    )
    status: KeyStr = Field(default=None, description="Key of the linked issue's status.")

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


class ImportLink(RequestBody):
    """Typed body for ``POST /issues/{key}/links/_import`` — import one issue link with history.

    Examples:
        >>> ImportLink(
        ...     relationship="relates",
        ...     issue="TEST-2",
        ...     created_at="2017-08-29T12:34:41.740+0000",
        ...     created_by="11",
        ... ).model_dump(exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
        {'relationship': 'relates', 'issue': 'TEST-2',
         'createdAt': '2017-08-29T12:34:41.740+0000', 'createdBy': '11'}
    """

    relationship: str = Field(
        description="Link type, e.g. ``relates``, ``depends on``, ``subtask``."
    )
    issue: str = Field(description="Key or id of the issue to link to.")
    created_at: str = Field(alias="createdAt", description="Original link creation time.")
    created_by: str = Field(alias="createdBy", description="Login or id of the link creator.")
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Original last-edit time (only together with ``updated_by``).",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="Login or id of the last editor (only together with ``updated_at``).",
    )
