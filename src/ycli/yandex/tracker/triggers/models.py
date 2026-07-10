"""Pydantic models for Tracker queue triggers (Trigger + polymorphic actions/conditions).

A trigger fires configured *actions* on an issue when its *conditions* match. Both actions
and conditions are open polymorphic objects keyed by a ``type`` discriminator (see the vendored
``triggers/actions.md`` and ``triggers/conditions.md`` catalogues): rather than enumerate every
one of the ~40 shapes, :class:`TriggerAction`/:class:`TriggerCondition` pin the shared ``type``
field and allow the rest (``extra="allow"``) so any documented shape round-trips unchanged.
"""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field, RootModel

from ycli.yandex.models import APIModel


class TriggerQueueRef(APIModel):
    """The queue a trigger belongs to (``queue`` object).

    Example:
        >>> TriggerQueueRef.model_validate({"key": "DESIGN", "display": "Design"}).key
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


class TriggerAction(APIModel):
    """One trigger action (a ``type``-keyed object; extra keys depend on the type).

    ``type`` is one of Transition, Update, Move, CreateComment, CreateChecklist, Webhook,
    CalculateFormula, CreateIssue, … ; the type-specific parameters (``status``, ``queue``,
    ``text``, ``endpoint`` …) ride along as extra fields preserved verbatim.

    Example:
        >>> TriggerAction.model_validate({"type": "Transition", "status": {"key": "open"}}).type
        'Transition'
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: str = Field(description="Action type discriminator (e.g. Transition, Update, Webhook).")


class TriggerCondition(APIModel):
    """One trigger condition, or an And/Or group of nested conditions.

    For an elementary condition ``type`` is a match rule (e.g. CommentFullyMatchCondition,
    FieldEquals) and the rule's parameters ride along as extra fields. For a group, ``type`` is
    ``Or``/``And`` and ``conditions`` holds the nested sub-conditions.

    Example:
        >>> TriggerCondition.model_validate(
        ...     {"type": "Or", "conditions": [{"type": "Event.comment-create"}]}
        ... ).conditions[0].type
        'Event.comment-create'
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: str = Field(description="Condition type, or the And/Or operator for a group.")
    conditions: list[TriggerCondition] | None = Field(
        default=None, description="Nested sub-conditions when this is an And/Or group."
    )


class Trigger(APIModel):
    """A queue trigger (``GET /queues/{id}/triggers/{trigger_id}``).

    Example:
        >>> Trigger.model_validate({"id": 16, "name": "trigger", "active": True}).name
        'trigger'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns the trigger's parameters.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the trigger.")
    queue: TriggerQueueRef | None = Field(
        default=None, description="Queue the trigger is configured in."
    )
    name: str | None = Field(default=None, description="Human-readable name of the trigger.")
    order: str | None = Field(
        default=None, description="Display weight controlling the trigger's order in the UI."
    )
    actions: list[TriggerAction] = Field(
        default_factory=list, description="Actions the trigger performs when it fires."
    )
    conditions: list[TriggerCondition] = Field(
        default_factory=list, description="Conditions under which the trigger fires."
    )
    version: int | None = Field(
        default=None, description="Trigger version; incremented on every change."
    )
    active: bool | None = Field(
        default=None, description="Whether the trigger is active (true) or disabled (false)."
    )


class TriggerCreate(APIModel):
    """Typed request body for ``triggers.create`` (``POST /queues/{id}/triggers``).

    Example:
        >>> TriggerCreate(name="TriggerName", actions=[TriggerAction(type="Transition")]).name
        'TriggerName'
    """

    name: str = Field(description="Name of the new trigger.")
    actions: list[TriggerAction] = Field(description="Actions the trigger performs when it fires.")
    conditions: list[TriggerCondition] | None = Field(
        default=None, description="Conditions under which the trigger fires (default: always)."
    )
    active: bool | None = Field(
        default=None, description="Whether the trigger starts active (true) or disabled (false)."
    )


class TriggerUpdate(APIModel):
    """Typed request body for ``triggers.edit`` (``PATCH /queues/{id}/triggers/{trigger_id}``).

    Every field is optional; only the fields you set are sent.

    Example:
        >>> TriggerUpdate(active=False).active
        False
    """

    name: str | None = Field(default=None, description="New name of the trigger.")
    actions: list[TriggerAction] | None = Field(
        default=None, description="Replacement actions the trigger performs."
    )
    conditions: list[TriggerCondition] | None = Field(
        default=None, description="Replacement conditions under which the trigger fires."
    )
    active: bool | None = Field(
        default=None, description="Whether the trigger is active (true) or disabled (false)."
    )
    before: int | None = Field(
        default=None, description="Id of the trigger to place this one before (reordering)."
    )


class WebhookLogEntry(APIModel):
    """One webhook-execution log record of a trigger's HTTP-request action.

    Example:
        >>> WebhookLogEntry.model_validate({"id": "x", "duration": 235}).duration
        235
    """

    id: str | None = Field(default=None, description="Identifier of the trigger run.")
    start_time: str | None = Field(
        default=None,
        alias="startTime",
        description="When the trigger run started (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    end_time: str | None = Field(
        default=None,
        alias="endTime",
        description="When the trigger run finished (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    duration: int | None = Field(
        default=None, description="Duration of the trigger run in milliseconds."
    )
    trigger_id: int | None = Field(
        default=None, alias="triggerId", description="Identifier of the trigger that ran."
    )
    action_id: int | None = Field(
        default=None, alias="actionId", description="Identifier of the action inside the trigger."
    )
    issue_id: str | None = Field(
        default=None, alias="issueId", description="Identifier of the issue the trigger ran on."
    )
    request: Any = Field(
        default=None, description="The outbound HTTP request (method, endpoint, headers, body)."
    )
    response: Any = Field(
        default=None, description="The received HTTP response (headers, statusCode)."
    )


class WebhookLogList(RootModel[list[WebhookLogEntry]]):
    """A bare JSON array of webhook log records (``.../triggers/{id}/webhooks/log``).

    Example:
        >>> WebhookLogList.model_validate([{"id": "x", "duration": 1}]).root[0].duration
        1
    """
