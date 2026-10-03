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

from ycli.cli.aliases import deprecated_alias
from ycli.cli.fields import parse_fields
from ycli.cli.output import BinaryResult
from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.entities.models import (
    Acl,
    AclInput,
    Attachment,
    AttachmentList,
    BulkChangeOperation,
    BulkChangeValues,
    ChecklistItemInput,
    ChecklistItemsInput,
    ChecklistMove,
    Comment,
    CommentList,
    CommentUpdate,
    DirectPermissionsUpdate,
    Entity,
    EntityEventList,
    EntityFieldsInput,
    EntityList,
    ExtendedPermissions,
    LinkInput,
    LinkList,
    ParentEntityInput,
    ReportCreate,
    ReportFieldsInput,
    ReportFilter,
    ReportParameters,
)
from ycli.yandex.tracker.models import CommentCreate, DeadlineInput


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
    summary: str,
    description: str,
    lead: str,
    author: str,
    status: str,
    start: str,
    end: str,
    parent: str,
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
        summary=summary or None,
        description=description or None,
        lead=lead or None,
        author=author or None,
        entityStatus=status or None,
        start=start or None,
        end=end or None,
        parentEntity=ParentEntityInput(primary=parent) if parent else None,
        teamUsers=team_user or None,
        tags=tag or None,
    ).model_dump(by_alias=True, exclude_none=True)
    fields |= parse_fields(field)
    return fields


@app.command()
def get(
    type_: TypeArg,
    entity_id: IdArg,
    expand: Annotated[str, typer.Option(help="Extra info, e.g. attachments.")] = "",
    fields: Annotated[str, typer.Option(help="Comma-separated extra fields to include.")] = "",
    *,
    tracker: TrackerClient,
) -> Entity:
    """Print a single entity (project/portfolio/goal) by ID."""
    return tracker.entities.get(
        type_.value, entity_id, expand=expand or None, fields=fields or None
    )


