"""`tracker fields` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.models import ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.fields.models import (
    CustomField,
    FieldCategoryCreate,
    FieldCategoryRecord,
    FieldCategoryUpdate,
    FieldUpdate,
)
from ycli.yandex.tracker.models import FieldCreate, LocalizedName, OptionsProviderInput
from ycli.yandex.tracker.typedefs import OptionOpt, OptionsTypeOpt

app = typer.Typer(name="fields", help="Tracker global fields.", no_args_is_help=True)


def _options_provider(values: list[str] | None, provider_type: str) -> OptionsProviderInput | None:
    """Build an ``OptionsProviderInput`` from repeated ``--option`` values, or None when empty."""
    if not values:
        return None
    return OptionsProviderInput(type=provider_type, values=values)


@app.command("list")
def list_(*, tracker: TrackerClient) -> ItemList[CustomField]:
    """List all global fields of the organisation."""
    return tracker.fields.list()


@app.command()
def get(
    field_id: Annotated[
        str, typer.Argument(metavar="FIELD_ID", help="Identifier of the issue field.")
    ],
    *,
    tracker: TrackerClient,
) -> CustomField:
    """Get parameters of one issue field by FIELD_ID."""
    return tracker.fields.get(field_id=field_id)


@app.command()
def create(
    id_: Annotated[str, typer.Option("--id", help="Identifier (key) of the new field.")],
    type_: Annotated[str, typer.Option("--type", help="Field type FQN, e.g. …StringFieldType.")],
    category: Annotated[str, typer.Option(help="Category id (from `fields` categories).")],
    name_ru: Annotated[str | None, typer.Option("--name-ru", help="Field name in Russian.")] = None,
    name_en: Annotated[str | None, typer.Option("--name-en", help="Field name in English.")] = None,
    description: Annotated[str | None, typer.Option(help="Description of the field.")] = None,
    order: Annotated[int | None, typer.Option(help="Position in the org's field list.")] = None,
    readonly: Annotated[
        bool | None,
        typer.Option("--readonly/--no-readonly", help="Whether the field value is read-only."),
    ] = None,
    option: OptionOpt = None,
    options_type: OptionsTypeOpt = "FixedListOptionsProvider",
    *,
    tracker: TrackerClient,
) -> CustomField:
    """Create a global field (POST /fields)."""
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
    return tracker.fields.create(body)


@app.command()
def update(
    field_id: Annotated[str, typer.Argument(metavar="FIELD_ID", help="Identifier of the field.")],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="New field name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="New field name in English.")
    ] = None,
    option: OptionOpt = None,
    options_type: OptionsTypeOpt = "FixedListOptionsProvider",
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> CustomField:
    """Edit a global field FIELD_ID — rename and/or change options (PATCH /fields/{id}?version=)."""
    named = name_ru is not None or name_en is not None
    body = FieldUpdate(
        name=LocalizedName(ru=name_ru, en=name_en) if named else None,
        options_provider=_options_provider(option, options_type),
    )
    return tracker.fields.update(field_id, body, version=version)


@app.command("categories-create")
def categories_create(
    order: Annotated[int, typer.Option(help="Display-order weight of the category.")],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="Category name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="Category name in English.")
    ] = None,
    description: Annotated[str | None, typer.Option(help="Description of the category.")] = None,
    *,
    tracker: TrackerClient,
) -> FieldCategoryRecord:
    """Create a field category (POST /fields/categories)."""
    body = FieldCategoryCreate(
        name=LocalizedName(ru=name_ru, en=name_en),
        order=order,
        description=description,
    )
    return tracker.fields.categories_create(body)


@app.command("categories-update")
def categories_update(
    category_id: Annotated[
        str, typer.Argument(metavar="CATEGORY_ID", help="Identifier of the field category.")
    ],
    name_ru: Annotated[
        str | None, typer.Option("--name-ru", help="New category name in Russian.")
    ] = None,
    name_en: Annotated[
        str | None, typer.Option("--name-en", help="New category name in English.")
    ] = None,
    order: Annotated[int | None, typer.Option(help="New display-order weight.")] = None,
    description: Annotated[
        str | None, typer.Option(help="New description of the category.")
    ] = None,
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> FieldCategoryRecord:
    """Edit a field category CATEGORY_ID (PATCH /fields/categories/{id}?version=)."""
    named = name_ru is not None or name_en is not None
    body = FieldCategoryUpdate(
        name=LocalizedName(ru=name_ru, en=name_en) if named else None,
        order=order,
        description=description,
    )
    return tracker.fields.categories_update(category_id, body, version=version)
