"""Pydantic models for Tracker ``/workflows``: what the API returns and what a write sends.

A workflow is a graph: each *step* is a status with the *actions* (transitions) that leave it,
and the *initial action* sets the status a new issue starts in. Replies spell the structure out
(statuses as objects, names as plain strings); requests take a status as a key, an id or a
``{"key": …}`` object and names as ``{"ru": …, "en": …}`` objects, so reading and writing use
separate models.

Request models read both the API's field name (``initialAction``) and the snake_case one and
write the API's, so the JSON of the docs can be passed to the CLI as is while Python code uses
snake_case.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import AfterValidator, AliasChoices, Field, RootModel

from ycli.yandex.models import APIModel
from ycli.yandex.tracker.models import KeyedReference, LocalizedName, UserReference


class WorkflowTransition(APIModel):
    """An action of a step (or the initial action): its id, name and the status it leads to.

    Examples:
        >>> WorkflowTransition.model_validate(
        ...     {"id": "close", "target": {"key": "closed"}}
        ... ).target.key
        'closed'
    """

    id: str | None = Field(default=None, description="Identifier of the action within its step.")
    name: str | None = Field(default=None, description="Display name of the action.")
    target: KeyedReference | None = Field(
        default=None, description="The status the action moves the issue to."
    )


class WorkflowStep(APIModel):
    """A step of a workflow: a status and the actions available from it.

    Examples:
        >>> WorkflowStep.model_validate({"status": {"key": "open"}, "actions": []}).status.key
        'open'
    """

    status: KeyedReference | None = Field(default=None, description="The status of the step.")
    actions: list[WorkflowTransition] = Field(
        default_factory=list, description="Actions (transitions) available from this status."
    )


class Workflow(APIModel):
    """A Tracker workflow (``GET /workflows/{id}``). Unfilled optional fields are absent.

    Examples:
        >>> Workflow.model_validate({"id": "W21", "name": "Design", "version": 1}).name
        'Design'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the workflow."
    )
    id: str | None = Field(default=None, description="Identifier of the workflow.")
    name: str | None = Field(default=None, description="Name of the workflow.")
    version: int | None = Field(
        default=None, description="Version of the workflow; each change increments it."
    )
    steps: list[WorkflowStep] = Field(
        default_factory=list, description="Steps: each status with the actions leaving it."
    )
    initial_action: WorkflowTransition | None = Field(
        default=None,
        alias="initialAction",
        description="The action that sets the status a new issue starts in.",
    )
    queue: KeyedReference | None = Field(
        default=None, description="The queue the workflow is bound to; absent for a shared one."
    )
    created: str | None = Field(default=None, description="Creation time (ISO 8601).")
    updated: str | None = Field(default=None, description="Last change time (ISO 8601).")
    created_by: UserReference | None = Field(
        default=None, alias="createdBy", description="The workflow's author."
    )
    updated_by: UserReference | None = Field(
        default=None, alias="updatedBy", description="The user who changed the workflow last."
    )
    deleted: bool | None = Field(default=None, description="Whether the workflow is deleted.")
    type: str | None = Field(
        default=None,
        description="Workflow type; ``visual`` today, and absent on older workflows.",
    )


class QueueWorkflows(RootModel[dict[str, list[KeyedReference]]]):
    """The workflows of a queue: workflow id → the issue types that use it.

    Examples:
        >>> QueueWorkflows.model_validate({"dev": [{"key": "task"}]}).root["dev"][0].key
        'task'
    """


class RefSelector(APIModel):
    """A status or queue named by an object; give one of ``key``, ``id`` or ``name``.

    Examples:
        >>> RefSelector(key="open").model_dump(exclude_none=True)
        {'key': 'open'}
    """

    key: str | None = Field(default=None, description="Key of the status or queue.")
    id: int | None = Field(default=None, description="Numeric id of the status or queue.")
    name: str | None = Field(default=None, description="Display name of the status or queue.")


def _needs_russian(name: LocalizedName | None) -> LocalizedName | None:
    """Tracker refuses an action name without its Russian text (422 "action.name: required").

    Args:
        name: The localized name, if any.

    Returns:
        ``name``, unchanged.

    Raises:
        ValueError: ``name`` has an English text but no Russian one.

    Examples:
        >>> _needs_russian(LocalizedName(en="Close"))
        Traceback (most recent call last):
        ...
        ValueError: an action name needs its Russian text (ru): Tracker refuses it otherwise
    """
    if name is not None and name.en and not name.ru:
        raise ValueError("an action name needs its Russian text (ru): Tracker refuses it otherwise")
    return name


class WorkflowActionInput(APIModel):
    """An action in a request: ``name`` and ``target`` are required.

    Examples:
        >>> WorkflowActionInput(
        ...     id="close", name=LocalizedName(ru="Закрыть", en="Close"), target="closed"
        ... ).model_dump(exclude_none=True)
        {'id': 'close', 'name': {'ru': 'Закрыть', 'en': 'Close'}, 'target': 'closed'}
    """

    id: str | None = Field(default=None, description="Identifier of the action within its step.")
    name: Annotated[LocalizedName, AfterValidator(_needs_russian)] = Field(
        description="Name of the action in each language; the Russian text is required."
    )
    description: LocalizedName | None = Field(
        default=None, description="Description of the action in each language."
    )
    target: str | int | RefSelector = Field(
        description="Status the action leads to: a key, a numeric id or a ``{key|id|name}`` object."
    )
    screen: dict[str, Any] | None = Field(
        default=None, description="Transition screen: the fields to fill in when running it."
    )
    conditions: list[dict[str, Any]] | None = Field(
        default=None, description="Conditions under which the action can run."
    )
    functions: list[dict[str, Any]] | None = Field(
        default=None, description="Functions run when the action is executed."
    )