@app.command()
def create(
    type_: TypeArg,
    summary: Annotated[str, typer.Option(help="Entity name (required).")],
    description: Annotated[str, typer.Option(help="Description.")] = "",
    lead: Annotated[str, typer.Option(help="Responsible user id/login.")] = "",
    author: Annotated[str, typer.Option(help="Author user id/login.")] = "",
    status: Annotated[str, typer.Option("--status", help="entityStatus key to set.")] = "",
    start: Annotated[str, typer.Option(help="Start date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")] = "",
    end: Annotated[str, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")] = "",
    parent: Annotated[str, typer.Option(help="Primary parent portfolio/goal id.")] = "",
    team_user: Annotated[
        list[str] | None, typer.Option("--team-user", help="Participant id/login (repeatable).")
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    field: FieldOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Create an entity (POST /entities/TYPE). summary is required; other fields optional."""
    fields_body = _fields_body(
        summary, description, lead, author, status, start, end, parent, team_user, tag, field
    )
    body = {"fields": fields_body}
    return tracker.entities.create(type_.value, body=body)


@deprecated_alias(app, "edit")
@app.command()
def update(
    type_: TypeArg,
    entity_id: IdArg,
    summary: Annotated[str, typer.Option(help="New name.")] = "",
    description: Annotated[str, typer.Option(help="New description.")] = "",
    lead: Annotated[str, typer.Option(help="New responsible user id/login.")] = "",
    author: Annotated[str, typer.Option(help="New author user id/login.")] = "",
    status: Annotated[str, typer.Option("--status", help="New entityStatus key.")] = "",
    start: Annotated[str, typer.Option(help="New start date.")] = "",
    end: Annotated[str, typer.Option(help="New deadline date.")] = "",
    parent: Annotated[str, typer.Option(help="New primary parent portfolio/goal id.")] = "",
    team_user: Annotated[
        list[str] | None, typer.Option("--team-user", help="Participant id/login (repeatable).")
    ] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable).")] = None,
    comment: Annotated[str, typer.Option(help="Comment to add with the change.")] = "",
    field: FieldOpt = None,
    *,
    tracker: TrackerClient,
) -> Entity:
    """Edit entity ID (PATCH /entities/TYPE/ID) — only supplied fields are sent."""
    fields_body = _fields_body(
        summary, description, lead, author, status, start, end, parent, team_user, tag, field
    )
    body: dict[str, Any] = {}
    if fields_body:
        body["fields"] = fields_body
    if comment:
        body["comment"] = comment
    return tracker.entities.edit(type_.value, entity_id, body=body)


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
    input_: Annotated[str, typer.Option("--input", help="Substring in the entity name.")] = "",
    filter_: Annotated[
        list[str] | None,
        typer.Option("--filter", help="Filter key=value (JSON-coerced; repeatable)."),
    ] = None,
    order_by: Annotated[str, typer.Option("--order-by", help="Field key to sort by.")] = "",
    order_asc: Annotated[bool, typer.Option("--order-asc", help="Sort ascending.")] = False,
    root_only: Annotated[
        bool, typer.Option("--root-only", help="Only top-level entities.")
    ] = False,
    fields: Annotated[str, typer.Option(help="Comma-separated extra fields to include.")] = "",
    *,
    tracker: TrackerClient,
) -> EntityList:
    """Search entities of TYPE (POST /entities/TYPE/_search)."""
    if order_asc and not order_by:
        raise typer.BadParameter("needs --order-by", param_hint="--order-asc")
    body: dict[str, Any] = {}
    if input_:
        body["input"] = input_
    if filter_:
        body["filter"] = parse_fields(filter_)
    if order_by:
        body["orderBy"] = order_by
        body["orderAsc"] = order_asc
    if root_only:
        body["rootOnly"] = True
    return tracker.entities.search(type_.value, body, fields=fields or None)


@deprecated_alias(app, "history")
@app.command()
def events_list(
    type_: TypeArg,
    entity_id: IdArg,
    limit: Annotated[int, typer.Option(help="Max events (0 = all).")] = 0,
    *,
    tracker: TrackerClient,
) -> EntityEventList:
    """Print an entity's event history (GET …/events/_relative, auto-paginated)."""
    return tracker.entities.history(type_.value, entity_id, limit=limit or None)


@deprecated_alias(app, "permissions")
@app.command()
def permissions_get(
    type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient
) -> ExtendedPermissions:
    """Print an entity's access settings (GET …/extendedPermissions)."""
    return tracker.entities.permissions(type_.value, entity_id)


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
    body = {"acl": parse_fields(field)}
    return tracker.entities.set_permissions(type_.value, entity_id, body=body)


@deprecated_alias(app, "direct-permissions")
@app.command("direct-permissions-get")
def direct_permissions_get(type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient) -> Acl:
    """Print an entity's direct READ/WRITE/GRANT rights, no inheritance (GET …/permissions)."""
    return tracker.entities.direct_permissions(type_.value, entity_id)


@app.command("set-direct-permissions")
def set_direct_permissions(
    type_: TypeArg,
    entity_id: IdArg,
    grant: Annotated[
        str,
        typer.Option(help='Rights to add as JSON, e.g. \'{"READ":{"users":["ann"]}}\'.'),
    ] = "",
    revoke: Annotated[
        str,
        typer.Option(help='Rights to remove as JSON, e.g. \'{"GRANT":{"roles":["OWNER"]}}\'.'),
    ] = "",
    *,
    tracker: TrackerClient,
) -> Acl:
    """Grant and revoke an entity's direct rights (PATCH …/permissions); pass --grant/--revoke."""
    if not (grant or revoke):
        raise typer.BadParameter("pass --grant and/or --revoke")
    body = DirectPermissionsUpdate(
        grant=AclInput.model_validate_json(grant) if grant else None,
        revoke=AclInput.model_validate_json(revoke) if revoke else None,
    )
    return tracker.entities.set_direct_permissions(type_.value, entity_id, body)


@deprecated_alias(app, "bulk")
@app.command()
def bulk_update(
    type_: TypeArg,
    entity: Annotated[list[str], typer.Option("--entity", help="Entity id (repeatable).")],
    comment: Annotated[str, typer.Option(help="Comment to add to every entity.")] = "",
    field: FieldOpt = None,
    *,
    tracker: TrackerClient,
) -> BulkChangeOperation:
    """Mass-edit entities (POST …/bulkchange/_update) — returns the async operation handle."""
    values = BulkChangeValues(
        fields=parse_fields(field) or None, comment=comment or None
    ).model_dump(by_alias=True, exclude_none=True)
    body = {"metaEntities": entity, "values": values}
    return tracker.entities.bulk_update(type_.value, body=body)


@deprecated_alias(app, "bulk-status")
@app.command("bulk-status-get")
def bulk_status_get(
    operation_id: Annotated[str, typer.Argument(metavar="OPERATION_ID", help="Bulk-change id.")],
    *,
    tracker: TrackerClient,
) -> BulkChangeOperation:
    """Print a bulk-change operation's status (GET /bulkchange/OPERATION_ID)."""
    return tracker.entities.bulk_status(operation_id)


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
    ).model_dump(by_alias=True, exclude_none=True)
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
    limit: Annotated[int, typer.Option(help="Max comments when --all (0 = all).")] = 0,
    *,
    tracker: TrackerClient,
) -> CommentList:
    """List comments on an entity (GET …/comments; --all uses …/comments/_relative)."""
    if all_:
        return tracker.entities.comments_relative(type_.value, entity_id, limit=limit or None)
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
    *,
    tracker: TrackerClient,
) -> Comment:
    """Add a comment to an entity (POST …/comments)."""
    body = CommentCreate(text=text, summonees=summon or None).model_dump(
        by_alias=True, exclude_none=True
    )
    return tracker.entities.comments_create(type_.value, entity_id, body=body)


