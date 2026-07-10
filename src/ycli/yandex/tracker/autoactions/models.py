"""Pydantic models for Tracker queue autoactions (Autoaction + actions + run logs).

An autoaction periodically applies *actions* to every issue matching a *filter* (or a TQL
``query``). Like triggers, its actions are open ``type``-keyed objects, so
:class:`AutoactionAction` pins the shared ``type`` and allows the rest (``extra="allow"``).
The two log endpoints return different shapes: ``/logs`` lists run summaries
(:class:`AutoactionLogEntry`); ``/logs/{run_id}`` lists per-issue outcomes
(:class:`AutoactionRunEntry`).
"""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field, RootModel

from ycli.yandex.models import APIModel


class AutoactionQueueRef(APIModel):
    """The queue an autoaction belongs to (``queue`` object).

    Example:
        >>> AutoactionQueueRef.model_validate({"key": "DESIGN", "display": "Design"}).key
        'DESIGN'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the queue.",
    )
    id: str | None = Field(default=None, description="Identifier of the queue.")
    key: str | None = Field(default=None, description="Key of the queue (e.g. DESIGN).")
    display: str | None = Field(default=None, description="Human-readable name of the queue.")


class AutoactionCalendar(APIModel):
    """The working-calendar window an autoaction is active in (``calendar`` object).

    Example:
        >>> AutoactionCalendar(id=2).id
        2
    """

    id: int = Field(description="Identifier of the working calendar/schedule.")


class AutoactionAction(APIModel):
    """One autoaction action (a ``type``-keyed object; extra keys depend on the type).

    ``type`` is one of Transition, Update, Event.comment-create, Webhook, CalculateFormula, … ;
    the type-specific parameters (``status`` …) ride along as extra fields preserved verbatim.

    Example:
        >>> AutoactionAction.model_validate({"type": "Transition", "status": {"key": "x"}}).type
        'Transition'
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: str = Field(description="Action type discriminator (e.g. Transition, Update, Webhook).")


