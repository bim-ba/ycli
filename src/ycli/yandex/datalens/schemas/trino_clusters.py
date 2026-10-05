# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class ListTrinoClustersArgs(RequestBody):
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of Trino clusters to return. The default is 100.",
        ge=0,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of Trino clusters.",
    )
    filter: list[str] | None = Field(
        default=None,
        description="Filter expressions applied to the Trino cluster list.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the DataLens collection that contains the Trino clusters.",
        max_length=50,
        min_length=1,
    )
    catalog_id: str | None = Field(
        default=None,
        alias="catalogId",
        description="ID of the REST catalog attached to the Trino clusters.",
        max_length=50,
        min_length=1,
    )


class GetTrinoClusterArgs(RequestBody):
    id: str = Field(
        ...,
        description="ID of the Trino cluster to return.",
        max_length=50,
        min_length=1,
    )


class Labels(RootModel[str]):
    root: str = Field(..., max_length=63, pattern="^[-_0-9a-z]*$")


class DeleteTrinoClusterArgs(RequestBody):
    id: str = Field(
        ...,
        description="ID of the Trino cluster to delete.",
        max_length=50,
        min_length=1,
    )


class StartTrinoClusterArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Trino cluster to start.",
        max_length=50,
        min_length=1,
    )


class StopTrinoClusterArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Trino cluster to stop.",
        max_length=50,
        min_length=1,
    )


class DeleteTrinoClusterCatalogArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Trino cluster.",
        max_length=50,
        min_length=1,
    )
    catalog_id: str = Field(
        ...,
        alias="catalogId",
        description="ID of the REST catalog to detach.",
        max_length=50,
        min_length=1,
    )


class TrinoResourcePreset(APIModel):
    id: str = Field(..., description="ID of the resource preset.", min_length=1)
    cores: str = Field(
        ..., description="Number of CPU cores for an instance created with the preset."
    )
    memory: str = Field(
        ..., description="RAM volume for an instance created with the preset, in bytes."
    )


class ListTrinoResourcePresetsResult(APIModel):
    resource_presets: list[TrinoResourcePreset] = Field(
        ...,
        alias="resourcePresets",
        description="Trino resource presets available in the cloud environment.",
    )
    next_page_token: str = Field(
        ...,
        alias="nextPageToken",
        description="Token for the next page of resource presets.",
    )


class ListTrinoResourcePresetsArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment to list resource presets for.",
        max_length=50,
        min_length=1,
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of resource presets to return.",
        ge=0,
        le=1000,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of resource presets.",
        max_length=100,
    )


class GetTrinoResourcePresetArgs(RequestBody):
    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the resource preset to return.",
        max_length=50,
        min_length=1,
    )
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment the resource preset is requested for.",
        max_length=50,
        min_length=1,
    )


class TrinoClusterConfigCatalogsConfigItem(APIModel):
    catalog_id: str = Field(
        ...,
        alias="catalogId",
        description="ID of the REST catalog.",
        max_length=50,
        min_length=1,
    )


class TrinoClusterConfigCoordinatorConfigResources(APIModel):
    """Resources assigned to the coordinator."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Trino resource preset.",
        max_length=50,
        min_length=1,
    )


class TrinoClusterConfigWorkerConfigResources(APIModel):
    """Resources assigned to each worker."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Trino resource preset.",
        max_length=50,
        min_length=1,
    )


class TrinoClusterConfigWorkerConfigScalePolicyAutoScale(APIModel):
    min_count: str = Field(
        ...,
        alias="minCount",
        description="Minimum number of worker instances.",
        pattern="^(?:0|[1-5]?\\d|6[0-4])$",
    )
    max_count: str = Field(
        ...,
        alias="maxCount",
        description="Maximum number of worker instances.",
        pattern="^(?:[1-9]|[1-5]\\d|6[0-4])$",
    )


class CreateTrinoClusterArgsCatalogsConfigItem(APIModel):
    catalog_id: str = Field(
        ...,
        alias="catalogId",
        description="ID of the REST catalog.",
        max_length=50,
        min_length=1,
    )


