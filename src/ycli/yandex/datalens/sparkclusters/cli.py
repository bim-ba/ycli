"""`datalens sparkclusters` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.body_fields import CallerFields
from ycli.cli.typedefs import AllOption, LimitOption, NextOption
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.schemas.spark_clusters import CreateSparkClusterArgs
from ycli.yandex.datalens.sparkclusters.models import SparkCluster, SparkResourcePreset

app = typer.Typer(
    name="sparkclusters",
    help="Spark clusters of DataLens (an experimental API; not measured, a cluster is paid for).",
    no_args_is_help=True,
)

SparkClusterIDArg = Annotated[str, typer.Argument(metavar="CLUSTER_ID", help="Spark cluster id.")]
EnvironmentOption = Annotated[
    str,
    typer.Option("--cloud-environment-id", help="The cloud environment the presets are for."),
]


@app.command("list")
def list_(
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    collection_id: Annotated[
        str | None, typer.Option("--collection-id", help="Keep the clusters of one collection.")
    ] = None,
    filter_: Annotated[
        list[str] | None,
        typer.Option("--filter", help="A filter expression of the API (repeatable)."),
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[SparkCluster]:
    """List the Spark clusters (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.sparkclusters.list(
        limit=cap, next=next_, collection_id=collection_id, filter=filter_
    )


@app.command()
def get(cluster_id: SparkClusterIDArg, *, datalens: DataLensClient) -> SparkCluster:
    """Print one Spark cluster: its settings, health and status."""
    return datalens.sparkclusters.get(cluster_id)


@app.command()
def create(
    collection_id: Annotated[
        str | None, typer.Option("--collection-id", help="The collection to create it in.")
    ] = None,
    cloud_environment_id: Annotated[
        str | None,
        typer.Option("--cloud-environment-id", help="The cloud environment the cluster runs in."),
    ] = None,
    name: Annotated[str | None, typer.Option("--name", help="The cluster's name.")] = None,
    config: Annotated[
        str | None,
        typer.Option(
            "--config",
            help="The Spark version and the pools of the driver and executors, as a JSON "
            "object; --body-file gives it under `config`.",
        ),
    ] = None,
    description: Annotated[
        str | None, typer.Option("--description", help="A description of the cluster.")
    ] = None,
    labels: Annotated[
        str | None, typer.Option("--labels", help='Labels, as a JSON object: {"team": "bi"}.')
    ] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Create a Spark cluster, which is paid for while it runs; prints the operation.

    The collection, the cloud environment, the name and `config` are required, from the flags
    or --body-file. `lakehouseoperations get <operation_id>` says how the operation ended.
    """
    flags = {
        "collectionId": collection_id,
        "cloudEnvironmentId": cloud_environment_id,
        "name": name,
        "config": config,
        "description": description,
        "labels": labels,
    }
    given = {
        key: json.loads(value) if key in {"config", "labels"} else value
        for key, value in flags.items()
        if value is not None
    }
    # The request whole: the flags over -F over the file, and a field that is not of it refused.
    body = CreateSparkClusterArgs.model_validate(caller.over(given))
    return datalens.sparkclusters.create(
        collection_id=body.collection_id,
        cloud_environment_id=body.cloud_environment_id,
        name=body.name,
        config=body.config,
        description=body.description,
        labels=body.labels,
    )


@app.command()
def delete(cluster_id: SparkClusterIDArg, *, datalens: DataLensClient) -> LakehouseOperation:
    """Delete a Spark cluster; prints the operation that deletes it."""
    return datalens.sparkclusters.delete(cluster_id)


@app.command()
def start(cluster_id: SparkClusterIDArg, *, datalens: DataLensClient) -> LakehouseOperation:
    """Start a stopped Spark cluster, which is paid for while it runs; prints the operation."""
    return datalens.sparkclusters.start(cluster_id)


@app.command()
def stop(cluster_id: SparkClusterIDArg, *, datalens: DataLensClient) -> LakehouseOperation:
    """Stop a running Spark cluster; prints the operation."""
    return datalens.sparkclusters.stop(cluster_id)


@app.command("resource-presets-list")
def resource_presets_list(
    cloud_environment_id: EnvironmentOption,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[SparkResourcePreset]:
    """List the sizes an instance of a Spark cluster can take (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.sparkclusters.resource_presets_list(cloud_environment_id, limit=cap, next=next_)


@app.command("resource-presets-get")
def resource_presets_get(
    resource_preset_id: Annotated[
        str, typer.Argument(metavar="RESOURCE_PRESET_ID", help="Resource preset id.")
    ],
    cloud_environment_id: EnvironmentOption,
    *,
    datalens: DataLensClient,
) -> SparkResourcePreset:
    """Print one resource preset: its cores and its memory."""
    return datalens.sparkclusters.resource_presets_get(
        resource_preset_id, cloud_environment_id=cloud_environment_id
    )
