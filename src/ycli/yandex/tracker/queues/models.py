"""Pydantic models for Tracker /queues (Queue + nested refs + ItemList[Queue]).

Mirrors the ``GET /queues/`` (list) and ``GET /queues/{id}`` (single) response shapes. The
list and the single-queue endpoints return the same object, so one :class:`Queue` model serves
both; the extra ``expand`` blocks (``workflows``, ``issueTypesConfig``, …) are lenient-optional
so a plain list stays valid.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.tracker.models import (
    AccessPermissions,
    KeyedReference,
    Reference,
    UserReference,
)


class IssueTypeConfig(APIModel):
    """One issue-type configuration row (``issueTypesConfig`` item).

    Binds an issue type to its workflow and the resolutions available for that type in the queue.

    Examples:
        >>> IssueTypeConfig.model_validate(
        ...     {"issueType": {"key": "task"}, "workflow": {"id": "dev"}}
        ... ).issue_type.key
        'task'
    """

    issue_type: KeyedReference | None = Field(
        default=None, alias="issueType", description="The issue type this configuration applies to."
    )
    workflow: Reference | None = Field(
        default=None, description="The life-cycle (workflow) bound to this issue type."
    )
    resolutions: list[KeyedReference] = Field(
        default_factory=list,
        description="Resolutions that may be set when closing an issue of this type.",
    )


class Queue(APIModel):
    """A Tracker queue (``GET /queues/`` list item and ``GET /queues/{id}`` response).

    The base fields are always present; the ``teamUsers``/``issueTypes``/``versions``/
    ``workflows``/``issueTypesConfig`` blocks are populated only when requested via ``expand``.

    Examples:
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
    lead: UserReference | None = Field(default=None, description="The queue owner (lead).")
    assign_auto: bool | None = Field(
        default=None,
        alias="assignAuto",
        description="Whether new issues in the queue are auto-assigned (true) or not (false).",
    )
    default_type: KeyedReference | None = Field(
        default=None,
        alias="defaultType",
        description="Issue type assigned to new issues by default.",
    )
    default_priority: KeyedReference | None = Field(
        default=None,
        alias="defaultPriority",
        description="Priority assigned to new issues by default.",
    )
    team_users: list[UserReference] = Field(
        default_factory=list,
        alias="teamUsers",
        description="Members of the queue team (present with expand=team).",
    )
    issue_types: list[KeyedReference] = Field(
        default_factory=list,
        alias="issueTypes",
        description="Issue types available in the queue (present with expand=types).",
    )
    versions: list[Reference] = Field(
        default_factory=list,
        description="Versions defined on the queue (present with expand=versions).",
    )
    workflows: dict[str, list[KeyedReference]] = Field(
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


class QueueVersionInfo(APIModel):
    """A queue version (``GET /queues/{id}/versions`` item, ``POST /versions/`` result).

    Unlike the bare reference inside an ``expand=versions`` block, this carries the full
    version record — release/archive flags, date range and the owning queue reference.

    Examples:
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
    queue: KeyedReference | None = Field(
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


class QueueField(APIModel):
    """A required/local field defined on a queue (``GET /queues/{id}/fields`` item).

    Examples:
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


class IssueTypeConfigInput(RequestBody):
    """One ``issueTypesConfig`` row in a create-queue body — binds a type to its workflow.

    Examples:
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


class QueueCreate(RequestBody):
    """Typed request body for ``queues.create`` (``POST /queues/``).

    Examples:
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


class QueueTagRemove(RequestBody):
    """Typed request body for ``queues.tag_remove`` (``POST /queues/{id}/tags/_remove``).

    Examples:
        >>> QueueTagRemove(tag="obsolete").tag
        'obsolete'
    """

    tag: str = Field(description="Name of the tag to remove from the queue.")


class QueueVersionCreate(RequestBody):
    """Typed request body for ``queues.version_create`` (``POST /versions/``).

    Examples:
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


class QueuePermissionSubjects(RequestBody):
    """The add/remove form of a permission subject list (users, groups or roles).

    Passing a bare array instead overwrites the subject list; this object form incrementally
    adds and/or revokes specific subjects.

    Examples:
        >>> QueuePermissionSubjects(add=["author"]).add
        ['author']
    """

    add: list[str | int] | None = Field(
        default=None, description="Subjects (logins/ids/role keys) to grant the permission to."
    )
    remove: list[str | int] | None = Field(
        default=None, description="Subjects (logins/ids/role keys) to revoke the permission from."
    )


class QueuePermissionScope(RequestBody):
    """One permission category (create/write/read/grant) in a permissions PATCH body.

    Each subject list is either a bare array (which overwrites) or a
    :class:`QueuePermissionSubjects` add/remove object (which mutates incrementally).

    Examples:
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


class QueuePermissionsUpdate(RequestBody):
    """Typed request body for ``queues.set_permissions`` (``PATCH /queues/{id}/permissions``).

    Set at least one category. Each names the users/groups/roles the permission applies to.

    Examples:
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

    Examples:
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


class QueueVersionUpdate(RequestBody):
    """Typed request body for ``queues.version_edit`` (``PATCH /versions/{id}``).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Examples:
        >>> QueueVersionUpdate(name="v1.1").model_dump(exclude_none=True)
        {'name': 'v1.1'}
    """

    name: str | None = Field(default=None, description="New name of the version.")
    description: str | None = Field(default=None, description="New description of the version.")
    start_date: str | None = Field(
        default=None,
        serialization_alias="startDate",
        description="New version start date (YYYY-MM-DD).",
    )
    due_date: str | None = Field(
        default=None,
        serialization_alias="dueDate",
        description="New version due date (YYYY-MM-DD).",
    )


class QueueUserAccess(APIModel):
    """One user's rights in a queue (``GET /queues/{id}/permissions/users/{userId}``).

    Examples:
        >>> QueueUserAccess.model_validate({"user": {"id": "11"}, "permissions": {}}).user.id
        '11'
    """

    user: UserReference | None = Field(default=None, description="The user the rights belong to.")
    permissions: AccessPermissions | None = Field(
        default=None, description="Rights by kind, with who grants each (personal, group, role)."
    )
    components: list[Reference] = Field(
        default_factory=list, description="Components the user has access to."
    )


class QueueGroupAccess(APIModel):
    """One group's rights in a queue (``GET /queues/{id}/permissions/groups/{groupId}``).

    Examples:
        >>> QueueGroupAccess.model_validate({"group": {"id": "5"}}).group.id
        '5'
    """

    group: Reference | None = Field(default=None, description="The group the rights belong to.")
    permissions: AccessPermissions | None = Field(
        default=None, description="Rights by kind, with who grants each."
    )
    components: list[Reference] = Field(
        default_factory=list, description="Components the group has access to."
    )
