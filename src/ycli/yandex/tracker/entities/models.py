"""Pydantic models for the Tracker Entities API (projects / portfolios / goals).

The Entities API is a unified surface over three *entity types* — ``project``, ``portfolio``
and ``goal`` — sharing one request/response shape. Read models mirror the JSON the API
returns (an :class:`Entity` carries a top-level envelope plus a polymorphic ``fields`` block);
typed write IN-models (``*Create`` / ``*Update`` / ``*Input``) describe every request body so
the CLI and SDK never hand-assemble raw dicts.

Every field carries ``Field(description=…)`` — those descriptions surface in the MCP
``outputSchema`` and in generated docs — and full, unabbreviated names.
"""

from __future__ import annotations

from typing import Any

from pydantic import ConfigDict, Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
)

# --------------------------------------------------------------------------------------------
# Shared reference blocks
# --------------------------------------------------------------------------------------------


class UserRef(APIModel):
    """A user reference block (``author`` / ``lead`` / ``createdBy`` / an assignee).

    Example:
        >>> UserRef.model_validate({"id": "11", "display": "Имя Фамилия"}).display
        'Имя Фамилия'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the user."
    )
    id: str | None = Field(default=None, description="User identifier.")
    display: str | None = Field(default=None, description="Display name of the user.")
    passport_uid: int | None = Field(
        default=None, alias="passportUid", description="Yandex 360 / Yandex ID account uid."
    )
    cloud_uid: str | None = Field(
        default=None, alias="cloudUid", description="Yandex Cloud Organization user uid."
    )


class EntityRef(APIModel):
    """A lightweight reference to another entity (``primary`` / ``secondary`` / a source).

    Example:
        >>> EntityRef.model_validate({"id": "67f", "display": "My portfolio"}).display
        'My portfolio'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the entity."
    )
    id: str | None = Field(default=None, description="Entity identifier.")
    display: str | None = Field(default=None, description="Entity name.")


