"""`tracker entities` commands — projects / portfolios / goals and their sub-resources.

Core verbs live on the top-level app (``get``/``create``/``update``/``delete``/``search``/
``events-list``/``permissions-get``/``set-permissions``/``bulk-update``); comments, checklists,
links and attachments are nested sub-apps. Commands return their results; the one binary
download (``attachments download``) returns a ``BinaryResult``.
"""

from __future__ import annotations

import enum
from typing import Annotated, Any

import typer

from ycli.cli.fields import parse_fields
from ycli.cli.output import BinaryResult
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.entities.models import (
    Acl,
    AclInput,
    Attachment,
    BulkChangeOperation,
    BulkChangeUpdate,
    BulkChangeValues,
    ChecklistItemInput,
    ChecklistMove,
    Comment,
    CommentUpdate,
    DirectPermissionsUpdate,
    Entity,
    EntityCreate,
    EntityEvent,
    EntityFieldsInput,
    EntitySearch,
    EntityUpdate,
    ExtendedPermissions,
    Link,
    LinkInput,
    ParentEntityInput,
    PermissionsUpdate,
    ReportCreate,
    ReportFieldsInput,
    ReportFilter,
    ReportParameters,
)
from ycli.yandex.tracker.models import CommentCreate, DeadlineInput
from ycli.yandex.tracker.typedefs import (
    AddToFollowersOpt,
    ExpandOpt,
    NotifyAuthorOpt,
    NotifyOpt,
    ReplyFieldsOpt,
)


class EntityType(enum.StrEnum):
    """The three entity types the Entities API unifies, plus issue reports (search only)."""

    project = "project"
    portfolio = "portfolio"
    goal = "goal"
    report = "report"  # documented for search only (issue reports)


app = typer.Typer(
    name="entities", help="Tracker projects, portfolios and goals.", no_args_is_help=True
)

TypeArg = Annotated[
    EntityType,
    typer.Argument(
        metavar="TYPE", help="Entity type: project, portfolio or goal (report: search only)."
    ),
]
IdArg = Annotated[str, typer.Argument(metavar="ID", help="Entity id (or shortId).")]
FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Extra fields entry key=value (JSON-coerced; repeatable)."),
]


def _fields_body(
    summary: str | None,
    description: str | None,
    lead: str | None,
    author: str | None,
    status: str | None,
    start: str | None,
    end: str | None,
    parent: str | None,
    team_user: list[str] | None,
    tag: list[str] | None,
    field: list[str] | None,
) -> dict[str, Any]:
    """Assemble the ``fields`` object (API alias keys) from CLI options, merging ``--field`` extras.

    Builds the typed :class:`EntityFieldsInput` (the single source of truth for every API alias)
    and dumps it, so the CLI never hand-assembles the aliased dict; ``--field key=value`` still
    overrides or adds arbitrary field parameters (last write wins).
    """
    fields = EntityFieldsInput(
        summary=summary,
        description=description,
        lead=lead,
        author=author,
        entityStatus=status,
        start=start,
        end=end,
        parentEntity=ParentEntityInput(primary=parent) if parent is not None else None,
        teamUsers=team_user or None,
        tags=tag or None,
    ).model_dump(exclude_none=True)
    fields |= parse_fields(field)
    return fields


