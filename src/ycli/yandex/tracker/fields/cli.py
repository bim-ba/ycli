"""`tracker fields` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.fields.models import (
    CustomField,
    FieldCategoryCreate,
    FieldCategoryRecord,
    FieldCategoryUpdate,
    FieldCreate,
    FieldList,
    FieldUpdate,
    LocalizedName,
    OptionsProviderInput,
)

app = typer.Typer(name="fields", help="Tracker global fields.", no_args_is_help=True)

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
def list_(*, tracker: TrackerClient) -> FieldList:
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
    name_ru: Annotated[str, typer.Option("--name-ru", help="Field name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Field name in English.")] = "",
    description: Annotated[str, typer.Option(help="Description of the field.")] = "",
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
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
        id=id_,
        category=category,
        type=type_,
        options_provider=_options_provider(option, options_type),
        order=order,
        description=description or None,
        readonly=readonly,
    )
    return tracker.fields.create(body)


@app.command()
def edit(
    field_id: Annotated[str, typer.Argument(metavar="FIELD_ID", help="Identifier of the field.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New field name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New field name in English.")] = "",
    option: OptionOpt = None,
    options_type: OptionsTypeOpt = "FixedListOptionsProvider",
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> CustomField:
    """Edit a global field FIELD_ID — rename and/or change options (PATCH /fields/{id}?version=)."""
    named = bool(name_ru or name_en)
    body = FieldUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        options_provider=_options_provider(option, options_type),
    )
    return tracker.fields.edit(field_id, body, version=version)


@app.command("category-create")
def category_create(
    order: Annotated[int, typer.Option(help="Display-order weight of the category.")],
    name_ru: Annotated[str, typer.Option("--name-ru", help="Category name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="Category name in English.")] = "",
    description: Annotated[str, typer.Option(help="Description of the category.")] = "",
    *,
    tracker: TrackerClient,
) -> FieldCategoryRecord:
    """Create a field category (POST /fields/categories)."""
    body = FieldCategoryCreate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None),
        order=order,
        description=description or None,
    )
    return tracker.fields.category_create(body)


@app.command("category-edit")
def category_edit(
    category_id: Annotated[
        str, typer.Argument(metavar="CATEGORY_ID", help="Identifier of the field category.")
    ],
    name_ru: Annotated[str, typer.Option("--name-ru", help="New category name in Russian.")] = "",
    name_en: Annotated[str, typer.Option("--name-en", help="New category name in English.")] = "",
    order: Annotated[int | None, typer.Option(help="New display-order weight.")] = None,
    description: Annotated[str, typer.Option(help="New description of the category.")] = "",
    version: Annotated[
        int | None, typer.Option(help="Current version for the optimistic lock (?version=).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> FieldCategoryRecord:
    """Edit a field category CATEGORY_ID (PATCH /fields/categories/{id}?version=)."""
    named = bool(name_ru or name_en)
    body = FieldCategoryUpdate(
        name=LocalizedName(ru=name_ru or None, en=name_en or None) if named else None,
        order=order,
        description=description or None,
    )
    return tracker.fields.category_edit(category_id, body, version=version)