class CreateTrinoClusterArgsWorkerConfigResources(APIModel):
    """Resources assigned to each worker."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Trino resource preset.",
        max_length=50,
        min_length=1,
    )


class CreateTrinoClusterArgsWorkerConfigScalePolicyAutoScale(APIModel):
    min_count: str = Field(
        ...,
        alias="minCount",
        description="Minimum number of worker instances.",
        pattern="^(?:0|[1-5]?\\d|6[0-4])$",
    )
    max_count: str = Field(
        ...,
        alias="maxCount",
        description="Maximum number of worker instances.",
        pattern="^(?:[1-9]|[1-5]\\d|6[0-4])$",
    )


class AddTrinoClusterCatalogArgsCatalog(APIModel):
    """REST catalog to attach to the cluster."""

    catalog_id: str = Field(
        ...,
        alias="catalogId",
        description="ID of the REST catalog.",
        max_length=50,
        min_length=1,
    )


class AddTrinoClusterCatalogArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Trino cluster.",
        max_length=50,
        min_length=1,
    )
    catalog: AddTrinoClusterCatalogArgsCatalog


class TrinoClusterConfigCoordinatorConfig(APIModel):
    resources: TrinoClusterConfigCoordinatorConfigResources


class TrinoClusterConfigWorkerConfigScalePolicy(APIModel):
    auto_scale: TrinoClusterConfigWorkerConfigScalePolicyAutoScale = Field(..., alias="autoScale")
    scale_type: Literal["autoScale"] = Field(..., alias="scaleType")


class CreateTrinoClusterArgsWorkerConfigScalePolicy(APIModel):
    auto_scale: CreateTrinoClusterArgsWorkerConfigScalePolicyAutoScale = Field(
        ..., alias="autoScale"
    )


class TrinoClusterConfigWorkerConfig(APIModel):
    resources: TrinoClusterConfigWorkerConfigResources
    scale_policy: TrinoClusterConfigWorkerConfigScalePolicy = Field(..., alias="scalePolicy")


class CreateTrinoClusterArgsWorkerConfig(APIModel):
    resources: CreateTrinoClusterArgsWorkerConfigResources
    scale_policy: CreateTrinoClusterArgsWorkerConfigScalePolicy = Field(..., alias="scalePolicy")


class CreateTrinoClusterArgs(RequestBody):
    collection_id: str = Field(
        ...,
        alias="collectionId",
        description="ID of the DataLens collection in which to create the cluster.",
        max_length=50,
        min_length=1,
    )
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment in which to create the cluster.",
        max_length=50,
        min_length=1,
    )
    name: str = Field(
        ...,
        description="Name of the Trino cluster.",
        max_length=63,
        min_length=1,
        pattern="^[a-zA-Z0-9_-]+$",
    )
    description: str | None = Field(
        default=None, description="Description of the Trino cluster.", max_length=256
    )
    labels: dict[str, Labels] | None = Field(default=None, description="Trino cluster labels.")
    catalogs_config: list[CreateTrinoClusterArgsCatalogsConfigItem] | None = Field(
        default=None,
        alias="catalogsConfig",
        description="REST catalogs to attach to the cluster.",
    )
    worker_config: CreateTrinoClusterArgsWorkerConfig = Field(..., alias="workerConfig")
    trino_version: str | None = Field(
        default=None,
        alias="trinoVersion",
        description="Trino version. The service default is used when omitted.",
    )


class TrinoClusterConfig(APIModel):
    trino_version: str = Field(
        ..., alias="trinoVersion", description="Trino version used by the cluster."
    )
    catalogs_config: list[TrinoClusterConfigCatalogsConfigItem] = Field(
        ...,
        alias="catalogsConfig",
        description="REST catalogs attached to the cluster.",
    )
    coordinator_config: TrinoClusterConfigCoordinatorConfig = Field(..., alias="coordinatorConfig")
    worker_config: TrinoClusterConfigWorkerConfig = Field(..., alias="workerConfig")


class TrinoCluster(APIModel):
    id: str = Field(..., description="ID of the Trino cluster.", min_length=1)
    cluster_id: str = Field(..., alias="clusterId", description="ID of the managed Trino cluster.")
    collection_id: str = Field(
        ...,
        alias="collectionId",
        description="ID of the DataLens collection that contains the cluster.",
        min_length=1,
    )
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the associated cloud environment.",
        min_length=1,
    )
    name: str = Field(..., description="Name of the Trino cluster.", min_length=1)
    description: str = Field(..., description="Description of the Trino cluster.")
    labels: dict[str, str] = Field(..., description="Trino cluster labels.")
    config: TrinoClusterConfig
    health: Literal["HEALTH_UNKNOWN", "ALIVE", "DEAD", "DEGRADED"] | str = Field(
        ..., description="Aggregated health of the Trino cluster."
    )
    status: (
        Literal[
            "STATUS_UNKNOWN",
            "CREATING",
            "RUNNING",
            "ERROR",
            "STOPPING",
            "STOPPED",
            "STARTING",
            "UPDATING",
        ]
        | str
    ) = Field(..., description="Current status of the Trino cluster.")
    coordinator_url: str = Field(
        ..., alias="coordinatorUrl", description="Address of the Trino coordinator."
    )
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the DataLens entry of the Trino cluster. Empty when the cluster has no entry.",
    )


class ListTrinoClustersResult(APIModel):
    clusters: list[TrinoCluster] = Field(..., description="Trino clusters matching the request.")
    next_page_token: str = Field(
        ...,
        alias="nextPageToken",
        description="Token for the next page of Trino clusters.",
    )