class IssueQueueRef(APIModel):
    """A queue whose issues belong to the entity (read-only ``issueQueues`` element).

    Example:
        >>> IssueQueueRef.model_validate({"key": "DE", "display": "Data"}).key
        'DE'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the queue."
    )
    id: str | None = Field(default=None, description="Queue identifier.")
    key: str | None = Field(default=None, description="Queue key.")
    display: str | None = Field(default=None, description="Queue display name.")


class ParentEntity(APIModel):
    """The ``parentEntity`` block — the portfolio(s) / parent goal an entity belongs to.

    Example:
        >>> ParentEntity.model_validate({"primary": {"id": "67f"}, "secondary": []}).primary.id
        '67f'
    """

    primary: EntityRef | None = Field(
        default=None,
        description="Primary parent (portfolio for project/portfolio, parent goal for goal).",
    )
    secondary: list[EntityRef] = Field(
        default_factory=list,
        description="Additional portfolios (projects/portfolios only; empty for goals).",
    )


class Deadline(APIModel):
    """A deadline block on a checklist item or key result.

    Example:
        >>> Deadline.model_validate({"date": "2025-12-01", "deadlineType": "date"}).deadline_type
        'date'
    """

    date: str | None = Field(
        default=None, description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm."
    )
    deadline_type: str | None = Field(
        default=None, alias="deadlineType", description="Deadline kind: 'date' or 'quarter'."
    )
    is_exceeded: bool | None = Field(
        default=None, alias="isExceeded", description="Whether the deadline has already passed."
    )


class KeyResultProgress(APIModel):
    """Quantitative progress of a 'by value' key result.

    Example:
        >>> KeyResultProgress.model_validate({"start": 0, "end": 100, "current": 40}).current
        40.0
    """

    start: float | None = Field(default=None, description="Progress value at the start of work.")
    end: float | None = Field(default=None, description="Target progress value to reach.")
    current: float | None = Field(default=None, description="Current progress value.")


class KeyResultItem(APIModel):
    """A key result of a goal (``fields.keyResultItems`` element).

    Example:
        >>> KeyResultItem.model_validate({"id": "1", "text": "Ship", "type": "binary"}).type
        'binary'
    """

    id: str | None = Field(default=None, description="Key result identifier.")
    text: str | None = Field(default=None, description="Key result text.")
    type: str | None = Field(
        default=None, description="Progress measurement: 'value' (by value) or 'binary' (by fact)."
    )
    deadline: Deadline | None = Field(default=None, description="Deadline for the key result.")
    progress: KeyResultProgress | None = Field(
        default=None, description="Quantitative progress ('by value' key results)."
    )
    achieved: bool | None = Field(
        default=None, description="Whether the key result is marked achieved."
    )
    assignee: UserRef | None = Field(default=None, description="Key result assignee.")


class ChecklistItem(APIModel):
    """A checklist item of a project/portfolio (``fields.checklistItems`` element).

    Example:
        >>> ChecklistItem.model_validate({"id": "5f", "text": "step", "checked": False}).text
        'step'
    """

    id: str | None = Field(default=None, description="Checklist item identifier.")
    text: str | None = Field(default=None, description="Item text.")
    text_html: str | None = Field(
        default=None, alias="textHtml", description="Item text rendered to HTML."
    )
    checked: bool | None = Field(default=None, description="Whether the item is marked done.")
    assignee: UserRef | None = Field(default=None, description="Item assignee.")
    deadline: Deadline | None = Field(default=None, description="Per-item deadline, if set.")
    checklist_item_type: str | None = Field(
        default=None, alias="checklistItemType", description="Item type, e.g. 'standard'."
    )


class MetricItem(APIModel):
    """A metric widget pulled onto the entity (``fields.metricItems`` element).

    Example:
        >>> MetricItem.model_validate({"id": "1", "text": "Revenue", "url": "u"}).text
        'Revenue'
    """

    id: str | None = Field(default=None, description="Metric identifier.")
    text: str | None = Field(default=None, description="Metric name.")
    url: str | None = Field(default=None, description="Link to the widget.")


class AttachmentMetadata(APIModel):
    """The ``metadata`` sub-object of an attachment (image dimensions for graphic files).

    Example:
        >>> AttachmentMetadata.model_validate({"size": "236x295"}).size
        '236x295'
    """

    size: str | None = Field(
        default=None, description="Image dimensions in pixels (WIDTHxHEIGHT); graphic files only."
    )


class Attachment(APIModel):
    """A file attached to an entity (``…/attachments`` element and ``attachments get``).

    Example:
        >>> Attachment.model_validate({"id": "3", "name": "Shops.csv", "size": 559}).name
        'Shops.csv'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the attachment."
    )
    id: str | None = Field(default=None, description="Unique file identifier.")
    name: str | None = Field(default=None, description="File name.")
    content: str | None = Field(default=None, description="Download URL for the file's raw bytes.")
    thumbnail: str | None = Field(
        default=None, description="Download URL for the preview thumbnail; graphic files only."
    )
    created_by: UserRef | None = Field(
        default=None, alias="createdBy", description="User who attached the file."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Upload timestamp (YYYY-MM-DDThh:mm…)."
    )
    mimetype: str | None = Field(default=None, description="MIME type, e.g. image/png.")
    size: int | None = Field(default=None, description="File size in bytes.")
    metadata: AttachmentMetadata | None = Field(
        default=None, description="Extra file metadata (image pixel dimensions)."
    )


class AttachmentList(RootModel[list[Attachment]]):
    """A bare JSON array of entity attachments (``…/attachments`` response).

    Example:
        >>> AttachmentList.model_validate([{"name": "Shops.csv"}]).root[0].name
        'Shops.csv'
    """


# --------------------------------------------------------------------------------------------
# Entity + its polymorphic ``fields`` block
# --------------------------------------------------------------------------------------------