@deprecated_alias(comments_app, "edit")
@comments_app.command("update")
def comments_update(
    type_: TypeArg,
    entity_id: IdArg,
    comment_id: CommentIdArg,
    text: Annotated[str, typer.Option(help="New comment text.")],
    *,
    tracker: TrackerClient,
) -> Comment:
    """Edit a comment on an entity (PATCH …/comments/COMMENT_ID)."""
    body = CommentUpdate(text=text).model_dump(by_alias=True, exclude_none=True)
    return tracker.entities.comments_edit(type_.value, entity_id, comment_id, body=body)


@comments_app.command("delete")
def comments_delete(
    type_: TypeArg, entity_id: IdArg, comment_id: CommentIdArg, *, tracker: TrackerClient
) -> Ack:
    """Delete a comment from an entity (DELETE …/comments/COMMENT_ID)."""
    tracker.entities.comments_delete(type_.value, entity_id, comment_id)
    return Ack.deleted("comment", comment_id, on=f"{type_.value} {entity_id}")


# --------------------------------------------------------------------------------------------
# checklists sub-app
# --------------------------------------------------------------------------------------------

checklists_app = typer.Typer(name="checklists", help="Entity checklists.", no_args_is_help=True)
app.add_typer(checklists_app)

ItemIdArg = Annotated[str, typer.Argument(metavar="ITEM_ID", help="Checklist item id.")]


def _item_input(
    text: str, checked: bool | None, assignee: str, deadline: str, item_id: str = ""
) -> ChecklistItemInput:
    """Build a typed checklist item from CLI options."""
    return ChecklistItemInput(
        id=item_id or None,
        text=text or None,
        checked=checked,
        assignee=assignee or None,
        deadline=DeadlineInput(date=deadline) if deadline else None,
    )


@checklists_app.command("create")
def checklists_create(
    type_: TypeArg,
    entity_id: IdArg,
    text: Annotated[
        list[str], typer.Option("--text", help="Item text (repeatable — one per item).")
    ],
    *,
    tracker: TrackerClient,
) -> Entity:
    """Add checklist items to an entity (POST …/checklistItems)."""
    items = ChecklistItemsInput([ChecklistItemInput(text=t) for t in text]).model_dump(
        by_alias=True, exclude_none=True
    )
    return tracker.entities.checklists_create(type_.value, entity_id, body=items)


