"""DataLens Trino cluster operations, declared once (sans-IO).

Every one of them is marked experimental in the document DataLens publishes.

Examples:
    >>> start("tc1").body
    {'clusterId': 'tc1'}
"""

from collections.abc import Mapping, Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.schemas.trino_clusters import (
    AddTrinoClusterCatalogArgs,
    CreateTrinoClusterArgs,
    DeleteTrinoClusterArgs,
    DeleteTrinoClusterCatalogArgs,
    GetTrinoClusterArgs,
    GetTrinoResourcePresetArgs,
    ListTrinoClustersArgs,
    ListTrinoResourcePresetsArgs,
    StartTrinoClusterArgs,
    StopTrinoClusterArgs,
)
from ycli.yandex.datalens.trinoclusters.models import (
    TrinoCatalogToAdd,
    TrinoCluster,
    TrinoClustersPage,
    TrinoNewCatalog,
    TrinoResourcePreset,
    TrinoResourcePresetsPage,
    TrinoWorkerConfig,
)


def list_(
    *,
    filter: Sequence[str] | None,  # noqa: A002  # the API's own name for it
    collection_id: str | None,
    catalog_id: str | None,
) -> Paged[TrinoClustersPage, TrinoCluster]:
    body = ListTrinoClustersArgs(
        filter=None if filter is None else list(filter),
        collectionId=collection_id,
        catalogId=catalog_id,
    )
    return Paged(
        RPC("listTrinoClusters", TrinoClustersPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.clusters or [],
    )


def get(
    id: str,  # noqa: A002  # the API's own name for it
) -> Endpoint[TrinoCluster]:
    return RPC("getTrinoCluster", TrinoCluster, json=GetTrinoClusterArgs(id=id), effect=Effect.READ)


def create(
    *,
    collection_id: str,
    cloud_environment_id: str,
    name: str,
    worker_config: TrinoWorkerConfig,
    description: str | None,
    labels: Mapping[str, str] | None,
    catalogs_config: Sequence[TrinoNewCatalog] | None,
    trino_version: str | None,
) -> Endpoint[LakehouseOperation]:
    body = CreateTrinoClusterArgs(
        collectionId=collection_id,
        cloudEnvironmentId=cloud_environment_id,
        name=name,
        workerConfig=worker_config,
        description=description,
        labels=None if labels is None else dict(labels),
        catalogsConfig=None if catalogs_config is None else list(catalogs_config),
        trinoVersion=trino_version,
    )
    return RPC("createTrinoCluster", LakehouseOperation, json=body, effect=Effect.WRITE)


def delete(
    id: str,  # noqa: A002  # the API's own name for it
) -> Endpoint[LakehouseOperation]:
    body = DeleteTrinoClusterArgs(id=id)
    return RPC("deleteTrinoCluster", LakehouseOperation, json=body, effect=Effect.DESTRUCTIVE)


def start(cluster_id: str) -> Endpoint[LakehouseOperation]:
    body = StartTrinoClusterArgs(clusterId=cluster_id)
    return RPC("startTrinoCluster", LakehouseOperation, json=body, effect=Effect.WRITE)


def stop(cluster_id: str) -> Endpoint[LakehouseOperation]:
    body = StopTrinoClusterArgs(clusterId=cluster_id)
    return RPC("stopTrinoCluster", LakehouseOperation, json=body, effect=Effect.WRITE)


def catalog_create(cluster_id: str, *, catalog: TrinoCatalogToAdd) -> Endpoint[LakehouseOperation]:
    body = AddTrinoClusterCatalogArgs(clusterId=cluster_id, catalog=catalog)
    return RPC("addTrinoClusterCatalog", LakehouseOperation, json=body, effect=Effect.WRITE)


def catalog_delete(cluster_id: str, *, catalog_id: str) -> Endpoint[LakehouseOperation]:
    # Destructive: the cluster loses the catalog; the catalog itself stays.
    body = DeleteTrinoClusterCatalogArgs(clusterId=cluster_id, catalogId=catalog_id)
    return RPC(
        "deleteTrinoClusterCatalog", LakehouseOperation, json=body, effect=Effect.DESTRUCTIVE
    )


def resource_presets_list(
    cloud_environment_id: str,
) -> Paged[TrinoResourcePresetsPage, TrinoResourcePreset]:
    body = ListTrinoResourcePresetsArgs(cloudEnvironmentId=cloud_environment_id)
    return Paged(
        RPC("listTrinoResourcePresets", TrinoResourcePresetsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.resource_presets or [],
    )


def resource_preset_get(
    resource_preset_id: str, *, cloud_environment_id: str
) -> Endpoint[TrinoResourcePreset]:
    body = GetTrinoResourcePresetArgs(
        resourcePresetId=resource_preset_id, cloudEnvironmentId=cloud_environment_id
    )
    return RPC("getTrinoResourcePreset", TrinoResourcePreset, json=body, effect=Effect.READ)
