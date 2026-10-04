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

from typing import Any, Literal

from pydantic import AliasChoices, ConfigDict, Field

from ycli.yandex.models import (
    APIModel,
    RequestBody,  # pydantic resolves field types via get_type_hints() at runtime
)
from ycli.yandex.tracker.models import (
    AttachmentMetadata,
    Deadline,
    DeadlineInput,
    KeyedReference,
    Reference,
    UserReference,
)

# --------------------------------------------------------------------------------------------
# Shared reference blocks
# --------------------------------------------------------------------------------------------

#: The file a report is exported to.
ReportFormat = Literal["xlsx", "xml", "csv"] | str

#: The entity types the Entities API unifies; ``report`` is documented for search only.
EntityType = Literal["project", "portfolio", "goal", "report"] | str


class ParentEntity(APIModel):
    """The ``parentEntity`` block — the portfolio(s) / parent goal an entity belongs to.

    Examples:
        >>> ParentEntity.model_validate({"primary": {"id": "67f"}, "secondary": []}).primary.id
        '67f'
    """

    primary: Reference | None = Field(
        default=None,
        description="Primary parent (portfolio for project/portfolio, parent goal for goal).",
    )
    secondary: list[Reference] = Field(
        default_factory=list,
        description="Additional portfolios (projects/portfolios only; empty for goals).",
    )


class KeyResultProgress(APIModel):
    """Quantitative progress of a 'by value' key result.

    Examples:
        >>> KeyResultProgress.model_validate({"start": 0, "end": 100, "current": 40}).current
        40.0
    """

    start: float | None = Field(default=None, description="Progress value at the start of work.")
    end: float | None = Field(default=None, description="Target progress value to reach.")
    current: float | None = Field(default=None, description="Current progress value.")


