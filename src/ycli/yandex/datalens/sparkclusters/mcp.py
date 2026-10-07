"""DataLens Spark clusters FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    app_config,
    datalens_client,
)
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.sparkclusters.models import (
    NewClusterConfig,
    SparkCluster,
    SparkResourcePreset,
)
from ycli.yandex.models import ItemList

mcp = FastMCP("datalens-sparkclusters")

ClusterID = Annotated[str, Field(description="Spark cluster id.")]
Environment = Annotated[str, Field(description="The cloud environment the presets are for.")]


@mcp.tool(name="sparkclusters_list", annotations={**RO, "title": "List DataLens Spark clusters"})
def list_(
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max clusters to return; {LIMIT_CAP}")
    ] = None,
    collection_id: Annotated[
        str | None, Field(description="Keep the clusters of one collection.")
    ] = None,
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None, Field(description="Filter expressions of the API.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[SparkCluster]:
    """The Spark clusters of DataLens, auto-paginated.

    Experimental API, not measured: ycli follows its document. Capped at the configured item
    cap unless ``limit`` is given.
    """
    return client.sparkclusters.list(
        limit=config.http.cap(limit), collection_id=collection_id, filter=filter
    )


@mcp.tool(name="sparkclusters_get", annotations={**RO, "title": "Get DataLens Spark cluster"})
def get(
    id: ClusterID,  # noqa: A002  # the API's own name for it
    client: DataLensClient = Depends(datalens_client),
) -> SparkCluster:
    """One Spark cluster: its settings, health and status. Experimental API, not measured."""
    return client.sparkclusters.get(id)


@mcp.tool(
    name="sparkclusters_create", annotations={**WRITE, "title": "Create DataLens Spark cluster"}
)
def create(
    collection_id: Annotated[str, Field(description="The collection to create the cluster in.")],
    cloud_environment_id: Annotated[
        str, Field(description="The cloud environment the cluster runs in.")
    ],
    name: Annotated[str, Field(description="The cluster's name.")],
    config: Annotated[
        NewClusterConfig,
        Field(description="The Spark version and the pools of the driver and executors."),
    ],
    description: Annotated[str | None, Field(description="A description of the cluster.")] = None,
    labels: Annotated[dict[str, str] | None, Field(description="Labels of the cluster.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Create a Spark cluster and return the operation that creates it.

    A cluster is paid for while it runs: create one only when asked to. The operation goes on
    after the reply: ``lakehouseoperations_get`` with its ``id`` says how it ended. Experimental
    API, not measured.
    """
    return client.sparkclusters.create(
        collection_id=collection_id,
        cloud_environment_id=cloud_environment_id,
        name=name,
        config=config,
        description=description,
        labels=labels,
    )


@mcp.tool(
    name="sparkclusters_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens Spark cluster"},
)
def delete(
    id: ClusterID,  # noqa: A002  # the API's own name for it
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Delete a Spark cluster and return the operation; ``lakehouseoperations_get`` reads it.

    Experimental API, not measured.
    """
    return client.sparkclusters.delete(id)


@mcp.tool(
    name="sparkclusters_start", annotations={**WRITE, "title": "Start DataLens Spark cluster"}
)
def start(
    cluster_id: ClusterID, client: DataLensClient = Depends(datalens_client)
) -> LakehouseOperation:
    """Start a stopped Spark cluster and return the operation.

    A cluster is paid for while it runs: start one only when asked to. ``lakehouseoperations_get``
    says how the operation ended. Experimental API, not measured.
    """
    return client.sparkclusters.start(cluster_id)


@mcp.tool(name="sparkclusters_stop", annotations={**WRITE, "title": "Stop DataLens Spark cluster"})
def stop(
    cluster_id: ClusterID, client: DataLensClient = Depends(datalens_client)
) -> LakehouseOperation:
    """Stop a running Spark cluster and return the operation; ``lakehouseoperations_get`` reads it.

    Experimental API, not measured.
    """
    return client.sparkclusters.stop(cluster_id)


@mcp.tool(
    name="sparkclusters_resource_presets_list",
    annotations={**RO, "title": "List DataLens Spark resource presets"},
)
def resource_presets_list(
    cloud_environment_id: Environment,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max presets to return; {LIMIT_CAP}")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[SparkResourcePreset]:
    """The sizes an instance of a Spark cluster can take, auto-paginated.

    Experimental API, not measured. Capped at the configured item cap unless ``limit`` is given.
    """
    return client.sparkclusters.resource_presets_list(
        cloud_environment_id, limit=config.http.cap(limit)
    )


@mcp.tool(
    name="sparkclusters_resource_presets_get",
    annotations={**RO, "title": "Get DataLens Spark resource preset"},
)
def resource_presets_get(
    resource_preset_id: Annotated[str, Field(description="Resource preset id.")],
    cloud_environment_id: Environment,
    client: DataLensClient = Depends(datalens_client),
) -> SparkResourcePreset:
    """One resource preset: its cores and its memory. Experimental API, not measured."""
    return client.sparkclusters.resource_presets_get(
        resource_preset_id, cloud_environment_id=cloud_environment_id
    )
