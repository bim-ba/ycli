"""`tracker entities` commands — projects / portfolios / goals and their sub-resources.

Core verbs live on the top-level app (``get``/``create``/``edit``/``delete``/``search``/
``history``/``permissions``/``set-permissions``/``bulk``); comments, checklists, links and
attachments are nested sub-apps. Reads/writes render through :class:`Serializer`; the one
binary download (``attachments download``) writes raw bytes via ``ycli.cli.binary``.
"""

from __future__ import annotations

import enum
from typing import Annotated, Any

import typer

from ycli.cli.binary import write_output
from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.entities.models import (
    ChecklistItemInput,
    ChecklistItemsInput,
    CommentCreate,
    CommentUpdate,
    DeadlineInput,
    LinkInput,
    ReportCreate,
    ReportFieldsInput,
    ReportFilter,
    ReportParameters,
)
from ycli.yandex.tracker.utils import parse_fields


class EntityType(enum.StrEnum):
    """The three entity types the Entities API unifies."""

    project = "project"
    portfolio = "portfolio"
    goal = "goal"


app = typer.Typer(
    name="entities", help="Tracker projects, portfolios and goals.", no_args_is_help=True
)

TypeArg = Annotated[
    EntityType, typer.Argument(metavar="TYPE", help="Entity type: project, portfolio or goal.")
]
IdArg = Annotated[str, typer.Argument(metavar="ID", help="Entity id (or shortId).")]
FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Extra fields entry key=value (JSON-coerced; repeatable)."),
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


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

    Mirrors the ``EntityFieldsInput`` model 1:1; a plain dict keeps the aliased keys explicit and
    lets ``--field key=value`` override or add arbitrary field parameters.
    """
    fields: dict[str, Any] = {}
    for key, value in (
        ("summary", summary),
        ("description", description),
        ("lead", lead),
        ("author", author),
        ("entityStatus", status),
        ("start", start),
        ("end", end),
    ):
        if value:
            fields[key] = value
    if parent:
        fields["parentEntity"] = {"primary": parent}
    if team_user:
        fields["teamUsers"] = team_user
    if tag:
        fields["tags"] = tag
    fields |= parse_fields(field)
    return fields


@app.command()
def get(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    expand: Annotated[str, typer.Option(help="Extra info, e.g. attachments.")] = "",
    fields: Annotated[str, typer.Option(help="Comma-separated extra fields to include.")] = "",
) -> None:
    """Print a single entity (project/portfolio/goal) by ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.get(
            type_.value, entity_id, expand=expand or None, fields=fields or None
        ),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def create(
    ctx: typer.Context,
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
) -> None:
    """Create an entity (POST /entities/TYPE). summary is required; other fields optional."""
    fields_body = _fields_body(
        summary, description, lead, author, status, start, end, parent, team_user, tag, field
    )
    body = {"fields": fields_body}
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.create(type_.value, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
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
) -> None:
    """Edit entity ID (PATCH /entities/TYPE/ID) — only supplied fields are sent."""
    fields_body = _fields_body(
        summary, description, lead, author, status, start, end, parent, team_user, tag, field
    )
    body: dict[str, Any] = {}
    if fields_body:
        body["fields"] = fields_body
    if comment:
        body["comment"] = comment
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.edit(type_.value, entity_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    with_board: Annotated[
        bool, typer.Option("--with-board", help="Also delete the entity's board.")
    ] = False,
) -> None:
    """Delete entity ID (DELETE /entities/TYPE/ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.entities.delete(type_.value, entity_id, with_board=with_board or None)
    print(f"Deleted {type_.value} {entity_id}")


@app.command()
def search(
    ctx: typer.Context,
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
) -> None:
    """Search entities of TYPE (POST /entities/TYPE/_search)."""
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
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.search(type_.value, body, fields=fields or None),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def history(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    limit: Annotated[int, typer.Option(help="Max events (0 = all).")] = 0,
) -> None:
    """Print an entity's event history (GET …/events/_relative, auto-paginated)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.history(type_.value, entity_id, limit=limit or None),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def permissions(ctx: typer.Context, type_: TypeArg, entity_id: IdArg) -> None:
    """Print an entity's access settings (GET …/extendedPermissions)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.permissions(type_.value, entity_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command("set-permissions")
def set_permissions(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    field: Annotated[
        list[str] | None,
        typer.Option("--acl", help='ACL entry LEVEL=<json>, e.g. READ={"roles":["OWNER"]}.'),
    ] = None,
) -> None:
    """Set an entity's access settings (PATCH …/extendedPermissions)."""
    body = {"acl": parse_fields(field)}
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.set_permissions(type_.value, entity_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def bulk(
    ctx: typer.Context,
    type_: TypeArg,
    entity: Annotated[list[str], typer.Option("--entity", help="Entity id (repeatable).")],
    comment: Annotated[str, typer.Option(help="Comment to add to every entity.")] = "",
    field: FieldOpt = None,
) -> None:
    """Mass-edit entities (POST …/bulkchange/_update) — returns the async operation handle."""
    values: dict[str, Any] = {}
    fields_body = parse_fields(field)
    if fields_body:
        values["fields"] = fields_body
    if comment:
        values["comment"] = comment
    body = {"metaEntities": entity, "values": values}
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.bulk_update(type_.value, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command("bulk-status")
def bulk_status(
    ctx: typer.Context,
    operation_id: Annotated[str, typer.Argument(metavar="OPERATION_ID", help="Bulk-change id.")],
) -> None:
    """Print a bulk-change operation's status (GET /bulkchange/OPERATION_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.bulk_status(operation_id), app_ctx.strategy, app_ctx.console
    )


@app.command("create-report")
def create_report(
    ctx: typer.Context,
    summary: Annotated[str, typer.Option(help="Report name (required).")],
    query: Annotated[str, typer.Option(help="Issue filter in Tracker Query Language (required).")],
    format_: Annotated[
        str, typer.Option("--format", help="Export format: xlsx, xml or csv.")
    ] = "xlsx",
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-F", help="Issue field key to include as a column (repeatable)."),
    ] = None,
) -> None:
    """Build an issue report (POST /entities/report/) from a TQL query and column fields."""
    body = ReportCreate(
        fields=ReportFieldsInput(
            summary=summary,
            parameters=ReportParameters(
                format=format_, filter=ReportFilter(query=query), fields=field or []
            ),
        )
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.create_report(body=body), app_ctx.strategy, app_ctx.console
    )


# --------------------------------------------------------------------------------------------
# comments sub-app
# --------------------------------------------------------------------------------------------

comments_app = typer.Typer(name="comments", help="Entity comments.", no_args_is_help=True)
app.add_typer(comments_app)

CommentIdArg = Annotated[str, typer.Argument(metavar="COMMENT_ID", help="Comment id.")]


@comments_app.callback()
def _comments_group() -> None:
    """Group anchor for `entities comments`."""


@comments_app.command("list")
def comments_list(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    all_: Annotated[
        bool, typer.Option("--all", help="Drain the paginated (_relative) listing.")
    ] = False,
    limit: Annotated[int, typer.Option(help="Max comments when --all (0 = all).")] = 0,
) -> None:
    """List comments on an entity (GET …/comments; --all uses …/comments/_relative)."""
    app_ctx = AppContext.from_typer_context(ctx)
    result = (
        app_ctx.tracker.entities.comments_relative(type_.value, entity_id, limit=limit or None)
        if all_
        else app_ctx.tracker.entities.comments_list(type_.value, entity_id)
    )
    Serializer.serialize(result, app_ctx.strategy, app_ctx.console)


@comments_app.command("get")
def comments_get(
    ctx: typer.Context, type_: TypeArg, entity_id: IdArg, comment_id: CommentIdArg
) -> None:
    """Get one comment on an entity (GET …/comments/COMMENT_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.comments_get(type_.value, entity_id, comment_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@comments_app.command("create")
def comments_create(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    text: Annotated[str, typer.Option(help='Comment text — pass "$(cat note.md)" for markdown.')],
    summon: Annotated[
        list[str] | None, typer.Option("--summon", help="User to summon (repeatable).")
    ] = None,
) -> None:
    """Add a comment to an entity (POST …/comments)."""
    body = CommentCreate(text=text, summonees=summon or None).model_dump(
        by_alias=True, exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.comments_create(type_.value, entity_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@comments_app.command("edit")
def comments_edit(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    comment_id: CommentIdArg,
    text: Annotated[str, typer.Option(help="New comment text.")],
) -> None:
    """Edit a comment on an entity (PATCH …/comments; id travels in the body)."""
    body = CommentUpdate(id=comment_id, text=text).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.comments_edit(type_.value, entity_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@comments_app.command("delete")
def comments_delete(
    ctx: typer.Context, type_: TypeArg, entity_id: IdArg, comment_id: CommentIdArg
) -> None:
    """Delete a comment from an entity (DELETE …/comments/COMMENT_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.entities.comments_delete(type_.value, entity_id, comment_id)
    print(f"Deleted comment {comment_id} on {type_.value} {entity_id}")


# --------------------------------------------------------------------------------------------
# checklists sub-app
# --------------------------------------------------------------------------------------------

checklists_app = typer.Typer(name="checklists", help="Entity checklists.", no_args_is_help=True)
app.add_typer(checklists_app)

ItemIdArg = Annotated[str, typer.Argument(metavar="ITEM_ID", help="Checklist item id.")]


@checklists_app.callback()
def _checklists_group() -> None:
    """Group anchor for `entities checklists`."""


def _item_input(
    text: str, checked: bool, assignee: str, deadline: str, item_id: str = ""
) -> ChecklistItemInput:
    """Build a typed checklist item from CLI options."""
    return ChecklistItemInput(
        id=item_id or None,
        text=text or None,
        checked=checked or None,
        assignee=assignee or None,
        deadline=DeadlineInput(date=deadline) if deadline else None,
    )


@checklists_app.command("create")
def checklists_create(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    text: Annotated[
        list[str], typer.Option("--text", help="Item text (repeatable — one per item).")
    ],
) -> None:
    """Add checklist items to an entity (POST …/checklistItems)."""
    items = ChecklistItemsInput([ChecklistItemInput(text=t) for t in text]).model_dump(
        by_alias=True, exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.checklists_create(type_.value, entity_id, body=items),
        app_ctx.strategy,
        app_ctx.console,
    )


@checklists_app.command("edit")
def checklists_edit(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    item: Annotated[
        list[str],
        typer.Option("--item", help="Item as id=text (repeatable — replaces the whole checklist)."),
    ],
) -> None:
    """Replace the whole checklist (PATCH …/checklistItems) from repeated --item id=text."""
    parsed = parse_fields(item)
    items = ChecklistItemsInput(
        [ChecklistItemInput(id=item_id, text=str(text)) for item_id, text in parsed.items()]
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.checklists_edit(type_.value, entity_id, body=items),
        app_ctx.strategy,
        app_ctx.console,
    )


@checklists_app.command("edit-item")
def checklists_edit_item(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    item_id: ItemIdArg,
    text: Annotated[str, typer.Option(help="New item text.")] = "",
    checked: Annotated[bool, typer.Option("--checked", help="Mark the item done.")] = False,
    assignee: Annotated[str, typer.Option(help="Assignee user id/login.")] = "",
    deadline: Annotated[
        str, typer.Option(help="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    ] = "",
) -> None:
    """Edit a single checklist item (PATCH …/checklistItems/ITEM_ID)."""
    body = _item_input(text, checked, assignee, deadline).model_dump(
        by_alias=True, exclude_none=True
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.checklists_edit_item(type_.value, entity_id, item_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@checklists_app.command("delete-item")
def checklists_delete_item(
    ctx: typer.Context, type_: TypeArg, entity_id: IdArg, item_id: ItemIdArg
) -> None:
    """Remove one checklist item (DELETE …/checklistItems/ITEM_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.checklists_delete_item(type_.value, entity_id, item_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@checklists_app.command("delete")
def checklists_delete(ctx: typer.Context, type_: TypeArg, entity_id: IdArg) -> None:
    """Clear the whole checklist (DELETE …/checklistItems)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.checklists_delete(type_.value, entity_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@checklists_app.command("move")
def checklists_move(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    item_id: ItemIdArg,
    before: Annotated[str, typer.Option(help="Item id to insert the moved item before.")] = "",
) -> None:
    """Reorder a checklist item (POST …/checklistItems/ITEM_ID/_move)."""
    body = {"before": before} if before else {}
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.checklists_move(type_.value, entity_id, item_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


# --------------------------------------------------------------------------------------------
# links sub-app
# --------------------------------------------------------------------------------------------

links_app = typer.Typer(name="links", help="Entity links.", no_args_is_help=True)
app.add_typer(links_app)


@links_app.callback()
def _links_group() -> None:
    """Group anchor for `entities links`."""


@links_app.command("list")
def links_list(ctx: typer.Context, type_: TypeArg, entity_id: IdArg) -> None:
    """List an entity's links to other entities (GET …/links)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.links_list(type_.value, entity_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@links_app.command("create")
def links_create(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    relationship: Annotated[str, typer.Option(help="Link type, e.g. relates, depends on.")],
    entity: Annotated[str, typer.Option(help="Id of the entity to link to.")],
) -> None:
    """Create a link between entities (POST …/links)."""
    body = LinkInput(relationship=relationship, entity=entity).model_dump(by_alias=True)
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.entities.links_create(type_.value, entity_id, body=body)
    print(f"Linked {type_.value} {entity_id} -> {entity} ({relationship})")


@links_app.command("delete")
def links_delete(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    right: Annotated[str, typer.Argument(metavar="RIGHT", help="Id of the entity to unlink.")],
) -> None:
    """Delete a link (DELETE …/links?right=RIGHT)."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.tracker.entities.links_delete(type_.value, entity_id, right)
    print(f"Unlinked {type_.value} {entity_id} -> {right}")


# --------------------------------------------------------------------------------------------
# attachments sub-app
# --------------------------------------------------------------------------------------------

attachments_app = typer.Typer(name="attachments", help="Entity attachments.", no_args_is_help=True)
app.add_typer(attachments_app)

FileIdArg = Annotated[str, typer.Argument(metavar="FILE_ID", help="Attachment file id.")]


@attachments_app.callback()
def _attachments_group() -> None:
    """Group anchor for `entities attachments`."""


@attachments_app.command("list")
def attachments_list(ctx: typer.Context, type_: TypeArg, entity_id: IdArg) -> None:
    """List files attached to an entity (GET …/attachments)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.attachments_list(type_.value, entity_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@attachments_app.command("get")
def attachments_get(
    ctx: typer.Context, type_: TypeArg, entity_id: IdArg, file_id: FileIdArg
) -> None:
    """Get one attachment's metadata (GET …/attachments/FILE_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.attachments_get(type_.value, entity_id, file_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@attachments_app.command("download")
def attachments_download(
    ctx: typer.Context,
    file_id: FileIdArg,
    filename: Annotated[str, typer.Argument(metavar="FILENAME", help="Attachment file name.")],
    output: Annotated[
        str | None,
        typer.Option("--output", "-O", help="Write to this path; omit or '-' for stdout."),
    ] = None,
) -> None:
    """Download an attachment's raw bytes to --output (or stdout). Binary is CLI/SDK-only."""
    app_ctx = AppContext.from_typer_context(ctx)
    write_output(app_ctx.tracker.entities.attachment_download(file_id, filename), output)


@attachments_app.command("attach")
def attachments_attach(
    ctx: typer.Context,
    type_: TypeArg,
    entity_id: IdArg,
    temp_file_id: Annotated[str, typer.Argument(metavar="TEMP_FILE_ID", help="Temp file id.")],
) -> None:
    """Attach a previously uploaded temp file to an entity (POST …/attachments/TEMP_FILE_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.attachments_attach(type_.value, entity_id, temp_file_id),
        app_ctx.strategy,
        app_ctx.console,
    )


@attachments_app.command("delete")
def attachments_delete(
    ctx: typer.Context, type_: TypeArg, entity_id: IdArg, file_id: FileIdArg
) -> None:
    """Detach a file from an entity (DELETE …/attachments/FILE_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.entities.attachments_delete(type_.value, entity_id, file_id),
        app_ctx.strategy,
        app_ctx.console,
    )