class Autoaction(APIModel):
    """A queue autoaction (``GET /queues/{id}/autoactions/{action_id}``).

    Example:
        >>> Autoaction.model_validate({"id": 9, "name": "auto", "active": True}).name
        'auto'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns the autoaction's parameters.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the autoaction.")
    queue: AutoactionQueueRef | None = Field(
        default=None, description="Queue the autoaction is configured in."
    )
    name: str | None = Field(default=None, description="Human-readable name of the autoaction.")
    version: int | None = Field(
        default=None, description="Autoaction version; incremented on every change."
    )
    active: bool | None = Field(
        default=None, description="Whether the autoaction is active (true) or disabled (false)."
    )
    created: str | None = Field(
        default=None, description="Creation timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm)."
    )
    updated: str | None = Field(
        default=None, description="Last-change timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm)."
    )
    filter: Any = Field(
        default=None, description="Field-based filter selecting the issues the autoaction runs on."
    )
    query: str | None = Field(
        default=None, description="TQL query selecting the issues the autoaction runs on."
    )
    actions: list[AutoactionAction] = Field(
        default_factory=list, description="Actions applied to each matching issue."
    )
    enable_notifications: bool | None = Field(
        default=None,
        alias="enableNotifications",
        description="Whether notifications are sent when the autoaction runs.",
    )
    last_launch: str | None = Field(
        default=None,
        alias="lastLaunch",
        description="Timestamp of the autoaction's last run (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    total_issues_processed: int | None = Field(
        default=None,
        alias="totalIssuesProcessed",
        description="Number of issues checked on the autoaction's last run.",
    )
    interval_millis: int | None = Field(
        default=None,
        alias="intervalMillis",
        description="Run interval in milliseconds (default 3600000 — once an hour).",
    )
    calendar: AutoactionCalendar | None = Field(
        default=None, description="Working-calendar window the autoaction is active in."
    )


class AutoactionCreate(APIModel):
    """Typed request body for ``autoactions.create`` (``POST /queues/{id}/autoactions``).

    Supply at least one of ``filter`` or ``query`` to select the issues to act on.

    Example:
        >>> AutoactionCreate(
        ...     name="A", actions=[AutoactionAction(type="Transition")], query="Status: Open"
        ... ).name
        'A'
    """

    name: str = Field(description="Name of the new autoaction.")
    filter: dict[str, Any] | None = Field(
        default=None, description="Field-based filter selecting the issues to act on."
    )
    query: str | None = Field(default=None, description="TQL query selecting the issues to act on.")
    actions: list[AutoactionAction] = Field(description="Actions applied to each matching issue.")
    active: bool | None = Field(
        default=None, description="Whether the autoaction starts active (true) or disabled (false)."
    )
    enable_notifications: bool | None = Field(
        default=None,
        serialization_alias="enableNotifications",
        description="Whether notifications are sent when the autoaction runs.",
    )
    interval_millis: int | None = Field(
        default=None,
        serialization_alias="intervalMillis",
        description="Run interval in milliseconds (default 3600000 — once an hour).",
    )
    calendar: AutoactionCalendar | None = Field(
        default=None, description="Working-calendar window the autoaction is active in."
    )


class AutoactionLogEntry(APIModel):
    """One run-summary record from ``.../autoactions/{id}/logs``.

    Example:
        >>> AutoactionLogEntry.model_validate({"id": "x", "searchHits": 3}).search_hits
        3
    """

    id: str | None = Field(default=None, description="Identifier of the autoaction run.")
    launch_time: str | None = Field(
        default=None,
        alias="launchTime",
        description="When the run started (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    search_hits: int | None = Field(
        default=None, alias="searchHits", description="Number of issues the run processed."
    )
    successes: int | None = Field(
        default=None, description="Number of issues the autoaction fired on."
    )
    failures: int | None = Field(
        default=None, description="Number of issues the autoaction failed on."
    )
    search_failed: bool | None = Field(
        default=None,
        alias="searchFailed",
        description="True when no issue was processed at all in the run.",
    )


class AutoactionLogList(RootModel[list[AutoactionLogEntry]]):
    """A bare JSON array of autoaction run summaries (``.../autoactions/{id}/logs``).

    Example:
        >>> AutoactionLogList.model_validate([{"id": "x"}]).root[0].id
        'x'
    """


class AutoactionIssueRef(APIModel):
    """The issue an autoaction run touched (``issueReference`` object).

    Example:
        >>> AutoactionIssueRef.model_validate({"key": "TEST-1"}).key
        'TEST-1'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the issue.",
    )
    id: str | None = Field(default=None, description="Identifier of the issue.")
    version: int | None = Field(default=None, description="Version of the issue.")
    key: str | None = Field(default=None, description="Key of the issue (e.g. TEST-1).")
    display: Any = Field(default=None, description="Human-readable name of the issue.")


class AutoactionRunStatus(APIModel):
    """The per-issue outcome of an autoaction run (``status`` object).

    Example:
        >>> AutoactionRunStatus.model_validate({"value": "success"}).value
        'success'
    """

    value: str | None = Field(default=None, description="Outcome value (e.g. success).")
    display: Any = Field(default=None, description="Human-readable outcome name.")


class AutoactionRunEntry(APIModel):
    """One per-issue outcome from ``.../autoactions/{id}/logs/{run_id}``.

    Example:
        >>> AutoactionRunEntry.model_validate(
        ...     {"id": 0, "issueReference": {"key": "TEST-1"}, "status": {"value": "success"}}
        ... ).issue_reference.key
        'TEST-1'
    """

    id: int | None = Field(
        default=None, description="Zero-based sequence number of the issue within the run."
    )
    issue_reference: AutoactionIssueRef | None = Field(
        default=None, alias="issueReference", description="The issue this outcome is for."
    )
    status: AutoactionRunStatus | None = Field(
        default=None, description="Outcome of the autoaction on this issue."
    )


class AutoactionRunList(RootModel[list[AutoactionRunEntry]]):
    """A bare JSON array of per-issue run outcomes (``.../autoactions/{id}/logs/{run_id}``).

    Example:
        >>> AutoactionRunList.model_validate([{"id": 0}]).root[0].id
        0
    """
