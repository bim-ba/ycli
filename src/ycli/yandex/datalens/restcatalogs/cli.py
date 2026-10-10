"""`datalens restcatalogs` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.restcatalogs.models import (
    RestCatalog,
    RestCatalogBucketSettings,
    RestCatalogSortField,
)

app = typer.Typer(
    name="restcatalogs",
    help="DataLens REST catalogs (experimental in the API).",
    no_args_is_help=True,
)


@app.command("list")
def list_(
    cloud_environment_id: Annotated[
        str | None,
        typer.Option("--cloud-environment-id", help="Only the catalogs of this cloud environment."),
    ] = None,
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None,
        typer.Option("--filter", help='A condition such as name="…" (repeatable).'),
    ] = None,
    sort_by: Annotated[
        str | None, values_option(RestCatalogSortField, "--sort-by", help="The field to sort by.")
    ] = None,
    reverse_order: Annotated[
        bool | None,
        typer.Option("--reverse-order/--no-reverse-order", help="Sort the other way round."),
    ] = None,
    include_permissions: Annotated[
        bool | None,
        typer.Option(
            "--include-permissions/--no-include-permissions",
            help="Also say what you may do with each catalog.",
        ),
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[RestCatalog]:
    """List the REST catalogs (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.restcatalogs.list(
        cloud_environment_id=cloud_environment_id,
        filter=filter or None,
        sort_by=sort_by,
        reverse_order=reverse_order,
        include_permissions=include_permissions,
        limit=cap,
        next=next_,
    )


@app.command(
    epilog="Experimental in the DataLens API. It creates a bucket in a cloud, which may be "
    "billed: written from the document and never called, not measured."
)
def create(
    cloud_environment_id: Annotated[
        str, typer.Option("--cloud-environment-id", help="The cloud environment to make it in.")
    ],
    name: Annotated[str, typer.Option("--name", help="The catalog's name.")],
    bucket_settings: Annotated[
        str,
        typer.Option(
            "--bucket-settings",
            help='The settings of its bucket, as a JSON object: {"storageClass": "STANDARD", '
            '"maxSize": "1073741824"}, or {}.',
        ),
    ],
    description: Annotated[str | None, typer.Option("--description", help="A description.")] = None,
    labels: Annotated[
        str | None,
        typer.Option("--labels", help='Labels, as a JSON object: {"team": "analytics"}.'),
    ] = None,
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Make a REST catalog; prints the operation that makes it."""
    return datalens.restcatalogs.create(
        cloud_environment_id=cloud_environment_id,
        name=name,
        bucket_settings=RestCatalogBucketSettings.model_validate(json.loads(bucket_settings)),
        description=description,
        labels=None if labels is None else json.loads(labels),
    )
