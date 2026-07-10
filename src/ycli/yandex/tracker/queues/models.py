"""Pydantic models for Tracker /queues (Queue + nested refs + QueueList).

Mirrors the ``GET /queues/`` (list) and ``GET /queues/{id}`` (single) response shapes. The
list and the single-queue endpoints return the same object, so one :class:`Queue` model serves
both; the extra ``expand`` blocks (``workflows``, ``issueTypesConfig``, …) are lenient-optional
so a plain list stays valid.
"""

from __future__ import annotations

from typing import Any

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
    id: str | int | None = Field(
        default=None,
        description="Unique identifier of the queue (a number; may arrive as an int or a string).",
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


class QueueTagList(RootModel[list[str]]):
    """A bare JSON array of queue tag names (``GET /queues/{id}/tags``).

    Example:
        >>> QueueTagList.model_validate(["tag1", "tag2"]).root[0]
        'tag1'
    """


class QueueVersionInfo(APIModel):
    """A queue version (``GET /queues/{id}/versions`` item, ``POST /versions/`` result).

    Unlike the lean ``QueueVersion`` inside an ``expand=versions`` block, this carries the full
    version record — release/archive flags, date range and the owning queue reference.

    Example:
        >>> QueueVersionInfo.model_validate({"id": 1, "name": "v0.1", "released": False}).name
        'v0.1'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the version.",
    )
    id: int | None = Field(default=None, description="Unique identifier of the version.")
    version: int | None = Field(default=None, description="Sequence number of the version.")
    queue: QueueRef | None = Field(
        default=None, description="Reference to the queue this version belongs to."
    )
    name: str | None = Field(default=None, description="Human-readable name of the version.")
    description: str | None = Field(
        default=None, description="Free-text description of the version."
    )
    start_date: str | None = Field(
        default=None, alias="startDate", description="Version start date (YYYY-MM-DD)."
    )
    due_date: str | None = Field(
        default=None, alias="dueDate", description="Version due/finish date (YYYY-MM-DD)."
    )
    released: bool | None = Field(
        default=None, description="Whether the version has been released (true) or not (false)."
    )
    archived: bool | None = Field(
        default=None, description="Whether the version is archived (true) or active (false)."
    )


class QueueVersionInfoList(RootModel[list[QueueVersionInfo]]):
    """A bare JSON array of queue versions (``GET /queues/{id}/versions``).

    Example:
        >>> QueueVersionInfoList.model_validate([{"id": 1, "name": "v0.1"}]).root[0].name
        'v0.1'
    """


class QueueField(APIModel):
    """A required/local field defined on a queue (``GET /queues/{id}/fields`` item).

    Example:
        >>> QueueField.model_validate({"id": "myfield", "name": "My field"}).name
        'My field'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the field.",
    )
    id: str | None = Field(default=None, description="Identifier of the field.")
    name: str | None = Field(default=None, description="Human-readable name of the field.")
    version: int | None = Field(
        default=None, description="Field version; incremented on every change to the field."
    )
    field_schema: Any = Field(
        default=None,
        alias="schema",
        description="Content-type descriptor: {type: float|string, required: bool}.",
    )
    readonly: bool | None = Field(
        default=None, description="Whether the field is read-only (true) or editable (false)."
    )
    options: bool | None = Field(
        default=None, description="Whether the field offers a fixed set of fill-in options."
    )
    suggest: bool | None = Field(
        default=None, description="Whether suggestions are shown while filling the field in."
    )
    options_provider: Any = Field(
        default=None,
        alias="optionsProvider",
        description="Descriptor of the set of allowed values for the field.",
    )
    query_provider: Any = Field(
        default=None,
        alias="queryProvider",
        description="Descriptor of the field's type for query-language requests.",
    )
    order: int | None = Field(
        default=None,
        description="Display weight in the UI; lower-weight fields render above higher ones.",
    )


class QueueFieldList(RootModel[list[QueueField]]):
    """A bare JSON array of queue required fields (``GET /queues/{id}/fields``).

    Example:
        >>> QueueFieldList.model_validate([{"id": "myfield"}]).root[0].id
        'myfield'
    """


class IssueTypeConfigInput(APIModel):
    """One ``issueTypesConfig`` row in a create-queue body — binds a type to its workflow.

    Example:
        >>> IssueTypeConfigInput(issue_type="task", workflow="oicn").issue_type
        'task'
    """

    issue_type: str = Field(
        alias="issueType", description="Key of the issue type this row configures."
    )
    workflow: str = Field(description="Identifier of the workflow bound to the issue type.")
    resolutions: list[str] | None = Field(
        default=None,
        description="Keys/identifiers of resolutions selectable when closing this type.",
    )