class KeyResultItem(APIModel):
    """A key result of a goal (``fields.keyResultItems`` element).

    Examples:
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
    assignee: UserReference | None = Field(default=None, description="Key result assignee.")


class ChecklistItem(APIModel):
    """A checklist item of a project/portfolio (``fields.checklistItems`` element).

    Examples:
        >>> ChecklistItem.model_validate({"id": "5f", "text": "step", "checked": False}).text
        'step'
    """

    id: str | None = Field(default=None, description="Checklist item identifier.")
    text: str | None = Field(default=None, description="Item text.")
    text_html: str | None = Field(
        default=None, alias="textHtml", description="Item text rendered to HTML."
    )
    checked: bool | None = Field(default=None, description="Whether the item is marked done.")
    assignee: UserReference | None = Field(default=None, description="Item assignee.")
    deadline: Deadline | None = Field(default=None, description="Per-item deadline, if set.")
    checklist_item_type: str | None = Field(
        default=None, alias="checklistItemType", description="Item type, e.g. 'standard'."
    )


class MetricItem(APIModel):
    """A metric widget pulled onto the entity (``fields.metricItems`` element).

    Examples:
        >>> MetricItem.model_validate({"id": "1", "text": "Revenue", "url": "u"}).text
        'Revenue'
    """

    id: str | None = Field(default=None, description="Metric identifier.")
    text: str | None = Field(default=None, description="Metric name.")
    url: str | None = Field(default=None, description="Link to the widget.")


class Attachment(APIModel):
    """A file attached to an entity (``…/attachments`` element and ``attachments get``).

    Examples:
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
    created_by: UserReference | None = Field(
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


# --------------------------------------------------------------------------------------------
# Entity + its polymorphic ``fields`` block
# --------------------------------------------------------------------------------------------


class EntityFields(APIModel):
    """The ``fields`` block of an entity — the additional parameters requested via ``fields=``.

    Which keys are populated depends on the entity type and the ``fields`` query selector;
    all are optional. Goals carry ``keyResultItems``/``progressPercentage``; projects/portfolios
    carry ``checklistItems``/``start``/``quarter``; ``issueQueues`` is project-only and read-only.

    Examples:
        >>> EntityFields.model_validate({"summary": "Q4", "entityStatus": "in_progress"}).summary
        'Q4'
    """

    summary: str | None = Field(default=None, description="Entity name.")
    description: str | None = Field(default=None, description="Entity description.")
    author: UserReference | None = Field(default=None, description="Author.")
    lead: UserReference | None = Field(default=None, description="Responsible person.")
    team_users: list[UserReference] = Field(
        default_factory=list, alias="teamUsers", description="Participants."
    )
    clients: list[UserReference] = Field(default_factory=list, description="Clients.")
    followers: list[UserReference] = Field(default_factory=list, description="Followers.")
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
    issue_queues: list[KeyedReference] = Field(
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

    Examples:
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
    created_by: UserReference | None = Field(
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


class EntitySearchResponse(APIModel):
    """The ``POST …/_search`` envelope — ``{hits, pages, values}`` (internal to the client).

    Examples:
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

    Examples:
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
    created_by: UserReference | None = Field(
        default=None, alias="createdBy", description="Comment author."
    )
    updated_by: UserReference | None = Field(
        default=None, alias="updatedBy", description="User who last edited the comment."
    )
    created_at: str | None = Field(
        default=None, alias="createdAt", description="Creation timestamp."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="Last-edit timestamp."
    )
    summonees: list[UserReference] = Field(
        default_factory=list, description="Users summoned in the comment."
    )
    version: int | None = Field(default=None, description="Comment version.")
    type: str | None = Field(default=None, description="Comment type, e.g. 'standard'.")
    transport: str | None = Field(default=None, description="Service field (e.g. 'internal').")


class CommentsRelativeResponse(APIModel):
    """The ``…/comments/_relative`` envelope — ``{comments, hasNext, hasPrev}`` (internal).

    Examples:
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

    Examples:
        >>> LinkFieldValues.model_validate({"summary": "First", "id": "658"}).summary
        'First'
    """

    summary: str | None = Field(default=None, description="Summary of the linked entity.")
    id: str | None = Field(default=None, description="Identifier of the linked entity.")


class Link(APIModel):
    """A link between two entities (``…/links`` element).

    Examples:
        >>> Link.model_validate({"type": "relates", "linkFieldValues": {"id": "1"}}).type
        'relates'
    """

    type: str | None = Field(
        default=None, description="Link type, e.g. 'relates', 'depends on', 'is dependent by'."
    )
    link_field_values: LinkFieldValues | None = Field(
        default=None, alias="linkFieldValues", description="Summary + id of the linked entity."
    )


# --------------------------------------------------------------------------------------------
# History (events)
# --------------------------------------------------------------------------------------------


class EventField(APIModel):
    """The changed ``field`` block inside an event change.

    Examples:
        >>> EventField.model_validate({"id": "teamUsers", "display": "Participants"}).id
        'teamUsers'
    """

    id: str | None = Field(default=None, description="Field identifier, e.g. 'teamUsers'.")
    display: str | None = Field(default=None, description="Field display name.")


class EventChange(APIModel):
    """One change entry inside an event (``changes`` element).

    Examples:
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

    Examples:
        >>> EntityEvent.model_validate({"id": "65a", "display": "Issue updated"}).display
        'Issue updated'
    """

    id: str | None = Field(default=None, description="Event identifier.")
    author: UserReference | None = Field(default=None, description="Event author.")
    date: str | None = Field(default=None, description="Event timestamp (YYYY-MM-DDThh:mm…).")
    transport: str | None = Field(default=None, description="Service field.")
    display: str | None = Field(default=None, description="Event display title.")
    changes: list[EventChange] = Field(
        default_factory=list, description="The individual changes carried by this event."
    )


class EntityEventsResponse(APIModel):
    """The ``…/events/_relative`` envelope — ``{events, hasNext, hasPrev}`` (internal).

    Examples:
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


class ACLPrincipals(APIModel):
    """The users/groups/roles granted one access level (READ / WRITE / GRANT).

    Examples:
        >>> ACLPrincipals.model_validate({"roles": ["OWNER"]}).roles
        ['OWNER']
    """

    users: list[UserReference] = Field(
        default_factory=list, description="Users granted this level."
    )
    groups: list[Reference] = Field(default_factory=list, description="Groups granted this level.")
    roles: list[str] = Field(default_factory=list, description="Roles granted this level.")


class ACL(APIModel):
    """The ``acl`` block — READ / WRITE / GRANT principal sets.

    Examples:
        >>> ACL.model_validate({"READ": {"roles": ["OWNER"]}}).read.roles
        ['OWNER']
    """

    read: ACLPrincipals | None = Field(
        default=None, alias="READ", description="Principals with READ access."
    )
    write: ACLPrincipals | None = Field(
        default=None, alias="WRITE", description="Principals with WRITE access."
    )
    grant: ACLPrincipals | None = Field(
        default=None, alias="GRANT", description="Principals with GRANT (admin) access."
    )


class ExtendedPermissions(APIModel):
    """An entity's access settings (``…/extendedPermissions`` response).

    Examples:
        >>> ExtendedPermissions.model_validate(
        ...     {"acl": {"READ": {"roles": ["OWNER"]}}}
        ... ).acl.read.roles
        ['OWNER']
    """

    acl: ACL | None = Field(default=None, description="Access-control lists by level.")
    permission_sources: list[Reference] = Field(
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

    Examples:
        >>> BulkChangeOperation.model_validate({"id": "656", "status": "CREATED"}).status
        'CREATED'
    """

    id: str | None = Field(default=None, description="Bulk-change operation identifier.")
    self_url: str | None = Field(
        default=None, alias="self", description="API resource address of the operation."
    )
    created_by: UserReference | None = Field(
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


class ParentEntityInput(RequestBody):
    """Typed ``parentEntity`` block for a create/edit body (ids, not objects).

    Examples:
        >>> ParentEntityInput(primary="67f").model_dump(exclude_none=True)
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

    Examples:
        >>> EntityFieldsInput(summary="Q4 goal").model_dump(exclude_none=True)
        {'summary': 'Q4 goal'}
        >>> EntityFieldsInput(tags={"add": ["urgent"]}).model_dump(exclude_none=True)
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


class LinkInput(RequestBody):
    """A link spec used by create-link and the bulk ``values.links`` array.

    Examples:
        >>> LinkInput(relationship="relates", entity="658").model_dump()
        {'relationship': 'relates', 'entity': '658'}
    """

    relationship: str = Field(
        description="Link type, e.g. 'depends on', 'is dependent by', 'works towards'."
    )
    entity: str = Field(description="Identifier of the entity to link to.")


class EntityCreate(RequestBody):
    """Typed request body for ``POST /entities/{type}`` — a ``{fields: {...}}`` envelope.

    Examples:
        >>> EntityCreate(fields=EntityFieldsInput(summary="Q4")).model_dump(exclude_none=True)
        {'fields': {'summary': 'Q4'}}
    """

    fields: EntityFieldsInput = Field(description="Entity settings (summary is required).")


class EntityUpdate(RequestBody):
    """Typed request body for ``PATCH /entities/{type}/{id}`` (edit fields, comment, links).

    Examples:
        >>> EntityUpdate(fields=EntityFieldsInput(summary="New")).model_dump(exclude_none=True)
        {'fields': {'summary': 'New'}}
    """

    fields: EntityFieldsInput | None = Field(default=None, description="Fields to change.")
    comment: str | None = Field(default=None, description="Comment to add with the change.")
    links: list[LinkInput] | None = Field(default=None, description="Links to add.")


class CommentUpdate(RequestBody):
    """Typed request body for ``PATCH …/comments/{comment_id}`` (the id travels in the path).

    Examples:
        >>> CommentUpdate(text="fixed").model_dump(exclude_none=True)
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


class ChecklistItemInput(RequestBody):
    """A checklist item in a create (``[{text}]``) or edit-all (``[{id, text}]``) body.

    Examples:
        >>> ChecklistItemInput(text="step").model_dump(exclude_none=True)
        {'text': 'step'}
    """

    id: str | None = Field(
        default=None, description="Item id (required only in the edit-all body)."
    )
    text: str | None = Field(default=None, description="Item text.")
    checked: bool | None = Field(default=None, description="Whether the item is marked done.")
    assignee: str | None = Field(default=None, description="Assignee user id/login.")
    deadline: DeadlineInput | None = Field(default=None, description="Per-item deadline.")


class ChecklistMove(RequestBody):
    """Typed request body for ``POST …/checklistItems/{id}/_move`` (reorder an item).

    Examples:
        >>> ChecklistMove(before="65f").model_dump(exclude_none=True)
        {'before': '65f'}
    """

    before: str | None = Field(
        default=None, description="Id of the item to insert the moved item before."
    )


class ACLPrincipalsInput(RequestBody):
    """The users/groups/roles for one access level in a permissions-set body.

    Examples:
        >>> ACLPrincipalsInput(roles=["OWNER"]).model_dump(exclude_none=True)
        {'roles': ['OWNER']}
    """

    users: list[str] | None = Field(default=None, description="User ids to grant this level.")
    groups: list[str] | None = Field(default=None, description="Group ids to grant this level.")
    roles: list[str] | None = Field(default=None, description="Roles to grant this level.")


class ACLInput(RequestBody):
    """The ``acl`` block for a permissions-set body (READ / WRITE / GRANT principal sets).

    Examples:
        >>> ACLInput(read=ACLPrincipalsInput(roles=["OWNER"])).model_dump(exclude_none=True)
        {'READ': {'roles': ['OWNER']}}
    """

    read: ACLPrincipalsInput | None = Field(
        default=None,
        validation_alias=AliasChoices("READ", "read"),
        serialization_alias="READ",
        description="Principals to grant READ.",
    )
    write: ACLPrincipalsInput | None = Field(
        default=None,
        validation_alias=AliasChoices("WRITE", "write"),
        serialization_alias="WRITE",
        description="Principals to grant WRITE.",
    )
    grant: ACLPrincipalsInput | None = Field(
        default=None,
        validation_alias=AliasChoices("GRANT", "grant"),
        serialization_alias="GRANT",
        description="Principals to grant GRANT (admin).",
    )


class DirectPermissionsUpdate(RequestBody):
    """Typed request body for ``PATCH …/permissions`` (grant and revoke direct rights).

    Each side maps an access level (READ / WRITE / GRANT) to users, groups and roles; the API
    adds or removes exactly those and keeps the rest. ``permissionSources`` is refused (400).

    Examples:
        >>> DirectPermissionsUpdate(
        ...     grant=ACLInput(read=ACLPrincipalsInput(users=["ann"]))
        ... ).model_dump(exclude_none=True)
        {'grant': {'READ': {'users': ['ann']}}}
    """

    grant: ACLInput | None = Field(default=None, description="Rights to add, by access level.")
    revoke: ACLInput | None = Field(
        default=None, description="Rights to remove, by access level (same shape as ``grant``)."
    )


class BulkChangeValues(RequestBody):
    """The ``values`` object of a bulk-change body (fields + comment + links).

    Examples:
        >>> BulkChangeValues(comment="done").model_dump(exclude_none=True)
        {'comment': 'done'}
    """

    fields: dict[str, Any] | None = Field(
        default=None, description="Field-key → value pairs to apply to every entity."
    )
    comment: str | None = Field(default=None, description="Comment to add to every entity.")
    links: list[LinkInput] | None = Field(default=None, description="Links to add to every entity.")


class BulkChangeUpdate(RequestBody):
    """Typed request body for ``POST …/bulkchange/_update`` (mass-edit entities).

    Examples:
        >>> BulkChangeUpdate(
        ...     meta_entities=["1", "2"], values=BulkChangeValues(comment="done")
        ... ).model_dump(exclude_none=True)
        {'metaEntities': ['1', '2'], 'values': {'comment': 'done'}}
    """

    meta_entities: list[str] = Field(
        alias="metaEntities", description="Identifiers of the entities to update."
    )
    values: BulkChangeValues = Field(description="What to change on every listed entity.")


# --------------------------------------------------------------------------------------------
# Report (issue-report builder)
# --------------------------------------------------------------------------------------------


class ReportSort(RequestBody):
    """A sort clause for a report filter (``parameters.filter.sorts`` element).

    Examples:
        >>> ReportSort(order_by="updated", order_asc=False).model_dump()
        {'orderBy': 'updated', 'orderAsc': False}
    """

    order_by: str = Field(alias="orderBy", description="Issue field to sort the report by.")
    order_asc: bool = Field(
        default=True,
        alias="orderAsc",
        description="Sort direction: true ascending, false descending.",
    )


class ReportFilter(RequestBody):
    """The ``filter`` block of a report — a Tracker Query Language ``query`` plus optional sorts.

    Examples:
        >>> ReportFilter(query="Queue: SUPPORT").model_dump(exclude_none=True)
        {'query': 'Queue: SUPPORT'}
    """

    query: str = Field(description="Issue filter in Tracker Query Language.")
    sorts: list[ReportSort] | None = Field(
        default=None, description="Sort clauses applied to the report."
    )


class ReportParameters(RequestBody):
    """The ``parameters`` block of a report — export settings plus the issue filter.

    Examples:
        >>> ReportParameters(filter=ReportFilter(query="Q"), fields=["key"]).format
        'xlsx'
    """

    type: str = Field(
        default="issueFilterExport", description="Export type. Value: issueFilterExport."
    )
    format: ReportFormat = Field(default="xlsx", description="Export format.")
    filter: ReportFilter = Field(description="Issue filtering parameters for the report.")
    fields: list[str] = Field(description="Issue field keys to include as report columns.")


class ReportFieldsInput(RequestBody):
    """The ``fields`` object of a report create body — the report name plus export ``parameters``.

    Examples:
        >>> params = ReportParameters(filter=ReportFilter(query="Q"), fields=["key"])
        >>> ReportFieldsInput(summary="Export", parameters=params).summary
        'Export'
    """

    summary: str = Field(description="Report name.")
    parameters: ReportParameters = Field(description="Export settings and issue filter.")


class ReportCreate(RequestBody):
    """Typed request body for ``POST /entities/report/`` — a ``{fields: {...}}`` envelope.

    Examples:
        >>> params = ReportParameters(filter=ReportFilter(query="Q"), fields=["key"])
        >>> body = ReportFieldsInput(summary="Export", parameters=params)
        >>> list(ReportCreate(fields=body).model_dump())
        ['fields']
    """

    fields: ReportFieldsInput = Field(description="Report settings (summary + export parameters).")


class EntitySearch(RequestBody):
    """Typed request body for ``POST /entities/{type}/_search``.

    Examples:
        >>> search = EntitySearch.model_validate({"input": "launch", "orderBy": "createdAt"})
        >>> search.model_dump(exclude_none=True)
        {'input': 'launch', 'orderBy': 'createdAt'}
    """

    input: str | None = Field(default=None, description="Substring to find in the entity name.")
    filter: dict[str, Any] | None = Field(
        default=None, description="Field name → value the entities must have."
    )
    order_by: str | None = Field(
        default=None, alias="orderBy", description="Key of the field to sort by."
    )
    order_asc: bool | None = Field(
        default=None,
        alias="orderAsc",
        description="Sort ascending; needs ``order_by``.",
    )
    root_only: bool | None = Field(
        default=None, alias="rootOnly", description="Only entities with no parent."
    )


class PermissionsUpdate(RequestBody):
    """Typed request body for ``PATCH …/extendedPermissions``: rights to grant and to revoke.

    Examples:
        >>> change = PermissionsUpdate.model_validate(
        ...     {"acl": {"grant": {"READ": {"users": ["7"]}}}}
        ... )
        >>> change.model_dump(exclude_none=True)
        {'acl': {'grant': {'READ': {'users': ['7']}}}}
    """

    acl: DirectPermissionsUpdate = Field(
        description="``grant`` and ``revoke``, each an access level → users, groups and roles."
    )
