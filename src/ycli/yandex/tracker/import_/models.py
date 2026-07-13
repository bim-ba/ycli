"""Typed request bodies for Tracker data import (``/_import`` endpoints).

Import is admin-only and *preserves history*: every body carries the original ``createdAt`` /
``createdBy`` (and optional ``updatedAt`` / ``updatedBy``) so the imported entity keeps its
source timestamps and authorship rather than being stamped "now". The responses reuse the
canonical entity models (``Issue`` / ``Comment`` / ``Link`` / ``Worklog`` / ``Attachment``).
"""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel  # pydantic resolves field types at runtime


class ImportTask(APIModel):
    """Typed body for ``POST /issues/_import`` — import one issue, preserving its history.

    Example:
        >>> ImportTask(
        ...     queue="TEST",
        ...     summary="Test",
        ...     created_at="2017-08-29T12:34:41.740+0000",
        ...     created_by="11",
        ... ).model_dump(by_alias=True, exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
        {'queue': 'TEST', 'summary': 'Test', 'createdAt': '2017-08-29T12:34:41.740+0000',
         'createdBy': '11'}
    """

    queue: str = Field(description="Key of the queue to import the issue into.")
    summary: str = Field(description="Issue title (max 255 characters).")
    created_at: str = Field(
        alias="createdAt",
        description="Original creation time (``YYYY-MM-DDThh:mm:ss.sss±hhmm``); not in the future.",
    )
    created_by: str = Field(
        alias="createdBy", description="Login or id of the original issue author."
    )
    key: str | None = Field(
        default=None, description="Explicit issue key (must belong to the queue)."
    )
    description: str | None = Field(default=None, description="Issue description (YFM markdown).")
    assignee: str | None = Field(default=None, description="Login or id of the assignee.")
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


class ImportComment(APIModel):
    """Typed body for ``POST /issues/{key}/comments/_import`` — import one comment with history.

    Example:
        >>> ImportComment(
        ...     text="Test", created_at="2017-08-29T12:34:41.740+0000", created_by="11"
        ... ).model_dump(by_alias=True, exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
        {'text': 'Test', 'createdAt': '2017-08-29T12:34:41.740+0000', 'createdBy': '11'}
    """

    text: str = Field(description="Comment text (max 512000 characters).")
    created_at: str = Field(alias="createdAt", description="Original comment creation time.")
    created_by: str = Field(alias="createdBy", description="Login or id of the comment author.")
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


class ImportLink(APIModel):
    """Typed body for ``POST /issues/{key}/links/_import`` — import one issue link with history.

    Example:
        >>> ImportLink(
        ...     relationship="relates",
        ...     issue="TEST-2",
        ...     created_at="2017-08-29T12:34:41.740+0000",
        ...     created_by="11",
        ... ).model_dump(by_alias=True, exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
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


class ImportWorklog(APIModel):
    """Typed body for ``POST /issues/{key}/worklogs/_import`` — import one worklog with history.

    Example:
        >>> ImportWorklog(
        ...     duration="PT1H",
        ...     created_at="2025-02-18T16:35:41.740+0000",
        ...     created_by="username",
        ...     start="2025-02-18T16:35:41.740+0000",
        ... ).model_dump(by_alias=True, exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
        {'duration': 'PT1H', 'createdAt': '2025-02-18T16:35:41.740+0000',
         'createdBy': 'username', 'start': '2025-02-18T16:35:41.740+0000'}
    """

    duration: str = Field(description="Time spent as an ISO-8601 duration, e.g. ``PT1H``.")
    created_at: str = Field(alias="createdAt", description="Original record creation time.")
    created_by: str = Field(alias="createdBy", description="Login or id of the record author.")
    start: str = Field(description="Work start time (``YYYY-MM-DDThh:mm:ss.sss±hhmm``).")
    comment: str | None = Field(default=None, description="Optional note saved in the time report.")