class QueueCreate(APIModel):
    """Typed request body for ``queues.create`` (``POST /queues/``).

    Example:
        >>> QueueCreate(
        ...     key="DESIGN",
        ...     name="Design",
        ...     lead="username",
        ...     default_type="task",
        ...     default_priority="normal",
        ... ).key
        'DESIGN'
    """

    key: str = Field(description="Key of the new queue (case-sensitive, e.g. DESIGN).")
    name: str = Field(description="Human-readable name of the queue.")
    lead: str = Field(description="Login or identifier of the queue owner (lead).")
    default_type: str = Field(
        serialization_alias="defaultType",
        description="Key or id of the issue type assigned to new issues by default.",
    )
    default_priority: str = Field(
        serialization_alias="defaultPriority",
        description="Key or id of the priority assigned to new issues by default.",
    )
    issue_types_config: list[IssueTypeConfigInput] | None = Field(
        default=None,
        serialization_alias="issueTypesConfig",
        description="Per-issue-type workflow/resolution configuration of the queue.",
    )


class QueueTagRemove(APIModel):
    """Typed request body for ``queues.tag_remove`` (``POST /queues/{id}/tags/_remove``).

    Example:
        >>> QueueTagRemove(tag="obsolete").tag
        'obsolete'
    """

    tag: str = Field(description="Name of the tag to remove from the queue.")


class QueueVersionCreate(APIModel):
    """Typed request body for ``queues.version_create`` (``POST /versions/``).

    Example:
        >>> QueueVersionCreate(queue="TEST", name="v0.1").name
        'v0.1'
    """

    queue: str = Field(description="Key of the queue the version is created in.")
    name: str = Field(description="Name of the new version.")
    description: str | None = Field(
        default=None, description="Free-text description of the version."
    )
    start_date: str | None = Field(
        default=None,
        serialization_alias="startDate",
        description="Version start date (YYYY-MM-DD).",
    )
    due_date: str | None = Field(
        default=None, serialization_alias="dueDate", description="Version due date (YYYY-MM-DD)."
    )


class QueuePermissionSubjects(APIModel):
    """The add/remove form of a permission subject list (users, groups or roles).

    Passing a bare array instead overwrites the subject list; this object form incrementally
    adds and/or revokes specific subjects.

    Example:
        >>> QueuePermissionSubjects(add=["author"]).add
        ['author']
    """

    add: list[str | int] | None = Field(
        default=None, description="Subjects (logins/ids/role keys) to grant the permission to."
    )
    remove: list[str | int] | None = Field(
        default=None, description="Subjects (logins/ids/role keys) to revoke the permission from."
    )


class QueuePermissionScope(APIModel):
    """One permission category (create/write/read/grant) in a permissions PATCH body.

    Each subject list is either a bare array (which overwrites) or a
    :class:`QueuePermissionSubjects` add/remove object (which mutates incrementally).

    Example:
        >>> QueuePermissionScope(roles=["author"]).roles
        ['author']
    """

    users: list[str | int] | QueuePermissionSubjects | None = Field(
        default=None, description="Users the permission applies to (logins/ids or add/remove)."
    )
    groups: list[str | int] | QueuePermissionSubjects | None = Field(
        default=None, description="Groups the permission applies to (ids or add/remove)."
    )
    roles: list[str] | QueuePermissionSubjects | None = Field(
        default=None,
        description="Roles the permission applies to (author/assignee/follower/access).",
    )


class QueuePermissionsUpdate(APIModel):
    """Typed request body for ``queues.set_permissions`` (``PATCH /queues/{id}/permissions``).

    Set at least one category. Each names the users/groups/roles the permission applies to.

    Example:
        >>> QueuePermissionsUpdate(create=QueuePermissionScope(roles=["author"])).create.roles
        ['author']
    """

    create: QueuePermissionScope | None = Field(
        default=None, description="Who may create issues in the queue."
    )
    write: QueuePermissionScope | None = Field(
        default=None, description="Who may edit issues in the queue."
    )
    read: QueuePermissionScope | None = Field(
        default=None, description="Who may read issues in the queue."
    )
    grant: QueuePermissionScope | None = Field(
        default=None, description="Who may change the queue's settings."
    )


class QueuePermissions(APIModel):
    """The permissions object returned by ``PATCH /queues/{id}/permissions``.

    Example:
        >>> QueuePermissions.model_validate({"version": 11}).version
        11
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL of the queue's permissions object.",
    )
    version: int | None = Field(
        default=None, description="Permissions version; incremented on every change."
    )
    create: Any = Field(default=None, description="Effective create-issue permissions.")
    write: Any = Field(default=None, description="Effective edit-issue permissions.")
    read: Any = Field(default=None, description="Effective read-issue permissions.")
    grant: Any = Field(default=None, description="Effective change-settings permissions.")
