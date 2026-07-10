"""`tracker localfields` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.localfields.models import (
    LocalFieldCreate,
    LocalFieldUpdate,
    LocalizedName,
    OptionsProviderInput,
)

app = typer.Typer(name="localfields", help="Tracker per-queue local fields.", no_args_is_help=True)

QueueArg = Annotated[str, typer.Argument(help="Queue key (case-sensitive) or numeric id.")]
OptionOpt = Annotated[
    list[str] | None,
    typer.Option("--option", help="Allowed drop-down value (repeatable)."),
]
OptionsTypeOpt = Annotated[
    str, typer.Option("--options-type", help="Drop-down provider type for --option values.")
]


def _options_provider(values: list[str] | None, provider_type: str) -> OptionsProviderInput | None:
    """Build an ``OptionsProviderInput`` from repeated ``--option`` values, or None when empty."""
    if not values:
        return None
    return OptionsProviderInput(type=provider_type, values=values)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, queue_id: QueueArg) -> None:
    """List the local fields of queue QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.localfields.list(queue_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def get(
    ctx: typer.Context,
    queue_id: QueueArg,
    field_key: Annotated[str, typer.Argument(help="Local field key (from `localfields list`).")],
) -> None:
    """Print one local field FIELD_KEY of queue QUEUE_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.localfields.get(queue_id, field_key), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    queue_id: QueueArg,
    id_: Annotated[str, typer.Option("--id", help="Identifier (key) of the new local field.")],
    type_: Annotated[str, typer.Option("--type", help="Field type FQN, e.g. …StringFieldType.")],
    category: Annotated[str, typer.Option(help="Category id (from GET /fields/categories).")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Field name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Field name in English.")] = "",
    description: Annotated[str, typer.Option(help="Description of the local field.")] = "",
    order: Annotated[int | None, typer.Option(help="Position in the org's field list.")] = None,
    readonly: Annotated[bool, typer.Option(help="Whether the field value is read-only.")] = False,
    option: OptionOpt = None,
    options_type: OptionsTypeOpt = "FixedListOptionsProvider",
) -> None:
    """Create a local field in queue QUEUE_ID (POST /queues/{id}/localFields)."""
    body = LocalFieldCreate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
        id=id_,
        category=category,
        type=type_,
        options_provider=_options_provider(option, options_type),
        order=order,
        description=description or None,
        readonly=readonly or None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.localfields.create(queue_id, body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def edit(
    ctx: typer.Context,
    queue_id: QueueArg,
    field_key: Annotated[str, typer.Argument(help="Local field key (from `localfields list`).")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New field name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New field name in English.")] = "",
    category: Annotated[str, typer.Option(help="New category id.")] = "",
    description: Annotated[str, typer.Option(help="New description of the local field.")] = "",
    order: Annotated[int | None, typer.Option(help="New position in the field list.")] = None,
    readonly: Annotated[
        bool | None, typer.Option("--readonly/--no-readonly", help="Read-only value.")
    ] = None,
    visible: Annotated[
        bool | None, typer.Option("--visible/--no-visible", help="Always show the field.")
    ] = None,
    hidden: Annotated[
        bool | None, typer.Option("--hidden/--no-hidden", help="Fully hide the field.")
    ] = None,
    option: OptionOpt = None,
    options_type: OptionsTypeOpt = "FixedListOptionsProvider",
) -> None:
    """Edit local field FIELD_KEY of queue QUEUE_ID (PATCH …/localFields/{key}; no version lock)."""
    named = bool(name_ru or name_en)
    body = LocalFieldUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        category=category or None,
        options_provider=_options_provider(option, options_type),
        order=order,
        description=description or None,
        readonly=readonly,
        visible=visible,
        hidden=hidden,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.localfields.edit(queue_id, field_key, body),
        app_ctx.strategy,
        app_ctx.console,
    )