class EntityFields(APIModel):
    """The ``fields`` block of an entity — the additional parameters requested via ``fields=``.

    Which keys are populated depends on the entity type and the ``fields`` query selector;
    all are optional. Goals carry ``keyResultItems``/``progressPercentage``; projects/portfolios
    carry ``checklistItems``/``start``/``quarter``; ``issueQueues`` is project-only and read-only.

    Example:
        >>> EntityFields.model_validate({"summary": "Q4", "entityStatus": "in_progress"}).summary
        'Q4'
    """

    summary: str | None = Field(default=None, description="Entity name.")
    description: str | None = Field(default=None, description="Entity description.")
    author: UserRef | None = Field(default=None, description="Author.")
    lead: UserRef | None = Field(default=None, description="Responsible person.")
    team_users: list[UserRef] = Field(
        default_factory=list, alias="teamUsers", description="Participants."
    )
    clients: list[UserRef] = Field(default_factory=list, description="Clients.")
    followers: list[UserRef] = Field(default_factory=list, description="Followers.")
    start: str | None = Field(
        default=None, description="Start date, YYYY-MM-DD (project/portfolio)."
    )
    end: str | None = Field(default=None, description="Deadline date, YYYY-MM-DD.")
    quarter: list[str] = Field(
        default_factory=list, description="Start/deadline quarters (YYYY QN); project/portfolio."
    )
    metric_items: list[MetricItem] = Field(
        default_factory=list, alias="metricItems", description="Dashboard metric widgets."
    )
    checklist_items: list[ChecklistItem] = Field(
        default_factory=list, alias="checklistItems", description="Checklist (project/portfolio)."
    )
    key_result_items: list[KeyResultItem] = Field(
        default_factory=list, alias="keyResultItems", description="Key results (goals)."
    )
    progress_percentage: float | None = Field(
        default=None,
        alias="progressPercentage",
        description="Goal progress 0..1 (read-only; null when no sub-goals/key results).",
    )
    tags: list[str] = Field(default_factory=list, description="Tags.")
    parent_entity: ParentEntity | None = Field(
        default=None, alias="parentEntity", description="Parent portfolio(s) / parent goal."
    )
    team_access: bool | None = Field(
        default=None, alias="teamAccess", description="Access limited to members only."
    )
    entity_status: str | None = Field(
        default=None,
        alias="entityStatus",
        description="Status key (e.g. draft/in_progress for projects; achieved for goals).",
    )
    issue_queues: list[IssueQueueRef] = Field(
        default_factory=list,
        alias="issueQueues",
        description="Queues feeding the project (read-only; project only).",
    )
    last_comment_updated_at: str | None = Field(
        default=None, alias="lastCommentUpdatedAt", description="Date of the last comment."
    )
    linked_goals_count: int | None = Field(
        default=None, alias="linkedGoalsCount", description="Number of linked goals."
    )
    linked_projects_count: int | None = Field(
        default=None,
        alias="linkedProjectsCount",
        description="Number of linked projects/portfolios (goals).",
    )


class Entity(APIModel):
    """A Tracker entity — a project, portfolio or goal (get/create/edit/checklist response).

    Example:
        >>> Entity.model_validate(
        ...     {"id": "655f", "entityType": "project", "fields": {"summary": "Q4"}}
        ... ).fields.summary
        'Q4'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the entity."
    )
    id: str | None = Field(default=None, description="Entity identifier.")
    version: int | None = Field(
        default=None, description="Entity version (bumps on every change; edits lock at the cap)."
    )
    short_id: int | None = Field(
        default=None, alias="shortId", description="Numeric short identifier."
    )
    entity_type: str | None = Field(
        default=None, alias="entityType", description="Entity type: project, portfolio or goal."
    )
    created_by: UserRef | None = Field(
        default=None, alias="createdBy", description="User who created the entity."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last-update timestamp."
    )
    attachments: list[Attachment] = Field(
        default_factory=list, description="Attached files (only when expand=attachments)."
    )
    fields: EntityFields | None = Field(
        default=None, description="Additional entity parameters (see EntityFields)."
    )


class EntityList(RootModel[list[Entity]]):
    """A flat list of entities — public return of :meth:`EntitiesClient.search`.

    Example:
        >>> EntityList.model_validate([{"id": "1", "entityType": "goal"}]).root[0].entity_type
        'goal'
    """


class EntitySearchResponse(APIModel):
    """The ``POST …/_search`` envelope — ``{hits, pages, values}`` (internal to the client).

    Example:
        >>> EntitySearchResponse.model_validate({"hits": 1, "values": [{"id": "1"}]}).values[0].id
        '1'
    """

    hits: int | None = Field(default=None, description="Number of results.")
    pages: int | None = Field(default=None, description="Number of result pages.")
    values: list[Entity] = Field(default_factory=list, description="Matched entity objects.")
    order_by: str | None = Field(
        default=None, alias="orderBy", description="Field the server sorted by."
    )


# --------------------------------------------------------------------------------------------
# Comments
# --------------------------------------------------------------------------------------------


class Comment(APIModel):
    """A comment on an entity (``…/comments`` element and ``comments get``).

    Example:
        >>> Comment.model_validate({"id": 22, "text": "Готово"}).text
        'Готово'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the comment."
    )
    id: int | None = Field(default=None, description="Numeric comment identifier.")
    long_id: str | None = Field(
        default=None, alias="longId", description="String (long) comment identifier."
    )
    text: str | None = Field(default=None, description="Comment text.")
    created_by: UserRef | None = Field(
        default=None, alias="createdBy", description="Comment author."
    )
    updated_by: UserRef | None = Field(
        default=None, alias="updatedBy", description="User who last edited the comment."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last-edit timestamp."
    )
    summonees: list[UserRef] = Field(
        default_factory=list, description="Users summoned in the comment."
    )
    version: int | None = Field(default=None, description="Comment version.")
    type: str | None = Field(default=None, description="Comment type, e.g. 'standard'.")
    transport: str | None = Field(default=None, description="Service field (e.g. 'internal').")


