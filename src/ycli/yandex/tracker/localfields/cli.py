"""`tracker localfields` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.localfields.models import LocalField, LocalFieldUpdate
from ycli.yandex.tracker.models import FieldCreate, LocalizedName, OptionsProviderInput

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


@app.command("list")
def list_(queue_id: QueueArg, *, tracker: TrackerClient) -> ItemList[LocalField]:
    """List the local fields of queue QUEUE_ID."""
    return tracker.localfields.list(queue_id)


@app.command()
def get(
    queue_id: QueueArg,
    field_key: Annotated[str, typer.Argument(help="Local field key (from `localfields list`).")],
    *,
    tracker: TrackerClient,
) -> LocalField:
    """Print one local field FIELD_KEY of queue QUEUE_ID."""
    return tracker.localfields.get(queue_id, field_key)


@app.command()
def create(
    queue_id: QueueArg,
    id_: Annotated[str, typer.Option("--id", help="Identifier (key) of the new local field.")],
    type_: Annotated[str, typer.Option("--type", help="Field type FQN, e.g. …StringFieldType.")],
    category: Annotated[str, typer.Option(help="Category id (from GET /fields/categories).")],
    name_ru: Annotated[str | None, typer.Option("--name-ru", help="Field name in Russian.")] = None,
    name_en: Annotated[str | None, typer.Option("--name-en", help="Field name in English.")] = None,
    description: Annotated[str | None, typer.Option(help="Description of the local field.")] = None,
    order: Annotated[int | None, typer.Option(help="Position in the org's field list.")] = None,
    readonly: Annotated[
        bool | None,
        typer.Option("--readonly/--no-readonly", help="Whether the field value is read-only."),
    ] = None,
    option: OptionOpt = None,
    options_type: OptionsTypeOpt = "FixedListOptionsProvider",
    *,
    tracker: TrackerClient,
) -> LocalField:
    """Create a local field in queue QUEUE_ID (POST /queues/{id}/localFields)."""
    body = FieldCreate(
        name=LocalizedName(ru=name_ru, en=name_en),
        id=id_,
        category=category,
        type=type_,
        options_provider=_options_provider(option, options_type),
        order=order,
        description=description,
        readonly=readonly,
    )
    return tracker.localfields.create(queue_id, body)


@app.command()
def update(
    queue_id: QueueArg,
    field_key: Annotated[str, typer.Argument(help="Local field key (from `localfields list`).")],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="New field name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="New field name in English.")
    ] = None,
    category: Annotated[str | None, typer.Option(help="New category id.")] = None,
    description: Annotated[
        str | None, typer.Option(help="New description of the local field.")
    ] = None,
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
    *,
    tracker: TrackerClient,
) -> LocalField:
    """Edit local field FIELD_KEY of queue QUEUE_ID (PATCH …/localFields/{key}; no version lock)."""
    named = name_ru is not None or name_en is not None
    body = LocalFieldUpdate(
        name=LocalizedName(ru=name_ru, en=name_en) if named else None,
        category=category,
        options_provider=_options_provider(option, options_type),
        order=order,
        description=description,
        readonly=readonly,
        visible=visible,
        hidden=hidden,
    )
    return tracker.localfields.update(queue_id, field_key, body)
