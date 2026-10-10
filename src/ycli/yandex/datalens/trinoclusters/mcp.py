"""DataLens Trino clusters FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    All,
    Next,
    app_config,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.trinoclusters.models import (
    TrinoCatalogToAdd,
    TrinoCluster,
    TrinoNewCatalog,
    TrinoResourcePreset,
    TrinoWorkerConfig,
)
from ycli.yandex.models import Listed

mcp = new_server("datalens-trinoclusters")

TrinoClusterID = Annotated[str, Field(description="Id of the Trino cluster.")]
PresetEnvironment = Annotated[str, Field(description="The cloud environment the presets are of.")]


@mcp.tool(name="trinoclusters_list", annotations={**RO, "title": "List DataLens Trino clusters"})
def list_(
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None, Field(description="Conditions the clusters must meet.")
    ] = None,
    collection_id: Annotated[
        str | None, Field(description="Only the clusters of this collection.")
    ] = None,
    catalog_id: Annotated[
        str | None, Field(description="Only the clusters this REST catalog is attached to.")
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max clusters to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[TrinoCluster]:
    """The Trino clusters of the DataLens instance, auto-paginated.

    Experimental in the DataLens API. An instance with none answers an empty list.
    """
    return client.trinoclusters.list(
        filter=filter,
        collection_id=collection_id,
        catalog_id=catalog_id,
        limit=config.http.cap(limit, all_=all),
        next=next,
    ).collect()


@mcp.tool(name="trinoclusters_get", annotations={**RO, "title": "Get DataLens Trino cluster"})
def get(
    id: TrinoClusterID,  # noqa: A002  # the API's own name for it
    client: DataLensClient = Depends(datalens_client),
) -> TrinoCluster:
    """One Trino cluster: its configuration, its health, its status and its coordinator.

    Experimental in the DataLens API and written from its document: not measured. An id
    nothing knows answers 403 Permission denied, not 404: it is not a lack of rights.
    """
    return client.trinoclusters.get(id)


@mcp.tool(
    name="trinoclusters_create", annotations={**WRITE, "title": "Create DataLens Trino cluster"}
)
def create(
    collection_id: Annotated[str, Field(description="The DataLens collection to make it in.")],
    cloud_environment_id: Annotated[str, Field(description="The cloud environment to make it in.")],
    name: Annotated[str, Field(description="The cluster's name.")],
    worker_config: Annotated[
        TrinoWorkerConfig,
        Field(description="The workers: their resource preset and how many there may be."),
    ],
    description: Annotated[str | None, Field(description="A description.")] = None,
    labels: Annotated[
        dict[str, str] | None, Field(description="Labels, a name to a value.")
    ] = None,
    catalogs_config: Annotated[
        list[TrinoNewCatalog] | None, Field(description="The REST catalogs to attach.")
    ] = None,
    trino_version: Annotated[
        str | None, Field(description="The version of Trino; the service's own when left out.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Make a Trino cluster and return the operation that makes it.

    A cluster is cloud resources, billed while it runs: ask the person before calling.
    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.trinoclusters.create(
        collection_id=collection_id,
        cloud_environment_id=cloud_environment_id,
        name=name,
        worker_config=worker_config,
        description=description,
        labels=labels,
        catalogs_config=catalogs_config,
        trino_version=trino_version,
    )


@mcp.tool(
    name="trinoclusters_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens Trino cluster"},
)
def delete(
    id: TrinoClusterID,  # noqa: A002  # the API's own name for it
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Delete a Trino cluster and return the operation that deletes it.

    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.trinoclusters.delete(id)


@mcp.tool(
    name="trinoclusters_start", annotations={**WRITE, "title": "Start DataLens Trino cluster"}
)
def start(
    cluster_id: TrinoClusterID, client: DataLensClient = Depends(datalens_client)
) -> LakehouseOperation:
    """Start a stopped Trino cluster and return the operation that starts it.

    A running cluster is billed: ask the person before calling. Experimental in the DataLens
    API, written from its document and never called: not measured.
    """
    return client.trinoclusters.start(cluster_id)


@mcp.tool(name="trinoclusters_stop", annotations={**WRITE, "title": "Stop DataLens Trino cluster"})
def stop(
    cluster_id: TrinoClusterID, client: DataLensClient = Depends(datalens_client)
) -> LakehouseOperation:
    """Stop a running Trino cluster and return the operation that stops it.

    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.trinoclusters.stop(cluster_id)


@mcp.tool(
    name="trinoclusters_catalog_create",
    annotations={**WRITE, "title": "Attach a REST catalog to a DataLens Trino cluster"},
)
def catalog_create(
    cluster_id: TrinoClusterID,
    catalog: Annotated[
        TrinoCatalogToAdd, Field(description="The REST catalog to attach, by its id.")
    ],
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Attach a REST catalog to a Trino cluster and return the operation.

    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.trinoclusters.catalog_create(cluster_id, catalog=catalog)


@mcp.tool(
    name="trinoclusters_catalog_delete",
    annotations={**DESTRUCTIVE, "title": "Detach a REST catalog from a DataLens Trino cluster"},
)
def catalog_delete(
    cluster_id: TrinoClusterID,
    catalog_id: Annotated[str, Field(description="The id of the REST catalog to detach.")],
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Detach a REST catalog from a Trino cluster; the catalog itself stays.

    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.trinoclusters.catalog_delete(cluster_id, catalog_id=catalog_id)


@mcp.tool(
    name="trinoclusters_resource_presets_list",
    annotations={**RO, "title": "List DataLens Trino resource presets"},
)
def resource_presets_list(
    cloud_environment_id: PresetEnvironment,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max presets to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[TrinoResourcePreset]:
    """The sizes a cluster's machines may have in a cloud environment, auto-paginated.

    Experimental in the DataLens API and written from its document: not measured. An
    environment nothing knows answers 403 Permission denied, not 404.
    """
    return client.trinoclusters.resource_presets_list(
        cloud_environment_id, limit=config.http.cap(limit, all_=all), next=next
    ).collect()


@mcp.tool(
    name="trinoclusters_resource_preset_get",
    annotations={**RO, "title": "Get DataLens Trino resource preset"},
)
def resource_preset_get(
    resource_preset_id: Annotated[str, Field(description="Id of the resource preset.")],
    cloud_environment_id: PresetEnvironment,
    client: DataLensClient = Depends(datalens_client),
) -> TrinoResourcePreset:
    """One size of a cluster's machines: its cores and its memory.

    Experimental in the DataLens API and written from its document: not measured.
    """
    return client.trinoclusters.resource_preset_get(
        resource_preset_id, cloud_environment_id=cloud_environment_id
    )