class CommentList(RootModel[list[Comment]]):
    """A flat list of comments — public return of the comment list endpoints.

    Example:
        >>> CommentList.model_validate([{"id": 22, "text": "hi"}]).root[0].text
        'hi'
    """


class CommentsRelativeResponse(APIModel):
    """The ``…/comments/_relative`` envelope — ``{comments, hasNext, hasPrev}`` (internal).

    Example:
        >>> CommentsRelativeResponse.model_validate(
        ...     {"comments": [{"id": 22}], "hasNext": False}
        ... ).comments[0].id
        22
    """

    comments: list[Comment] = Field(default_factory=list, description="Comments on this page.")
    has_next: bool | None = Field(
        default=None, alias="hasNext", description="Whether later comments exist."
    )
    has_prev: bool | None = Field(
        default=None, alias="hasPrev", description="Whether earlier comments exist."
    )


# --------------------------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------------------------


class LinkFieldValues(APIModel):
    """The ``linkFieldValues`` block of an entity link (the linked entity's summary + id).

    Example:
        >>> LinkFieldValues.model_validate({"summary": "First", "id": "658"}).summary
        'First'
    """

    summary: str | None = Field(default=None, description="Summary of the linked entity.")
    id: str | None = Field(default=None, description="Identifier of the linked entity.")


class Link(APIModel):
    """A link between two entities (``…/links`` element).

    Example:
        >>> Link.model_validate({"type": "relates", "linkFieldValues": {"id": "1"}}).type
        'relates'
    """

    type: str | None = Field(
        default=None, description="Link type, e.g. 'relates', 'depends on', 'is dependent by'."
    )
    link_field_values: LinkFieldValues | None = Field(
        default=None, alias="linkFieldValues", description="Summary + id of the linked entity."
    )


class LinkList(RootModel[list[Link]]):
    """A flat list of entity links — public return of :meth:`EntitiesClient.links_list`.

    Example:
        >>> LinkList.model_validate([{"type": "relates"}]).root[0].type
        'relates'
    """


# --------------------------------------------------------------------------------------------
# History (events)
# --------------------------------------------------------------------------------------------


class EventField(APIModel):
    """The changed ``field`` block inside an event change.

    Example:
        >>> EventField.model_validate({"id": "teamUsers", "display": "Participants"}).id
        'teamUsers'
    """

    id: str | None = Field(default=None, description="Field identifier, e.g. 'teamUsers'.")
    display: str | None = Field(default=None, description="Field display name.")


class EventChange(APIModel):
    """One change entry inside an event (``changes`` element).

    Example:
        >>> EventChange.model_validate({"diff": "<added>x</added>"}).diff
        '<added>x</added>'
    """

    diff: str | None = Field(default=None, description="Rendered diff of the change.")
    field: EventField | None = Field(default=None, description="The field that changed.")
    comment_url: str | None = Field(
        default=None, alias="commentUrl", description="Comment URL for comment changes."
    )


class EntityEvent(APIModel):
    """A single history event of an entity (``…/events/_relative`` element).

    Example:
        >>> EntityEvent.model_validate({"id": "65a", "display": "Issue updated"}).display
        'Issue updated'
    """

    id: str | None = Field(default=None, description="Event identifier.")
    author: UserRef | None = Field(default=None, description="Event author.")
    date: str | None = Field(default=None, description="Event timestamp (YYYY-MM-DDThh:mm…).")
    transport: str | None = Field(default=None, description="Service field.")
    display: str | None = Field(default=None, description="Event display title.")
    changes: list[EventChange] = Field(
        default_factory=list, description="The individual changes carried by this event."
    )


