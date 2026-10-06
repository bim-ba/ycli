"""DataLens Spark cluster operations, declared once (sans-IO).

Not measured: the API is experimental and a cluster is paid for, so every operation here
follows the document alone (#455).

Examples:
    >>> start("sc1").body
    {'clusterId': 'sc1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.schemas.spark_clusters import (
    CreateSparkClusterArgs,
    DeleteSparkClusterArgs,
    GetSparkClusterArgs,
    GetSparkResourcePresetArgs,
    ListSparkClustersArgs,
    ListSparkResourcePresetsArgs,
    StartSparkClusterArgs,
    StopSparkClusterArgs,
)
from ycli.yandex.datalens.sparkclusters.models import (
    NewClusterConfig,
    SparkCluster,
    SparkClustersPage,
    SparkResourcePreset,
    SparkResourcePresetsPage,
)


def list_(
    *,
    collection_id: str | None,
    filter: list[str] | None,  # noqa: A002  # the API's own name for it
) -> Paged[SparkClustersPage, SparkCluster]:
    body = ListSparkClustersArgs(collectionId=collection_id, filter=filter)
    return Paged(
        RPC("listSparkClusters", SparkClustersPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.spark_clusters or [],
    )


def get(id: str) -> Endpoint[SparkCluster]:  # noqa: A002  # the API's own name for it
    body = GetSparkClusterArgs(id=id)
    return RPC("getSparkCluster", SparkCluster, json=body, effect=Effect.READ)


def create(
    *,
    collection_id: str,
    cloud_environment_id: str,
    name: str,
    config: NewClusterConfig,
    description: str | None,
    labels: dict[str, str] | None,
) -> Endpoint[LakehouseOperation]:
    body = CreateSparkClusterArgs(
        collectionId=collection_id,
        cloudEnvironmentId=cloud_environment_id,
        name=name,
        config=config,
        description=description,
        labels=labels,
    )
    return RPC("createSparkCluster", LakehouseOperation, json=body, effect=Effect.WRITE)


def delete(id: str) -> Endpoint[LakehouseOperation]:  # noqa: A002  # the API's own name for it
    body = DeleteSparkClusterArgs(id=id)
    return RPC("deleteSparkCluster", LakehouseOperation, json=body, effect=Effect.DESTRUCTIVE)


def start(cluster_id: str) -> Endpoint[LakehouseOperation]:
    body = StartSparkClusterArgs(clusterId=cluster_id)
    return RPC("startSparkCluster", LakehouseOperation, json=body, effect=Effect.WRITE)


def stop(cluster_id: str) -> Endpoint[LakehouseOperation]:
    body = StopSparkClusterArgs(clusterId=cluster_id)
    return RPC("stopSparkCluster", LakehouseOperation, json=body, effect=Effect.WRITE)


def resource_presets_list(
    cloud_environment_id: str,
) -> Paged[SparkResourcePresetsPage, SparkResourcePreset]:
    body = ListSparkResourcePresetsArgs(cloudEnvironmentId=cloud_environment_id)
    return Paged(
        RPC("listSparkResourcePresets", SparkResourcePresetsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.resource_presets or [],
    )


def resource_presets_get(
    resource_preset_id: str, *, cloud_environment_id: str
) -> Endpoint[SparkResourcePreset]:
    body = GetSparkResourcePresetArgs(
        resourcePresetId=resource_preset_id, cloudEnvironmentId=cloud_environment_id
    )
    return RPC("getSparkResourcePreset", SparkResourcePreset, json=body, effect=Effect.READ)