@app.command()
def get(
    type_: TypeArg,
    entity_id: IdArg,
    expand: Annotated[str | None, typer.Option(help="Extra info, e.g. attachments.")] = None,
    fields: Annotated[
        str | None, typer.Option(help="Comma-separated extra fields to include.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Print a single entity (project/portfolio/goal) by ID."""
    return tracker.entities.get(type_.value, entity_id, expand=expand, fields=fields)


@app.command()
def create(
    type_: TypeArg,
    summary: Annotated[str, typer.Option(help="Entity name (required).")],
    description: Annotated[str | None, typer.Option(help="Description.")] = None,
    lead: Annotated[str | None, typer.Option(help="Responsible user id/login.")] = None,
    author: Annotated[str | None, typer.Option(help="Author user id/login.")] = None,
    status: Annotated[str | None, typer.Option("--status", help="entityStatus key to set.")] = None,
    start: Annotated[
        str | None, typer.Option(help="Start date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    ] = None,
    end: Annotated[
        str | None, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    ] = None,
    parent: Annotated[str | None, typer.Option(help="Primary parent portfolio/goal id.")] = None,
    team_user: Annotated[
        list[str] | None, typer.Option("--team-user", help="Participant id/login (repeatable).")
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    field: FieldOpt = None,
    fields: ReplyFieldsOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Create an entity (POST /entities/TYPE). summary is required; other fields optional."""
    fields_body = _fields_body(
        summary, description, lead, author, status, start, end, parent, team_user, tag, field
    )
    body = EntityCreate.model_validate({"fields": fields_body})
    return tracker.entities.create(type_.value, body=body, fields=fields)


@app.command()
def update(
    type_: TypeArg,
    entity_id: IdArg,
    summary: Annotated[str | None, typer.Option(help="New name.")] = None,
    description: Annotated[str | None, typer.Option(help="New description.")] = None,
    lead: Annotated[str | None, typer.Option(help="New responsible user id/login.")] = None,
    author: Annotated[str | None, typer.Option(help="New author user id/login.")] = None,
    status: Annotated[str | None, typer.Option("--status", help="New entityStatus key.")] = None,
    start: Annotated[str | None, typer.Option(help="New start date.")] = None,
    end: Annotated[str | None, typer.Option(help="New deadline date.")] = None,
    parent: Annotated[
        str | None, typer.Option(help="New primary parent portfolio/goal id.")
    ] = None,
    team_user: Annotated[
        list[str] | None, typer.Option("--team-user", help="Participant id/login (repeatable).")
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    comment: Annotated[str | None, typer.Option(help="Comment to add with the change.")] = None,
    field: FieldOpt = None,
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Edit entity ID (PATCH /entities/TYPE/ID) — only supplied fields are sent."""
    fields_body = _fields_body(
        summary, description, lead, author, status, start, end, parent, team_user, tag, field
    )
    body = EntityUpdate.model_validate({"fields": fields_body or None, "comment": comment})
    return tracker.entities.update(type_.value, entity_id, body=body, expand=expand, fields=fields)


@app.command()
def delete(
    type_: TypeArg,
    entity_id: IdArg,
    with_board: Annotated[
        bool, typer.Option("--with-board", help="Also delete the entity's board.")
    ] = False,
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete entity ID (DELETE /entities/TYPE/ID)."""
    tracker.entities.delete(type_.value, entity_id, with_board=with_board or None)
    return Ack.deleted(type_.value, entity_id)


@app.command()
def search(
    type_: TypeArg,
    input_: Annotated[
        str | None, typer.Option("--input", help="Substring in the entity name.")
    ] = None,
    filter_: Annotated[
        list[str] | None,
        typer.Option("--filter", help="Filter key=value (JSON-coerced; repeatable)."),
    ] = None,
    order_by: Annotated[
        str | None, typer.Option("--order-by", help="Field key to sort by.")
    ] = None,
    order_asc: Annotated[bool, typer.Option("--order-asc", help="Sort ascending.")] = False,
    root_only: Annotated[
        bool, typer.Option("--root-only", help="Only top-level entities.")
    ] = False,
    fields: Annotated[
        str | None, typer.Option(help="Comma-separated extra fields to include.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Entity]:
    """Search entities of TYPE (POST /entities/TYPE/_search)."""
    if order_asc and order_by is None:
        raise typer.BadParameter("needs --order-by", param_hint="--order-asc")
    body = EntitySearch.model_validate(
        {
            "input": input_,
            "filter": parse_fields(filter_) or None,
            "orderBy": order_by,
            "orderAsc": order_asc if order_by is not None else None,
            "rootOnly": root_only or None,
        }
    )
    return tracker.entities.search(type_.value, body, fields=fields)


@app.command()
def events_list(
    type_: TypeArg,
    entity_id: IdArg,
    limit: Annotated[int | None, typer.Option(help="Max events (default: all).")] = None,
    selected: Annotated[str | None, typer.Option(help="Event id to build the list around.")] = None,
    new_events_on_top: Annotated[
        bool | None,
        typer.Option("--new-events-on-top/--no-new-events-on-top", help="Newest events first."),
    ] = None,
    direction: Annotated[
        str | None, typer.Option(help="forward (the default) or backward.")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[EntityEvent]:
    """Print an entity's event history (GET …/events/_relative, auto-paginated)."""
    return tracker.entities.events_list(
        type_.value,
        entity_id,
        limit=limit,
        selected=selected,
        new_events_on_top=new_events_on_top,
        direction=direction,
    )


@app.command()
def permissions_get(
    type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient
) -> ExtendedPermissions:
    """Print an entity's access settings (GET …/extendedPermissions)."""
    return tracker.entities.permissions_get(type_.value, entity_id)


@app.command("set-permissions")
def set_permissions(
    type_: TypeArg,
    entity_id: IdArg,
    field: Annotated[
        list[str] | None,
        typer.Option(
            "--acl",
            help="ACL change ACTION=<json> where ACTION is grant or revoke, e.g. "
            'grant={"READ":{"users":["8000000000000002"]}} (repeatable).',
        ),
    ] = None,
    *,
    tracker: TrackerClient,
) -> ExtendedPermissions:
    """Set an entity's access settings (PATCH …/extendedPermissions).

    The API accepts only ``grant`` / ``revoke`` actions, each mapping an access level
    (READ/WRITE/GRANT) to users/groups/roles, e.g.
    ``--acl 'grant={"READ":{"users":["8000000000000002"]}}'``.
    """
    body = PermissionsUpdate.model_validate({"acl": parse_fields(field)})
    return tracker.entities.set_permissions(type_.value, entity_id, body=body)


@app.command("direct-permissions-get")
def direct_permissions_get(type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient) -> Acl:
    """Print an entity's direct READ/WRITE/GRANT rights, no inheritance (GET …/permissions)."""
    return tracker.entities.direct_permissions_get(type_.value, entity_id)


@app.command("set-direct-permissions")
def set_direct_permissions(
    type_: TypeArg,
    entity_id: IdArg,
    grant: Annotated[
        str | None,
        typer.Option(help='Rights to add as JSON, e.g. \'{"READ":{"users":["ann"]}}\'.'),
    ] = None,
    revoke: Annotated[
        str | None,
        typer.Option(help='Rights to remove as JSON, e.g. \'{"GRANT":{"roles":["OWNER"]}}\'.'),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Acl:
    """Grant and revoke an entity's direct rights (PATCH …/permissions); pass --grant/--revoke."""
    if grant is None and revoke is None:
        raise typer.BadParameter("pass --grant and/or --revoke")
    body = DirectPermissionsUpdate(
        grant=AclInput.model_validate_json(grant) if grant is not None else None,
        revoke=AclInput.model_validate_json(revoke) if revoke is not None else None,
    )
    return tracker.entities.set_direct_permissions(type_.value, entity_id, body)


@app.command()
def bulk_update(
    type_: TypeArg,
    entity: Annotated[list[str], typer.Option("--entity", help="Entity id (repeatable).")],
    comment: Annotated[str | None, typer.Option(help="Comment to add to every entity.")] = None,
    field: FieldOpt = None,
    *,
    tracker: TrackerClient,
) -> BulkChangeOperation:
    """Mass-edit entities (POST …/bulkchange/_update) — returns the async operation handle."""
    values = BulkChangeValues(fields=parse_fields(field) or None, comment=comment)
    body = BulkChangeUpdate.model_validate({"metaEntities": entity, "values": values})
    return tracker.entities.bulk_update(type_.value, body=body)


@app.command("bulk-status-get")
def bulk_status_get(
    operation_id: Annotated[str, typer.Argument(metavar="OPERATION_ID", help="Bulk-change id.")],
    *,
    tracker: TrackerClient,
) -> BulkChangeOperation:
    """Print a bulk-change operation's status (GET /bulkchange/OPERATION_ID)."""
    return tracker.entities.bulk_status_get(operation_id)


@app.command("create-report")
def create_report(
    summary: Annotated[str, typer.Option(help="Report name (required).")],
    query: Annotated[str, typer.Option(help="Issue filter in Tracker Query Language (required).")],
    format_: Annotated[
        str, typer.Option("--format", help="Export format: xlsx, xml or csv.")
    ] = "xlsx",
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-F", help="Issue field key to include as a column (repeatable)."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Build an issue report (POST /entities/report/) from a TQL query and column fields."""
    body = ReportCreate(
        fields=ReportFieldsInput(
            summary=summary,
            parameters=ReportParameters(
                format=format_, filter=ReportFilter(query=query), fields=field or []
            ),
        )
    )
    return tracker.entities.create_report(body=body)


# --------------------------------------------------------------------------------------------
# comments sub-app
# --------------------------------------------------------------------------------------------

comments_app = typer.Typer(name="comments", help="Entity comments.", no_args_is_help=True)
app.add_typer(comments_app)

CommentIdArg = Annotated[str, typer.Argument(metavar="COMMENT_ID", help="Comment id.")]


@comments_app.command("list")
def comments_list(
    type_: TypeArg,
    entity_id: IdArg,
    all_: Annotated[
        bool, typer.Option("--all", help="Drain the paginated (_relative) listing.")
    ] = False,
    limit: Annotated[
        int | None, typer.Option(help="Max comments when --all (default: all).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> ItemList[Comment]:
    """List comments on an entity (GET …/comments; --all uses …/comments/_relative)."""
    if all_:
        return tracker.entities.comments_relative_list(type_.value, entity_id, limit=limit)
    return tracker.entities.comments_list(type_.value, entity_id)


@comments_app.command("get")
def comments_get(
    type_: TypeArg, entity_id: IdArg, comment_id: CommentIdArg, *, tracker: TrackerClient
) -> Comment:
    """Get one comment on an entity (GET …/comments/COMMENT_ID)."""
    return tracker.entities.comments_get(type_.value, entity_id, comment_id)


@comments_app.command("create")
def comments_create(
    type_: TypeArg,
    entity_id: IdArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
    summon: Annotated[
        list[str] | None, typer.Option("--summon", help="User to summon (repeatable).")
    ] = None,
    expand: ExpandOpt = None,
    add_to_followers: AddToFollowersOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Comment:
    """Add a comment to an entity (POST …/comments)."""
    body = CommentCreate(text=text, summonees=summon or None)
    return tracker.entities.comments_create(
        type_.value,
        entity_id,
        body=body,
        expand=expand,
        is_add_to_followers=add_to_followers,
        notify=notify,
        notify_author=notify_author,
    )


@comments_app.command("update")
def comments_update(
    type_: TypeArg,
    entity_id: IdArg,
    comment_id: CommentIdArg,
    text: Annotated[str, typer.Option(help="New comment text.")],
    expand: ExpandOpt = None,
    add_to_followers: AddToFollowersOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Comment:
    """Edit a comment on an entity (PATCH …/comments/COMMENT_ID)."""
    body = CommentUpdate(text=text)
    return tracker.entities.comments_update(
        type_.value,
        entity_id,
        comment_id,
        body=body,
        expand=expand,
        is_add_to_followers=add_to_followers,
        notify=notify,
        notify_author=notify_author,
    )


@comments_app.command("delete")
def comments_delete(
    type_: TypeArg,
    entity_id: IdArg,
    comment_id: CommentIdArg,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete a comment from an entity (DELETE …/comments/COMMENT_ID)."""
    tracker.entities.comments_delete(
        type_.value, entity_id, comment_id, notify=notify, notify_author=notify_author
    )
    return Ack.deleted("comment", comment_id, on=f"{type_.value} {entity_id}")


# --------------------------------------------------------------------------------------------
# checklists sub-app
# --------------------------------------------------------------------------------------------

checklists_app = typer.Typer(name="checklists", help="Entity checklists.", no_args_is_help=True)
app.add_typer(checklists_app)

ItemIdArg = Annotated[str, typer.Argument(metavar="ITEM_ID", help="Checklist item id.")]


def _item_input(
    text: str | None,
    checked: bool | None,
    assignee: str | None,
    deadline: str | None,
    item_id: str | None = None,
) -> ChecklistItemInput:
    """Build a typed checklist item from CLI options."""
    return ChecklistItemInput(
        id=item_id,
        text=text,
        checked=checked,
        assignee=assignee,
        deadline=DeadlineInput(date=deadline) if deadline is not None else None,
    )


@checklists_app.command("create")
def checklists_create(
    type_: TypeArg,
    entity_id: IdArg,
    text: Annotated[
        list[str], typer.Option("--text", help="Item text (repeatable — one per item).")
    ],
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Add checklist items to an entity (POST …/checklistItems)."""
    items = ItemList[ChecklistItemInput]([ChecklistItemInput(text=t) for t in text])
    return tracker.entities.checklists_create(
        type_.value,
        entity_id,
        body=items,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@checklists_app.command("update")
def checklists_update(
    type_: TypeArg,
    entity_id: IdArg,
    item: Annotated[
        list[str],
        typer.Option("--item", help="Item as id=text (repeatable — replaces the whole checklist)."),
    ],
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Replace the whole checklist (PATCH …/checklistItems) from repeated --item id=text.

    The text is sent verbatim — never JSON-coerced — and only the first ``=`` splits:
    ``--item 5f=true`` sends the text ``true``, ``--item 6a=a=b`` sends ``a=b``.
    """
    inputs: list[ChecklistItemInput] = []
    for raw in item:
        item_id, separator, text = raw.partition("=")
        if not separator:
            raise typer.BadParameter(f"must be id=text, got {raw!r}", param_hint="--item")
        inputs.append(ChecklistItemInput(id=item_id, text=text))
    items = ItemList[ChecklistItemInput](inputs)
    return tracker.entities.checklists_update(
        type_.value,
        entity_id,
        body=items,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@checklists_app.command("update-item")
def checklists_update_item(
    type_: TypeArg,
    entity_id: IdArg,
    item_id: ItemIdArg,
    text: Annotated[str | None, typer.Option(help="New item text.")] = None,
    checked: Annotated[
        bool | None, typer.Option("--checked/--no-checked", help="Mark the item done or not done.")
    ] = None,
    assignee: Annotated[str | None, typer.Option(help="Assignee user id/login.")] = None,
    deadline: Annotated[
        str | None, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    ] = None,
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Edit a single checklist item (PATCH …/checklistItems/ITEM_ID)."""
    body = _item_input(text, checked, assignee, deadline)
    return tracker.entities.checklists_update_item(
        type_.value,
        entity_id,
        item_id,
        body=body,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@checklists_app.command("delete-item")
def checklists_delete_item(
    type_: TypeArg,
    entity_id: IdArg,
    item_id: ItemIdArg,
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Remove one checklist item (DELETE …/checklistItems/ITEM_ID)."""
    return tracker.entities.checklists_delete_item(
        type_.value,
        entity_id,
        item_id,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@checklists_app.command("delete")
def checklists_delete(
    type_: TypeArg,
    entity_id: IdArg,
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Clear the whole checklist (DELETE …/checklistItems)."""
    return tracker.entities.checklists_delete(
        type_.value,
        entity_id,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@checklists_app.command("move")
def checklists_move(
    type_: TypeArg,
    entity_id: IdArg,
    item_id: ItemIdArg,
    before: Annotated[
        str | None, typer.Option(help="Item id to insert the moved item before.")
    ] = None,
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Reorder a checklist item (POST …/checklistItems/ITEM_ID/_move)."""
    body = ChecklistMove(before=before)
    return tracker.entities.checklists_move(
        type_.value,
        entity_id,
        item_id,
        body=body,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


# --------------------------------------------------------------------------------------------
# links sub-app
# --------------------------------------------------------------------------------------------

links_app = typer.Typer(name="links", help="Entity links.", no_args_is_help=True)
app.add_typer(links_app)


@links_app.command("list")
def links_list(type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient) -> ItemList[Link]:
    """List an entity's links to other entities (GET …/links)."""
    return tracker.entities.links_list(type_.value, entity_id)


@links_app.command("create")
def links_create(
    type_: TypeArg,
    entity_id: IdArg,
    relationship: Annotated[str, typer.Option(help="Link type, e.g. relates, depends on.")],
    entity: Annotated[str, typer.Option(help="Id of the entity to link to.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Create a link between entities (POST …/links)."""
    body = LinkInput(relationship=relationship, entity=entity)
    tracker.entities.links_create(type_.value, entity_id, body=body)
    return Ack.linked(type_.value, entity_id, entity, relationship)


@links_app.command("delete")
def links_delete(
    type_: TypeArg,
    entity_id: IdArg,
    right: Annotated[str, typer.Argument(metavar="RIGHT", help="Id of the entity to unlink.")],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete a link (DELETE …/links?right=RIGHT)."""
    tracker.entities.links_delete(type_.value, entity_id, right)
    return Ack.unlinked(type_.value, entity_id, right)


# --------------------------------------------------------------------------------------------
# attachments sub-app
# --------------------------------------------------------------------------------------------

attachments_app = typer.Typer(name="attachments", help="Entity attachments.", no_args_is_help=True)
app.add_typer(attachments_app)

FileIdArg = Annotated[str, typer.Argument(metavar="FILE_ID", help="Attachment file id.")]


@attachments_app.command("list")
def attachments_list(
    type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient
) -> ItemList[Attachment]:
    """List files attached to an entity (GET …/attachments)."""
    return tracker.entities.attachments_list(type_.value, entity_id)


@attachments_app.command("get")
def attachments_get(
    type_: TypeArg, entity_id: IdArg, file_id: FileIdArg, *, tracker: TrackerClient
) -> Attachment:
    """Get one attachment's metadata (GET …/attachments/FILE_ID)."""
    return tracker.entities.attachments_get(type_.value, entity_id, file_id)


@attachments_app.command("download")
def attachments_download(
    file_id: FileIdArg,
    filename: Annotated[str, typer.Argument(metavar="FILENAME", help="Attachment file name.")],
    output: Annotated[
        str | None,
        typer.Option("--output", "-O", help="Write to this path; omit or '-' for stdout."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> BinaryResult:
    """Download an attachment's raw bytes to --output (or stdout). Binary is CLI/SDK-only."""
    return BinaryResult(tracker.entities.attachments_download(file_id, filename), output)


@attachments_app.command("attach")
def attachments_attach(
    type_: TypeArg,
    entity_id: IdArg,
    temp_file_id: Annotated[str, typer.Argument(metavar="TEMP_FILE_ID", help="Temp file id.")],
    expand: ExpandOpt = None,
    fields: ReplyFieldsOpt = None,
    notify: NotifyOpt = None,
    notify_author: NotifyAuthorOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Attach a previously uploaded temp file to an entity (POST …/attachments/TEMP_FILE_ID)."""
    return tracker.entities.attachments_attach(
        type_.value,
        entity_id,
        temp_file_id,
        expand=expand,
        fields=fields,
        notify=notify,
        notify_author=notify_author,
    )


@attachments_app.command("delete")
def attachments_delete(
    type_: TypeArg, entity_id: IdArg, file_id: FileIdArg, *, tracker: TrackerClient
) -> Ack:
    """Detach a file from an entity (DELETE …/attachments/FILE_ID; empty response body)."""
    tracker.entities.attachments_delete(type_.value, entity_id, file_id)
    return Ack.deleted("attachment", file_id, on=f"{type_.value} {entity_id}")