class EntityEventList(RootModel[list[EntityEvent]]):
    """A flat list of history events — public return of :meth:`EntitiesClient.history`.

    Example:
        >>> EntityEventList.model_validate([{"id": "65a"}]).root[0].id
        '65a'
    """


class EntityEventsResponse(APIModel):
    """The ``…/events/_relative`` envelope — ``{events, hasNext, hasPrev}`` (internal).

    Example:
        >>> EntityEventsResponse.model_validate(
        ...     {"events": [{"id": "65a"}], "hasNext": True}
        ... ).events[0].id
        '65a'
    """

    events: list[EntityEvent] = Field(default_factory=list, description="Events on this page.")
    has_next: bool | None = Field(
        default=None, alias="hasNext", description="Whether later events exist."
    )
    has_prev: bool | None = Field(
        default=None, alias="hasPrev", description="Whether earlier events exist."
    )


# --------------------------------------------------------------------------------------------
# Extended permissions (access)
# --------------------------------------------------------------------------------------------


class AclGroup(APIModel):
    """A group principal in an ACL grant.

    Example:
        >>> AclGroup.model_validate({"id": "1", "display": "Группа 1"}).display
        'Группа 1'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the group."
    )
    id: str | None = Field(default=None, description="Group identifier.")
    display: str | None = Field(default=None, description="Group display name.")


class AclPrincipals(APIModel):
    """The users/groups/roles granted one access level (READ / WRITE / GRANT).

    Example:
        >>> AclPrincipals.model_validate({"roles": ["OWNER"]}).roles
        ['OWNER']
    """

    users: list[UserRef] = Field(default_factory=list, description="Users granted this level.")
    groups: list[AclGroup] = Field(default_factory=list, description="Groups granted this level.")
    roles: list[str] = Field(default_factory=list, description="Roles granted this level.")


class Acl(APIModel):
    """The ``acl`` block — READ / WRITE / GRANT principal sets.

    Example:
        >>> Acl.model_validate({"READ": {"roles": ["OWNER"]}}).read.roles
        ['OWNER']
    """

    read: AclPrincipals | None = Field(
        default=None, alias="READ", description="Principals with READ access."
    )
    write: AclPrincipals | None = Field(
        default=None, alias="WRITE", description="Principals with WRITE access."
    )
    grant: AclPrincipals | None = Field(
        default=None, alias="GRANT", description="Principals with GRANT (admin) access."
    )


class ExtendedPermissions(APIModel):
    """An entity's access settings (``…/extendedPermissions`` response).

    Example:
        >>> ExtendedPermissions.model_validate(
        ...     {"acl": {"READ": {"roles": ["OWNER"]}}}
        ... ).acl.read.roles
        ['OWNER']
    """

    acl: Acl | None = Field(default=None, description="Access-control lists by level.")
    permission_sources: list[EntityRef] = Field(
        default_factory=list,
        alias="permissionSources",
        description="Parent entities this entity inherits permissions from.",
    )
    parent_entities: ParentEntity | None = Field(
        default=None, alias="parentEntities", description="Parent portfolio(s) / parent goal."
    )


# --------------------------------------------------------------------------------------------
# Bulk change
# --------------------------------------------------------------------------------------------


class BulkChangeOperation(APIModel):
    """An async bulk-change operation handle (``POST …/bulkchange/_update`` response).

    Poll :meth:`EntitiesClient.bulk_status` with ``id`` until ``status`` is terminal.

    Example:
        >>> BulkChangeOperation.model_validate({"id": "656", "status": "CREATED"}).status
        'CREATED'
    """

    id: str | None = Field(default=None, description="Bulk-change operation identifier.")
    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the operation."
    )
    created_by: UserRef | None = Field(
        default=None, alias="createdBy", description="User who started the operation."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Operation creation timestamp."
    )
    status: str | None = Field(
        default=None, description="Operation status, e.g. CREATED / COMPLETE / FAILED."
    )
    status_text: str | None = Field(
        default=None, alias="statusText", description="Human-readable status message."
    )
    execution_chunk_percent: int | None = Field(
        default=None, alias="executionChunkPercent", description="Percent of chunks processed."
    )
    execution_issue_percent: int | None = Field(
        default=None, alias="executionIssuePercent", description="Percent of entities processed."
    )


# --------------------------------------------------------------------------------------------
# Typed write bodies (IN-models)
# --------------------------------------------------------------------------------------------


class DeadlineInput(APIModel):
    """Typed ``deadline`` block for a checklist write body.

    Example:
        >>> DeadlineInput(date="2025-12-01T00:00:00.000+0000").model_dump(by_alias=True)
        {'date': '2025-12-01T00:00:00.000+0000', 'deadlineType': 'date'}
    """

    date: str = Field(description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    deadline_type: str = Field(
        default="date", alias="deadlineType", description="Deadline kind: 'date' or 'quarter'."
    )


class ParentEntityInput(APIModel):
    """Typed ``parentEntity`` block for a create/edit body (ids, not objects).

    Example:
        >>> ParentEntityInput(primary="67f").model_dump(by_alias=True, exclude_none=True)
        {'primary': '67f'}
    """

    primary: str | None = Field(
        default=None,
        description="Primary portfolio id (project/portfolio) or parent goal id (goal).",
    )
    secondary: list[str] | None = Field(
        default=None, description="Additional portfolio ids (projects/portfolios only)."
    )


class EntityFieldsInput(APIModel):
    """Typed ``fields`` object for entity create/edit bodies.

    Only ``summary`` is required by ``create``; every other key is optional and only sent when
    set. Use ``entityStatus`` to move an entity through its workflow and ``parent_entity`` to
    (re)parent it.

    ``extra="allow"`` lets custom (queue-local) field keys pass through unvalidated, matching
    the old untyped ``body: dict`` behavior. Array fields additionally accept the operator-edit
    form (``{"add": [...]}`` / ``{"set": [...]}`` / ``{"remove": [...]}``) documented at
    ``references/yandex-360/tracker/ru/api-ref/entities/about-entities.md`` (see
    ``common-format.md#edit-fields``), alongside their plain replace-list form.

    Example:
        >>> EntityFieldsInput(summary="Q4 goal").model_dump(by_alias=True, exclude_none=True)
        {'summary': 'Q4 goal'}
        >>> EntityFieldsInput(tags={"add": ["urgent"]}).model_dump(by_alias=True, exclude_none=True)
        {'tags': {'add': ['urgent']}}
    """

    model_config = ConfigDict(extra="allow")

    summary: str | None = Field(default=None, description="Entity name (required on create).")
    team_access: bool | None = Field(
        default=None, alias="teamAccess", description="Limit access to members only."
    )
    description: str | None = Field(default=None, description="Description.")
    markup_type: str | None = Field(
        default=None, alias="markupType", description="Set to 'md' when text uses YFM markup."
    )
    author: str | None = Field(default=None, description="Author user id/login.")
    lead: str | None = Field(default=None, description="Responsible user id/login.")
    team_users: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        alias="teamUsers",
        description="Participant user ids/logins — a replace list, or an "
        "{'add'|'set'|'remove': [...]} operator edit.",
    )
    clients: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="Client user ids/logins — a replace list, or an "
        "{'add'|'set'|'remove': [...]} operator edit.",
    )
    followers: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="Follower user ids/logins — a replace list, or an "
        "{'add'|'set'|'remove': [...]} operator edit.",
    )
    start: str | None = Field(default=None, description="Start date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    end: str | None = Field(
        default=None, description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm."
    )
    tags: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="Tags — a replace list, or an {'add'|'set'|'remove': [...]} operator edit.",
    )
    parent_entity: ParentEntityInput | None = Field(
        default=None, alias="parentEntity", description="Parent portfolio(s) / parent goal ids."
    )
    entity_status: str | None = Field(
        default=None, alias="entityStatus", description="Status key to set."
    )


class LinkInput(APIModel):
    """A link spec used by create-link and the bulk ``values.links`` array.

    Example:
        >>> LinkInput(relationship="relates", entity="658").model_dump(by_alias=True)
        {'relationship': 'relates', 'entity': '658'}
    """

    relationship: str = Field(
        description="Link type, e.g. 'depends on', 'is dependent by', 'works towards'."
    )
    entity: str = Field(description="Identifier of the entity to link to.")


class EntityCreate(APIModel):
    """Typed request body for ``POST /entities/{type}`` — a ``{fields: {...}}`` envelope.

    Example:
        >>> EntityCreate(fields=EntityFieldsInput(summary="Q4")).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'fields': {'summary': 'Q4'}}
    """

    fields: EntityFieldsInput = Field(description="Entity settings (summary is required).")


class EntityUpdate(APIModel):
    """Typed request body for ``PATCH /entities/{type}/{id}`` (edit fields, comment, links).

    Example:
        >>> EntityUpdate(fields=EntityFieldsInput(summary="New")).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'fields': {'summary': 'New'}}
    """

    fields: EntityFieldsInput | None = Field(default=None, description="Fields to change.")
    comment: str | None = Field(default=None, description="Comment to add with the change.")
    links: list[LinkInput] | None = Field(default=None, description="Links to add.")


class CommentCreate(APIModel):
    """Typed request body for ``POST …/comments`` (add a comment).

    Example:
        >>> CommentCreate(text="Готово").model_dump(by_alias=True, exclude_none=True)
        {'text': 'Готово'}
    """

    text: str = Field(description="Comment text (required).")
    attachment_ids: list[str] | None = Field(
        default=None, alias="attachmentIds", description="Temp-file ids to attach as files."
    )
    summonees: list[str] | None = Field(
        default=None, description="User ids/logins to summon in the comment."
    )
    maillist_summonees: list[str] | None = Field(
        default=None, alias="maillistSummonees", description="Mailing lists to summon."
    )


class CommentUpdate(APIModel):
    """Typed request body for ``PATCH …/comments/{comment_id}`` (the id travels in the path).

    Example:
        >>> CommentUpdate(text="fixed").model_dump(by_alias=True, exclude_none=True)
        {'text': 'fixed'}
    """

    text: str | None = Field(default=None, description="New comment text.")
    attachment_ids: list[str] | None = Field(
        default=None, alias="attachmentIds", description="Temp-file ids to attach as files."
    )
    summonees: list[str] | None = Field(
        default=None, description="User ids/logins to summon in the comment."
    )
    maillist_summonees: list[str] | None = Field(
        default=None, alias="maillistSummonees", description="Mailing lists to summon."
    )


class ChecklistItemInput(APIModel):
    """A checklist item in a create (``[{text}]``) or edit-all (``[{id, text}]``) body.

    Example:
        >>> ChecklistItemInput(text="step").model_dump(by_alias=True, exclude_none=True)
        {'text': 'step'}
    """

    id: str | None = Field(
        default=None, description="Item id (required only in the edit-all body)."
    )
    text: str | None = Field(default=None, description="Item text.")
    checked: bool | None = Field(default=None, description="Whether the item is marked done.")
    assignee: str | None = Field(default=None, description="Assignee user id/login.")
    deadline: DeadlineInput | None = Field(default=None, description="Per-item deadline.")


class ChecklistItemsInput(RootModel[list[ChecklistItemInput]]):
    """A bare array body for checklist create / edit-all.

    Example:
        >>> ChecklistItemsInput([ChecklistItemInput(text="a")]).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        [{'text': 'a'}]
    """


class ChecklistMove(APIModel):
    """Typed request body for ``POST …/checklistItems/{id}/_move`` (reorder an item).

    Example:
        >>> ChecklistMove(before="65f").model_dump(by_alias=True, exclude_none=True)
        {'before': '65f'}
    """

    before: str | None = Field(
        default=None, description="Id of the item to insert the moved item before."
    )


class AclPrincipalsInput(APIModel):
    """The users/groups/roles for one access level in a permissions-set body.

    Example:
        >>> AclPrincipalsInput(roles=["OWNER"]).model_dump(by_alias=True, exclude_none=True)
        {'roles': ['OWNER']}
    """

    users: list[str] | None = Field(default=None, description="User ids to grant this level.")
    groups: list[str] | None = Field(default=None, description="Group ids to grant this level.")
    roles: list[str] | None = Field(default=None, description="Roles to grant this level.")


class AclInput(APIModel):
    """The ``acl`` block for a permissions-set body (READ / WRITE / GRANT principal sets).

    Example:
        >>> AclInput(read=AclPrincipalsInput(roles=["OWNER"])).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'READ': {'roles': ['OWNER']}}
    """

    read: AclPrincipalsInput | None = Field(
        default=None, alias="READ", description="Principals to grant READ."
    )
    write: AclPrincipalsInput | None = Field(
        default=None, alias="WRITE", description="Principals to grant WRITE."
    )
    grant: AclPrincipalsInput | None = Field(
        default=None, alias="GRANT", description="Principals to grant GRANT (admin)."
    )


class ExtendedPermissionsUpdate(APIModel):
    """Typed request body for ``PATCH …/extendedPermissions`` (set access settings).

    Example:
        >>> ExtendedPermissionsUpdate(
        ...     acl=AclInput(read=AclPrincipalsInput(roles=["OWNER"]))
        ... ).model_dump(by_alias=True, exclude_none=True)
        {'acl': {'READ': {'roles': ['OWNER']}}}
    """

    acl: AclInput = Field(description="Access-control lists to set, by level.")


class BulkChangeValues(APIModel):
    """The ``values`` object of a bulk-change body (fields + comment + links).

    Example:
        >>> BulkChangeValues(comment="done").model_dump(by_alias=True, exclude_none=True)
        {'comment': 'done'}
    """

    fields: dict[str, Any] | None = Field(
        default=None, description="Field-key → value pairs to apply to every entity."
    )
    comment: str | None = Field(default=None, description="Comment to add to every entity.")
    links: list[LinkInput] | None = Field(default=None, description="Links to add to every entity.")


class BulkChangeUpdate(APIModel):
    """Typed request body for ``POST …/bulkchange/_update`` (mass-edit entities).

    Example:
        >>> BulkChangeUpdate(
        ...     meta_entities=["1", "2"], values=BulkChangeValues(comment="done")
        ... ).model_dump(by_alias=True, exclude_none=True)
        {'metaEntities': ['1', '2'], 'values': {'comment': 'done'}}
    """

    meta_entities: list[str] = Field(
        alias="metaEntities", description="Identifiers of the entities to update."
    )
    values: BulkChangeValues = Field(description="What to change on every listed entity.")


# --------------------------------------------------------------------------------------------
# Report (issue-report builder)
# --------------------------------------------------------------------------------------------


class ReportSort(APIModel):
    """A sort clause for a report filter (``parameters.filter.sorts`` element).

    Example:
        >>> ReportSort(order_by="updated", order_asc=False).model_dump(by_alias=True)
        {'orderBy': 'updated', 'orderAsc': False}
    """

    order_by: str = Field(alias="orderBy", description="Issue field to sort the report by.")
    order_asc: bool = Field(
        default=True,
        alias="orderAsc",
        description="Sort direction: true ascending, false descending.",
    )


class ReportFilter(APIModel):
    """The ``filter`` block of a report — a Tracker Query Language ``query`` plus optional sorts.

    Example:
        >>> ReportFilter(query="Queue: SUPPORT").model_dump(by_alias=True, exclude_none=True)
        {'query': 'Queue: SUPPORT'}
    """

    query: str = Field(description="Issue filter in Tracker Query Language.")
    sorts: list[ReportSort] | None = Field(
        default=None, description="Sort clauses applied to the report."
    )


class ReportParameters(APIModel):
    """The ``parameters`` block of a report — export settings plus the issue filter.

    Example:
        >>> ReportParameters(filter=ReportFilter(query="Q"), fields=["key"]).format
        'xlsx'
    """

    type: str = Field(
        default="issueFilterExport", description="Export type. Value: issueFilterExport."
    )
    format: str = Field(default="xlsx", description="Export format: xlsx, xml or csv.")
    filter: ReportFilter = Field(description="Issue filtering parameters for the report.")
    fields: list[str] = Field(description="Issue field keys to include as report columns.")


class ReportFieldsInput(APIModel):
    """The ``fields`` object of a report create body — the report name plus export ``parameters``.

    Example:
        >>> params = ReportParameters(filter=ReportFilter(query="Q"), fields=["key"])
        >>> ReportFieldsInput(summary="Export", parameters=params).summary
        'Export'
    """

    summary: str = Field(description="Report name.")
    parameters: ReportParameters = Field(description="Export settings and issue filter.")


class ReportCreate(APIModel):
    """Typed request body for ``POST /entities/report/`` — a ``{fields: {...}}`` envelope.

    Example:
        >>> params = ReportParameters(filter=ReportFilter(query="Q"), fields=["key"])
        >>> body = ReportFieldsInput(summary="Export", parameters=params)
        >>> list(ReportCreate(fields=body).model_dump(by_alias=True))
        ['fields']
    """

    fields: ReportFieldsInput = Field(description="Report settings (summary + export parameters).")
