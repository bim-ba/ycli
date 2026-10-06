"""`datalens trinoclusters` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.trinoclusters.models import (
    TrinoCatalogToAdd,
    TrinoCluster,
    TrinoNewCatalog,
    TrinoResourcePreset,
    TrinoWorkerConfig,
)
from ycli.yandex.models import ItemList

BILLED = (
    "Experimental in the DataLens API. A cluster is cloud resources, billed while it runs: "
    "written from the document and never called, not measured."
)
UNMEASURED = (
    "Experimental in the DataLens API and written from its document: not measured. An id "
    "nothing knows answers 403 Permission denied, not 404."
)
app = typer.Typer(
    name="trinoclusters",
    help="DataLens Trino clusters (experimental in the API).",
    no_args_is_help=True,
)

TrinoClusterIDArg = Annotated[str, typer.Argument(metavar="ID", help="Id of the Trino cluster.")]
ClusterIDArg = Annotated[str, typer.Argument(metavar="CLUSTER_ID", help="Id of the Trino cluster.")]
PresetEnvironmentOption = Annotated[
    str,
    typer.Option("--cloud-environment-id", help="The cloud environment the presets are of."),
]


@app.command("list")
def list_(
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None,
        typer.Option("--filter", help="A condition the clusters must meet (repeatable)."),
    ] = None,
    collection_id: Annotated[
        str | None, typer.Option("--collection-id", help="Only the clusters of this collection.")
    ] = None,
    catalog_id: Annotated[
        str | None,
        typer.Option("--catalog-id", help="Only the clusters this REST catalog is attached to."),
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> ItemList[TrinoCluster]:
    """List the Trino clusters (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.trinoclusters.list(
        filter=filter or None, collection_id=collection_id, catalog_id=catalog_id, limit=cap
    )


@app.command(epilog=UNMEASURED)
def get(
    id: TrinoClusterIDArg,  # noqa: A002  # the API's own name for it
    *,
    datalens: DataLensClient,
) -> TrinoCluster:
    """Print one Trino cluster: its configuration, health, status and coordinator."""
    return datalens.trinoclusters.get(id)


@app.command(epilog=BILLED)
def create(
    collection_id: Annotated[
        str, typer.Option("--collection-id", help="The DataLens collection to make it in.")
    ],
    cloud_environment_id: Annotated[
        str, typer.Option("--cloud-environment-id", help="The cloud environment to make it in.")
    ],
    name: Annotated[str, typer.Option("--name", help="The cluster's name.")],
    worker_config: Annotated[
        str,
        typer.Option(
            "--worker-config",
            help="The workers, as a JSON object: "
            '{"resources": {"resourcePresetId": "…"}, '
            '"scalePolicy": {"autoScale": {"minCount": "1", "maxCount": "4"}}}.',
        ),
    ],
    description: Annotated[str | None, typer.Option("--description", help="A description.")] = None,
    labels: Annotated[
        str | None,
        typer.Option("--labels", help='Labels, as a JSON object: {"team": "analytics"}.'),
    ] = None,
    catalogs_config: Annotated[
        list[str] | None,
        typer.Option(
            "--catalogs-config",
            help='A REST catalog to attach, as a JSON object: {"catalogId": "…"} (repeatable).',
        ),
    ] = None,
    trino_version: Annotated[
        str | None,
        typer.Option("--trino-version", help="The version of Trino; the service's own if not."),
    ] = None,
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Make a Trino cluster; prints the operation that makes it."""
    return datalens.trinoclusters.create(
        collection_id=collection_id,
        cloud_environment_id=cloud_environment_id,
        name=name,
        worker_config=TrinoWorkerConfig.model_validate(json.loads(worker_config)),
        description=description,
        labels=None if labels is None else json.loads(labels),
        catalogs_config=(
            [TrinoNewCatalog.model_validate(json.loads(item)) for item in catalogs_config]
            if catalogs_config
            else None
        ),
        trino_version=trino_version,
    )


@app.command(epilog=BILLED)
def delete(
    id: TrinoClusterIDArg,  # noqa: A002  # the API's own name for it
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Delete a Trino cluster; prints the operation that deletes it."""
    return datalens.trinoclusters.delete(id)


@app.command(epilog=BILLED)
def start(cluster_id: ClusterIDArg, *, datalens: DataLensClient) -> LakehouseOperation:
    """Start a stopped Trino cluster; prints the operation that starts it."""
    return datalens.trinoclusters.start(cluster_id)


@app.command(epilog=BILLED)
def stop(cluster_id: ClusterIDArg, *, datalens: DataLensClient) -> LakehouseOperation:
    """Stop a running Trino cluster; prints the operation that stops it."""
    return datalens.trinoclusters.stop(cluster_id)


@app.command("catalog-create", epilog=BILLED)
def catalog_create(
    cluster_id: ClusterIDArg,
    catalog: Annotated[
        str,
        typer.Option(
            "--catalog", help='The REST catalog to attach, as a JSON object: {"catalogId": "…"}.'
        ),
    ],
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Attach a REST catalog to a Trino cluster; prints the operation."""
    return datalens.trinoclusters.catalog_create(
        cluster_id, catalog=TrinoCatalogToAdd.model_validate(json.loads(catalog))
    )


@app.command("catalog-delete", epilog=BILLED)
def catalog_delete(
    cluster_id: ClusterIDArg,
    catalog_id: Annotated[
        str, typer.Option("--catalog-id", help="The id of the REST catalog to detach.")
    ],
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Detach a REST catalog from a Trino cluster; the catalog itself stays."""
    return datalens.trinoclusters.catalog_delete(cluster_id, catalog_id=catalog_id)


@app.command("resource-presets-list", epilog=UNMEASURED)
def resource_presets_list(
    cloud_environment_id: Annotated[
        str,
        typer.Argument(metavar="CLOUD_ENVIRONMENT_ID", help="Id of the cloud environment."),
    ],
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> ItemList[TrinoResourcePreset]:
    """List the sizes a cluster's machines may have in a cloud environment."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.trinoclusters.resource_presets_list(cloud_environment_id, limit=cap)


@app.command("resource-preset-get", epilog=UNMEASURED)
def resource_preset_get(
    resource_preset_id: Annotated[
        str, typer.Argument(metavar="RESOURCE_PRESET_ID", help="Id of the resource preset.")
    ],
    cloud_environment_id: PresetEnvironmentOption,
    *,
    datalens: DataLensClient,
) -> TrinoResourcePreset:
    """Print one size of a cluster's machines: its cores and its memory."""
    return datalens.trinoclusters.resource_preset_get(
        resource_preset_id, cloud_environment_id=cloud_environment_id
    )
