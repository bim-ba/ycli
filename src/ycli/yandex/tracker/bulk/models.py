"""Pydantic models for Tracker bulk-change operations (``/bulkchange``).

A bulk change is an *async* operation: the trigger call (update/move/transition) returns a
:class:`BulkChange` with an ``id`` and an initial ``status`` (``CREATED``); you then re-read
``GET /bulkchange/{id}`` until the status reaches a terminal value (``COMPLETE`` / ``FAILED``).
The ``--wait`` CLI path drives that poll via :func:`ycli.yandex.polling.poll`, using
:attr:`BulkChange.is_terminal` as the stop predicate.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
    KeyStr,
)

#: Statuses at which a bulk-change operation has stopped running (poll terminates here).
TERMINAL_STATUSES = frozenset({"COMPLETE", "FAILED"})


class BulkChange(APIModel):
    """A bulk-change operation's status (returned by the trigger and by ``GET /bulkchange/{id}``).

    ``status`` starts at ``CREATED`` and progresses to a terminal ``COMPLETE`` / ``FAILED``;
    :attr:`is_terminal` reports whether it has stopped, driving the ``--wait`` poll loop.

    Example:
        >>> BulkChange.model_validate({"id": "1ab", "status": "COMPLETE"}).is_terminal
        True
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource address of this bulk-change operation.",
    )
    id: str | None = Field(default=None, description="Identifier of the bulk-change operation.")
    created_by: DisplayStr = Field(
        default=None,
        alias="createdBy",
        description="Display name of the user who started the operation.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Creation timestamp (``YYYY-MM-DDThh:mm:ss.sss±hhmm``).",
    )
    status: str | None = Field(
        default=None, description="Operation status, e.g. ``CREATED``, ``COMPLETE``, ``FAILED``."
    )
    status_text: str | None = Field(
        default=None, alias="statusText", description="Human-readable description of the status."
    )
    execution_chunk_percent: float | None = Field(
        default=None,
        alias="executionChunkPercent",
        description="Service parameter (chunk progress %).",
    )
    execution_issue_percent: float | None = Field(
        default=None,
        alias="executionIssuePercent",
        description="Service parameter (issue progress %).",
    )
    total_issues: int | None = Field(
        default=None,
        alias="totalIssues",
        description="Number of issues the operation should change.",
    )
    total_completed_issues: int | None = Field(
        default=None,
        alias="totalCompletedIssues",
        description="Number of issues the operation has finished successfully.",
    )

    @property
    def is_terminal(self) -> bool:
        """``True`` once ``status`` reached a terminal value (see :data:`TERMINAL_STATUSES`)."""
        return self.status in TERMINAL_STATUSES


class BulkError(APIModel):
    """The ``error`` block on a failed bulk-change issue result.

    Example:
        >>> BulkError.model_validate({"errors": {"resolution": "bad"}, "errorMessages": []}).errors
        {'resolution': 'bad'}
    """

    errors: dict[str, Any] | None = Field(
        default=None, description="Per-field error descriptions keyed by field name."
    )
    error_messages: list[str] = Field(
        default_factory=list,
        alias="errorMessages",
        description="Service parameter (extra messages).",
    )


class BulkIssueResult(APIModel):
    """One issue's outcome in ``GET /bulkchange/{id}/issues`` (issues that failed to change).

    Example:
        >>> BulkIssueResult.model_validate({"issue": {"key": "TEST-1"}, "status": "FAILED"}).issue
        'TEST-1'
    """

    issue: KeyStr = Field(default=None, description="Key of the affected issue.")
    status: str | None = Field(
        default=None, description="Outcome status for this issue, e.g. ``FAILED``."
    )
    status_text: str | None = Field(
        default=None, alias="statusText", description="Human-readable description of the outcome."
    )
    error: BulkError | None = Field(
        default=None, description="Details of the errors that occurred on this issue."
    )


class BulkIssueResultList(RootModel[list[BulkIssueResult]]):
    """A bare JSON array of per-issue bulk-change results.

    Example:
        >>> BulkIssueResultList.model_validate([{"status": "FAILED"}]).root[0].status
        'FAILED'
    """


class BulkUpdate(APIModel):
    """Typed request body for ``POST /bulkchange/_update`` (mass-edit issues).

    Example:
        >>> BulkUpdate(issues=["TEST-1"], values={"priority": {"key": "blocker"}}).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'issues': ['TEST-1'], 'values': {'priority': {'key': 'blocker'}}}
    """

    issues: list[str] | str = Field(
        description="Array of issue keys, or a query-language filter string selecting the issues."
    )
    values: dict[str, Any] = Field(
        description="Field values to apply (any editable issue field; supports set/add/remove ops)."
    )
    notify: bool | None = Field(
        default=None, description="Notify users referenced in the issues (default false)."
    )


class BulkMove(APIModel):
    """Typed request body for ``POST /bulkchange/_move`` (mass-move issues to another queue).

    Example:
        >>> BulkMove(queue="CHECK", issues=["TEST-1"]).model_dump(by_alias=True, exclude_none=True)
        {'queue': 'CHECK', 'issues': ['TEST-1']}
    """

    queue: str = Field(description="Key of the target queue to move the issues into.")
    issues: list[str] | str = Field(
        description="Array of issue keys, or a query-language filter string selecting the issues."
    )
    values: dict[str, Any] | None = Field(
        default=None, description="Optional field values to apply during the move."
    )
    move_all_fields: bool | None = Field(
        default=None,
        alias="moveAllFields",
        description="Carry versions/components/projects to the new queue if they exist there.",
    )
    initial_status: bool | None = Field(
        default=None,
        alias="initialStatus",
        description="Reset each issue's status to the workflow's initial status (default false).",
    )
    notify: bool | None = Field(
        default=None, description="Notify users referenced in the issues (default false)."
    )


class BulkTransition(APIModel):
    """Typed request body for ``POST /bulkchange/_transition`` (mass status transition).

    Example:
        >>> BulkTransition(transition="close", issues=["TEST-1"]).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'transition': 'close', 'issues': ['TEST-1']}
    """

    transition: str = Field(description="Identifier of the transition to apply, e.g. ``close``.")
    issues: list[str] | str = Field(
        description="Array of issue keys, or a query-language filter string selecting the issues."
    )
    values: dict[str, Any] | None = Field(
        default=None,
        description="Optional field values set during the transition (e.g. a resolution).",
    )
    notify: bool | None = Field(
        default=None, description="Notify users referenced in the issues (default false)."
    )
