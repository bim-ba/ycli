"""`datalens cloudenvironments` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.cloudenvironments.models import (
    CloudEnvironment,
    CloudEnvironmentNewStorage,
    CloudEnvironmentStorageChange,
)
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.models import ItemList

UNMEASURED = (
    "Experimental in the DataLens API. It creates or changes resources in a cloud, which may "
    "be billed: written from the document and never called, not measured."
)
app = typer.Typer(
    name="cloudenvironments",
    help="DataLens cloud environments (experimental in the API).",
    no_args_is_help=True,
)

EnvironmentIDArg = Annotated[str, typer.Argument(metavar="ID", help="Id of the cloud environment.")]
EnvironmentPermissionsOption = Annotated[
    bool | None,
    typer.Option(
        "--include-permissions/--no-include-permissions",
        help="Also say what you may do with the environment.",
    ),
]
SecurityGroupsOption = Annotated[
    list[str] | None,
    typer.Option("--security-group-ids", help="A security group it uses (repeatable)."),
]
StorageOption = Annotated[
    str | None,
    typer.Option(
        "--storage",
        help='The settings of its storage bucket, as a JSON object: {"maxSize": "0"} '
        "(bytes; zero is unlimited).",
    ),
]


@app.command("list")
def list_(
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None,
        typer.Option(
            "--filter",
            help='A condition, all must hold: status="READY", name="…", cloud_id="…", '
            'created_by_id="…" (repeatable).',
        ),
    ] = None,
    include_permissions: EnvironmentPermissionsOption = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> ItemList[CloudEnvironment]:
    """List the cloud environments (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.cloudenvironments.list(
        filter=filter or None, include_permissions=include_permissions, limit=cap
    )


@app.command()
def get(
    id: EnvironmentIDArg,  # noqa: A002  # the API's own name for it
    include_permissions: EnvironmentPermissionsOption = None,
    *,
    datalens: DataLensClient,
) -> CloudEnvironment:
    """Print one cloud environment; an id nothing knows answers 403, not 404."""
    return datalens.cloudenvironments.get(id, include_permissions=include_permissions)


@app.command(epilog=UNMEASURED)
def create(
    name: Annotated[str, typer.Option("--name", help="The environment's name.")],
    cloud_id: Annotated[str, typer.Option("--cloud-id", help="The cloud to make it in.")],
    subnet_id: Annotated[str, typer.Option("--subnet-id", help="The subnet it uses.")],
    description: Annotated[str | None, typer.Option("--description", help="A description.")] = None,
    security_group_ids: SecurityGroupsOption = None,
    storage: StorageOption = None,
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Make a cloud environment; prints the operation that makes it."""
    return datalens.cloudenvironments.create(
        name=name,
        cloud_id=cloud_id,
        subnet_id=subnet_id,
        description=description,
        security_group_ids=security_group_ids or None,
        storage=(
            None
            if storage is None
            else CloudEnvironmentNewStorage.model_validate(json.loads(storage))
        ),
    )


@app.command(epilog=UNMEASURED)
def update(
    id: EnvironmentIDArg,  # noqa: A002  # the API's own name for it
    name: Annotated[str | None, typer.Option("--name", help="A new name.")] = None,
    description: Annotated[
        str | None, typer.Option("--description", help="A new description; empty clears it.")
    ] = None,
    security_group_ids: SecurityGroupsOption = None,
    storage: StorageOption = None,
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Change the fields given of a cloud environment; prints the operation."""
    return datalens.cloudenvironments.update(
        id,
        name=name,
        description=description,
        security_group_ids=security_group_ids or None,
        storage=(
            None
            if storage is None
            else CloudEnvironmentStorageChange.model_validate(json.loads(storage))
        ),
    )


@app.command(epilog=UNMEASURED)
def delete(
    id: EnvironmentIDArg,  # noqa: A002  # the API's own name for it
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Delete a cloud environment; prints the operation that deletes it."""
    return datalens.cloudenvironments.delete(id)
