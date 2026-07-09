"""Pydantic models for Tracker /queues (Queue + nested refs + QueueList).

Mirrors the ``GET /queues/`` (list) and ``GET /queues/{id}`` (single) response shapes. The
list and the single-queue endpoints return the same object, so one :class:`Queue` model serves
both; the extra ``expand`` blocks (``workflows``, ``issueTypesConfig``, …) are lenient-optional
so a plain list stays valid.
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class QueueUser(APIModel):
    """A user reference inside a queue (the ``lead`` owner or a ``teamUsers`` member).

    Example:
        >>> QueueUser.model_validate({"id": "42", "display": "Ivan Ivanov"}).display
        'Ivan Ivanov'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the user account.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the user account.")
    display: str | None = Field(default=None, description="Display name of the user.")
    passport_uid: int | None = Field(
        default=None,
        alias="passportUid",
        description="Unique account identifier in Yandex 360 for Business and Yandex ID.",
    )
    cloud_uid: str | None = Field(
        default=None,
        alias="cloudUid",
        description="Unique identifier of the user in Yandex Cloud Organization.",
    )


class QueueRef(APIModel):
    """A keyed reference to a typed entity (issue type, priority, resolution, …).

    Example:
        >>> QueueRef.model_validate({"key": "task", "display": "Task"}).key
        'task'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the entity.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the entity.")
    key: str | None = Field(default=None, description="Machine key of the entity (e.g. task, bug).")
    display: str | None = Field(default=None, description="Human-readable name of the entity.")


class QueueVersion(APIModel):
    """A version defined on the queue (``versions`` item; has no ``key``).

    Example:
        >>> QueueVersion.model_validate({"id": "4", "display": "My version"}).display
        'My version'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the version.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the version.")
    display: str | None = Field(default=None, description="Human-readable name of the version.")


class WorkflowRef(APIModel):
    """A workflow (life-cycle) reference used inside ``issueTypesConfig``.

    Example:
        >>> WorkflowRef.model_validate({"id": "dev", "display": "dev"}).id
        'dev'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the workflow.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the workflow.")
    display: str | None = Field(default=None, description="Human-readable name of the workflow.")


class IssueTypeConfig(APIModel):
    """One issue-type configuration row (``issueTypesConfig`` item).

    Binds an issue type to its workflow and the resolutions available for that type in the queue.

    Example:
        >>> IssueTypeConfig.model_validate(
        ...     {"issueType": {"key": "task"}, "workflow": {"id": "dev"}}
        ... ).issue_type.key
        'task'
    """

    issue_type: QueueRef | None = Field(
        default=None, alias="issueType", description="The issue type this configuration applies to."
    )
    workflow: WorkflowRef | None = Field(
        default=None, description="The life-cycle (workflow) bound to this issue type."
    )
    resolutions: list[QueueRef] = Field(
        default_factory=list,
        description="Resolutions that may be set when closing an issue of this type.",
    )


class Queue(APIModel):
    """A Tracker queue (``GET /queues/`` list item and ``GET /queues/{id}`` response).

    The base fields are always present; the ``teamUsers``/``issueTypes``/``versions``/
    ``workflows``/``issueTypesConfig`` blocks are populated only when requested via ``expand``.

    Example:
        >>> Queue.model_validate({"id": "3", "key": "TEST", "name": "Test"}).key
        'TEST'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the queue.",
    )
    id: str | None = Field(
        default=None, description="Unique identifier of the queue (a number in string form)."
    )
    key: str | None = Field(
        default=None,
        description="Queue key (case-sensitive), e.g. TEST — used as the issue prefix.",
    )
    version: int | None = Field(
        default=None, description="Queue version; incremented on every change to the queue."
    )
    name: str | None = Field(default=None, description="Human-readable name of the queue.")
    description: str | None = Field(default=None, description="Free-text description of the queue.")
    lead: QueueUser | None = Field(default=None, description="The queue owner (lead).")
    assign_auto: bool | None = Field(
        default=None,
        alias="assignAuto",
        description="Whether new issues in the queue are auto-assigned (true) or not (false).",
    )
    default_type: QueueRef | None = Field(
        default=None,
        alias="defaultType",
        description="Issue type assigned to new issues by default.",
    )
    default_priority: QueueRef | None = Field(
        default=None,
        alias="defaultPriority",
        description="Priority assigned to new issues by default.",
    )
    team_users: list[QueueUser] = Field(
        default_factory=list,
        alias="teamUsers",
        description="Members of the queue team (present with expand=team).",
    )
    issue_types: list[QueueRef] = Field(
        default_factory=list,
        alias="issueTypes",
        description="Issue types available in the queue (present with expand=types).",
    )
    versions: list[QueueVersion] = Field(
        default_factory=list,
        description="Versions defined on the queue (present with expand=versions).",
    )
    workflows: dict[str, list[QueueRef]] = Field(
        default_factory=dict,
        description="Life-cycles keyed by workflow name, each mapping to its issue-type refs.",
    )
    deny_voting: bool | None = Field(
        default=None,
        alias="denyVoting",
        description="Whether voting for issues is disabled (true) or allowed (false).",
    )
    issue_types_config: list[IssueTypeConfig] = Field(
        default_factory=list,
        alias="issueTypesConfig",
        description="Per-issue-type workflow/resolution configuration of the queue.",
    )


class QueueList(RootModel[list[Queue]]):
    """A bare JSON array of queues — the flat public shape of ``queues.list()``.

    Example:
        >>> QueueList.model_validate([{"key": "TEST"}]).root[0].key
        'TEST'
    """