class WorkflowActionUpdate(APIModel):
    """Typed request body for ``workflows.edit_action``.

    The docs mark every field optional, but Tracker refuses an edit without ``name`` and
    ``target`` (422), so both are required; the other fields change only when set.

    Examples:
        >>> WorkflowActionUpdate(name=LocalizedName(ru="Закрыть"), target="closed").model_dump(
        ...     exclude_none=True
        ... )
        {'name': {'ru': 'Закрыть'}, 'target': 'closed'}
    """

    id: str | None = Field(default=None, description="New identifier of the action.")
    name: Annotated[LocalizedName, AfterValidator(_needs_russian)] = Field(
        description="Name of the action (required by Tracker, with its Russian text)."
    )
    description: LocalizedName | None = Field(
        default=None, description="New description of the action."
    )
    target: str | int | RefSelector = Field(
        description=(
            "Target status (required by Tracker): a key, a numeric id or a ``{key|id|name}``."
        ),
    )
    screen: dict[str, Any] | None = Field(default=None, description="New transition screen.")
    conditions: list[dict[str, Any]] | None = Field(
        default=None, description="New conditions under which the action can run."
    )
    functions: list[dict[str, Any]] | None = Field(
        default=None, description="New functions run when the action is executed."
    )


class WorkflowStepInput(APIModel):
    """A step in a request: a status and the actions leaving it.

    Examples:
        >>> WorkflowStepInput(status="open").model_dump(exclude_none=True)
        {'status': 'open'}
    """

    status: str | int | RefSelector = Field(
        description="Status of the step: a key, a numeric id or a ``{key|id|name}`` object."
    )
    description: LocalizedName | None = Field(
        default=None, description="Description of the step in each language."
    )
    actions: list[WorkflowActionInput] | None = Field(
        default=None, description="Actions (transitions) available from this status."
    )
    meta_action: WorkflowActionInput | None = Field(
        default=None,
        validation_alias=AliasChoices("metaAction", "meta_action"),
        serialization_alias="metaAction",
        description="Meta action of the step, run automatically.",
    )
    status_type: Literal["NEW", "IN_PROGRESS", "PAUSED", "DONE", "CANCELLED"] | None = Field(
        default=None,
        validation_alias=AliasChoices("statusType", "status_type"),
        serialization_alias="statusType",
        description="Kind of the status.",
    )


class IssueTypeResolutions(APIModel):
    """The resolutions allowed for one issue type in a workflow.

    Examples:
        >>> IssueTypeResolutions(issue_type="task", resolutions=["fixed"]).model_dump()
        {'issueType': 'task', 'resolutions': ['fixed']}
    """

    issue_type: str | int = Field(
        validation_alias=AliasChoices("issueType", "issue_type"),
        serialization_alias="issueType",
        description="Key or id of the issue type, from ``issuetypes_list``.",
    )
    resolutions: list[str | int] = Field(
        description="Keys or ids of the resolutions, from ``resolutions_list``."
    )


class WorkflowCreate(APIModel):
    """Typed request body for ``workflows.create`` (``POST /workflows``).

    Examples:
        >>> body = WorkflowCreate(
        ...     name="Design",
        ...     initial_action=WorkflowActionInput(
        ...         name=LocalizedName(ru="Открыть", en="Open"), target="open"
        ...     ),
        ...     steps=[WorkflowStepInput(status="open")],
        ... )
        >>> sorted(body.model_dump(exclude_none=True))
        ['initialAction', 'name', 'steps']
    """

    id: str | None = Field(
        default=None, description="Identifier of the workflow; generated (``W…``) when absent."
    )
    name: str = Field(description="Name of the workflow.")
    queue: str | int | RefSelector | None = Field(
        default=None,
        description="Queue to bind to: a key, an id or a ``{key|id|name}`` object; none = shared.",
    )
    type: Literal["VISUAL"] | None = Field(
        default=None, description="Workflow type; ``VISUAL`` is the only one today."
    )
    initial_action: WorkflowActionInput = Field(
        validation_alias=AliasChoices("initialAction", "initial_action"),
        serialization_alias="initialAction",
        description="The action that sets the status a new issue starts in.",
    )
    steps: list[WorkflowStepInput] = Field(
        description="Steps: each status with the actions leaving it."
    )
    issue_type_resolutions: list[IssueTypeResolutions] | None = Field(
        default=None,
        validation_alias=AliasChoices("issueTypeResolutions", "issue_type_resolutions"),
        serialization_alias="issueTypeResolutions",
        description="Resolutions allowed per issue type.",
    )


class WorkflowUpdate(APIModel):
    """Typed request body for ``workflows.edit`` (``PATCH /workflows/{id}``).

    Only the fields that are set change; a given ``steps`` list replaces the whole step list.

    Examples:
        >>> WorkflowUpdate(name="Renamed").model_dump(exclude_none=True)
        {'name': 'Renamed'}
    """

    name: str | None = Field(default=None, description="New name of the workflow.")
    type: Literal["VISUAL"] | None = Field(
        default=None, description="Workflow type; ``VISUAL`` is the only one today."
    )
    initial_action: WorkflowActionInput | None = Field(
        default=None,
        validation_alias=AliasChoices("initialAction", "initial_action"),
        serialization_alias="initialAction",
        description="New initial action.",
    )
    steps: list[WorkflowStepInput] | None = Field(
        default=None, description="New steps; replaces the existing ones."
    )
    issue_type_resolutions: list[IssueTypeResolutions] | None = Field(
        default=None,
        validation_alias=AliasChoices("issueTypeResolutions", "issue_type_resolutions"),
        serialization_alias="issueTypeResolutions",
        description="New resolutions allowed per issue type.",
    )