@deprecated_alias(checklists_app, "edit")
@checklists_app.command("update")
def checklists_update(
    type_: TypeArg,
    entity_id: IdArg,
    item: Annotated[
        list[str],
        typer.Option("--item", help="Item as id=text (repeatable — replaces the whole checklist)."),
    ],
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
    items = ChecklistItemsInput(inputs).model_dump(by_alias=True, exclude_none=True)
    return tracker.entities.checklists_edit(type_.value, entity_id, body=items)


@deprecated_alias(checklists_app, "edit-item")
@checklists_app.command("update-item")
def checklists_update_item(
    type_: TypeArg,
    entity_id: IdArg,
    item_id: ItemIdArg,
    text: Annotated[str, typer.Option(help="New item text.")] = "",
    checked: Annotated[
        bool | None, typer.Option("--checked/--no-checked", help="Mark the item done or not done.")
    ] = None,
    assignee: Annotated[str, typer.Option(help="Assignee user id/login.")] = "",
    deadline: Annotated[
        str, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    ] = "",
    *,
    tracker: TrackerClient,
) -> Entity:
    """Edit a single checklist item (PATCH …/checklistItems/ITEM_ID)."""
    body = _item_input(text, checked, assignee, deadline).model_dump(
        by_alias=True, exclude_none=True
    )
    return tracker.entities.checklists_edit_item(type_.value, entity_id, item_id, body=body)


@checklists_app.command("delete-item")
def checklists_delete_item(
    type_: TypeArg, entity_id: IdArg, item_id: ItemIdArg, *, tracker: TrackerClient
) -> Entity:
    """Remove one checklist item (DELETE …/checklistItems/ITEM_ID)."""
    return tracker.entities.checklists_delete_item(type_.value, entity_id, item_id)


@checklists_app.command("delete")
def checklists_delete(type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient) -> Entity:
    """Clear the whole checklist (DELETE …/checklistItems)."""
    return tracker.entities.checklists_delete(type_.value, entity_id)


@checklists_app.command("move")
def checklists_move(
    type_: TypeArg,
    entity_id: IdArg,
    item_id: ItemIdArg,
    before: Annotated[str, typer.Option(help="Item id to insert the moved item before.")] = "",
    *,
    tracker: TrackerClient,
) -> Entity:
    """Reorder a checklist item (POST …/checklistItems/ITEM_ID/_move)."""
    body = ChecklistMove(before=before or None).model_dump(by_alias=True, exclude_none=True)
    return tracker.entities.checklists_move(type_.value, entity_id, item_id, body=body)


# --------------------------------------------------------------------------------------------
# links sub-app
# --------------------------------------------------------------------------------------------

links_app = typer.Typer(name="links", help="Entity links.", no_args_is_help=True)
app.add_typer(links_app)


@links_app.command("list")
def links_list(type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient) -> LinkList:
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
    body = LinkInput(relationship=relationship, entity=entity).model_dump(by_alias=True)
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
def attachments_list(type_: TypeArg, entity_id: IdArg, *, tracker: TrackerClient) -> AttachmentList:
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
    return BinaryResult(tracker.entities.attachment_download(file_id, filename), output)


@attachments_app.command("attach")
def attachments_attach(
    type_: TypeArg,
    entity_id: IdArg,
    temp_file_id: Annotated[str, typer.Argument(metavar="TEMP_FILE_ID", help="Temp file id.")],
    *,
    tracker: TrackerClient,
) -> Entity:
    """Attach a previously uploaded temp file to an entity (POST …/attachments/TEMP_FILE_ID)."""
    return tracker.entities.attachments_attach(type_.value, entity_id, temp_file_id)


@attachments_app.command("delete")
def attachments_delete(
    type_: TypeArg, entity_id: IdArg, file_id: FileIdArg, *, tracker: TrackerClient
) -> Ack:
    """Detach a file from an entity (DELETE …/attachments/FILE_ID; empty response body)."""
    tracker.entities.attachments_delete(type_.value, entity_id, file_id)
    return Ack.deleted("attachment", file_id, on=f"{type_.value} {entity_id}")
