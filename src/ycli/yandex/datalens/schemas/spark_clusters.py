# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class ListSparkClustersArgs(RequestBody):
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of Spark clusters to return. The default is 100.",
        ge=0,
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of Spark clusters.",
    )
    filter: list[str] | None = Field(
        default=None,
        description="Filter expressions applied to the Spark cluster list.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the DataLens collection that contains the Spark clusters.",
        max_length=50,
        min_length=1,
    )


class GetSparkClusterArgs(RequestBody):
    id: str = Field(
        ...,
        description="ID of the Spark cluster to return.",
        max_length=50,
        min_length=1,
    )


class Labels(RootModel[str]):
    root: str = Field(..., max_length=63, pattern="^[-_0-9a-z]*$")


class DeleteSparkClusterArgs(RequestBody):
    id: str = Field(
        ...,
        description="ID of the Spark cluster to delete.",
        max_length=50,
        min_length=1,
    )


class StartSparkClusterArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster to start.",
        max_length=50,
        min_length=1,
    )


class StopSparkClusterArgs(RequestBody):
    cluster_id: str = Field(
        ...,
        alias="clusterId",
        description="ID of the Spark cluster to stop.",
        max_length=50,
        min_length=1,
    )


class SparkResourcePreset(APIModel):
    id: str = Field(..., description="ID of the resource preset.", min_length=1)
    cores: str = Field(
        ..., description="Number of CPU cores for an instance created with the preset."
    )
    memory: str = Field(
        ..., description="RAM volume for an instance created with the preset, in bytes."
    )


class ListSparkResourcePresetsResult(APIModel):
    resource_presets: list[SparkResourcePreset] = Field(
        ...,
        alias="resourcePresets",
        description="Spark resource presets available in the cloud environment.",
    )
    next_page_token: str = Field(
        ...,
        alias="nextPageToken",
        description="Token for the next page of resource presets.",
    )


class ListSparkResourcePresetsArgs(RequestBody):
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


class GetSparkResourcePresetArgs(RequestBody):
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


class SparkClusterConfigResourcePoolsDriverScalePolicyVariant1FixedScale(APIModel):
    size: str = Field(
        ...,
        description="Number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )


class SparkClusterConfigResourcePoolsDriverScalePolicyVariant2AutoScale(APIModel):
    min_size: str = Field(
        ...,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )
    max_size: str = Field(
        ...,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )
    initial_size: str = Field(
        ...,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )


class SparkClusterConfigResourcePoolsExecutorScalePolicyVariant1FixedScale(APIModel):
    size: str = Field(
        ...,
        description="Number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )


class SparkClusterConfigResourcePoolsExecutorScalePolicyVariant2AutoScale(APIModel):
    min_size: str = Field(
        ...,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )
    max_size: str = Field(
        ...,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )
    initial_size: str = Field(
        ...,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )


class SparkClusterConfigDependencies(APIModel):
    """Packages installed in the cluster."""

    pip_packages: list[str] = Field(
        ...,
        alias="pipPackages",
        description="Python packages installed in the cluster.",
    )
    deb_packages: list[str] = Field(
        ...,
        alias="debPackages",
        description="Debian packages installed in the cluster.",
    )


class SparkClusterConfigLogging(APIModel):
    """Cluster logging configuration."""

    enabled: bool = Field(..., description="Whether cluster logging is enabled.")


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1FixedScale(APIModel):
    size: str = Field(
        ...,
        description="Number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2AutoScale(APIModel):
    min_size: str = Field(
        ...,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )
    max_size: str = Field(
        ...,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )
    initial_size: str = Field(
        ...,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1FixedScale(APIModel):
    size: str = Field(
        ...,
        description="Number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2AutoScale(APIModel):
    min_size: str = Field(
        ...,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )
    max_size: str = Field(
        ...,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )
    initial_size: str = Field(
        ...,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
        pattern="^(?:0|[1-9]\\d?|100)$",
    )


class CreateSparkClusterArgsConfigDependencies(APIModel):
    """Packages to install in the cluster."""

    pip_packages: list[str] | None = Field(
        default=None,
        alias="pipPackages",
        description="Python packages to install in the cluster.",
    )
    deb_packages: list[str] | None = Field(
        default=None,
        alias="debPackages",
        description="Debian packages to install in the cluster.",
    )


class CreateSparkClusterArgsConfigLogging(APIModel):
    """Cluster logging configuration."""

    enabled: bool = Field(..., description="Whether cluster logging is enabled.")


class SparkClusterConfigResourcePoolsDriverScalePolicyVariant1(APIModel):
    fixed_scale: SparkClusterConfigResourcePoolsDriverScalePolicyVariant1FixedScale = Field(
        ..., alias="fixedScale"
    )
    scale_type: Literal["fixedScale"] = Field(..., alias="scaleType")


class SparkClusterConfigResourcePoolsDriverScalePolicyVariant2(APIModel):
    auto_scale: SparkClusterConfigResourcePoolsDriverScalePolicyVariant2AutoScale = Field(
        ..., alias="autoScale"
    )
    scale_type: Literal["autoScale"] = Field(..., alias="scaleType")


class SparkClusterConfigResourcePoolsExecutorScalePolicyVariant1(APIModel):
    fixed_scale: SparkClusterConfigResourcePoolsExecutorScalePolicyVariant1FixedScale = Field(
        ..., alias="fixedScale"
    )
    scale_type: Literal["fixedScale"] = Field(..., alias="scaleType")


class SparkClusterConfigResourcePoolsExecutorScalePolicyVariant2(APIModel):
    auto_scale: SparkClusterConfigResourcePoolsExecutorScalePolicyVariant2AutoScale = Field(
        ..., alias="autoScale"
    )
    scale_type: Literal["autoScale"] = Field(..., alias="scaleType")


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1(APIModel):
    fixed_scale: CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1FixedScale = (
        Field(..., alias="fixedScale")
    )


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2(APIModel):
    auto_scale: CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2AutoScale = Field(
        ..., alias="autoScale"
    )


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1(APIModel):
    fixed_scale: CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1FixedScale = (
        Field(..., alias="fixedScale")
    )


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2(APIModel):
    auto_scale: CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2AutoScale = (
        Field(..., alias="autoScale")
    )


class SparkClusterConfigResourcePoolsDriver(APIModel):
    """Driver resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: (
        SparkClusterConfigResourcePoolsDriverScalePolicyVariant1
        | SparkClusterConfigResourcePoolsDriverScalePolicyVariant2
    ) = Field(..., alias="scalePolicy", description="Resource pool scaling policy.")


class SparkClusterConfigResourcePoolsExecutor(APIModel):
    """Executor resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: (
        SparkClusterConfigResourcePoolsExecutorScalePolicyVariant1
        | SparkClusterConfigResourcePoolsExecutorScalePolicyVariant2
    ) = Field(..., alias="scalePolicy", description="Resource pool scaling policy.")


class CreateSparkClusterArgsConfigResourcePoolsDriver(APIModel):
    """Driver resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: (
        CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1
        | CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2
    ) = Field(..., alias="scalePolicy", description="Resource pool scaling policy.")


class CreateSparkClusterArgsConfigResourcePoolsExecutor(APIModel):
    """Executor resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: (
        CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1
        | CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2
    ) = Field(..., alias="scalePolicy", description="Resource pool scaling policy.")


class SparkClusterConfigResourcePools(APIModel):
    driver: SparkClusterConfigResourcePoolsDriver
    executor: SparkClusterConfigResourcePoolsExecutor


class CreateSparkClusterArgsConfigResourcePools(APIModel):
    driver: CreateSparkClusterArgsConfigResourcePoolsDriver
    executor: CreateSparkClusterArgsConfigResourcePoolsExecutor


class SparkClusterConfig(APIModel):
    spark_version: str = Field(
        ..., alias="sparkVersion", description="Spark version used by the cluster."
    )
    resource_pools: SparkClusterConfigResourcePools = Field(..., alias="resourcePools")
    dependencies: SparkClusterConfigDependencies | None
    logging: SparkClusterConfigLogging | None


class CreateSparkClusterArgsConfig(APIModel):
    spark_version: str | None = Field(
        default=None,
        alias="sparkVersion",
        description="Spark version. The service default is used when omitted.",
    )
    resource_pools: CreateSparkClusterArgsConfigResourcePools = Field(..., alias="resourcePools")
    dependencies: CreateSparkClusterArgsConfigDependencies | None = None
    logging: CreateSparkClusterArgsConfigLogging | None = None


class SparkCluster(APIModel):
    id: str = Field(..., description="ID of the Spark cluster.", min_length=1)
    cluster_id: str = Field(..., alias="clusterId", description="ID of the managed Spark cluster.")
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
    name: str = Field(..., description="Name of the Spark cluster.", min_length=1)
    description: str = Field(..., description="Description of the Spark cluster.")
    labels: dict[str, str] = Field(..., description="Spark cluster labels.")
    config: SparkClusterConfig
    health: Literal["HEALTH_UNKNOWN", "ALIVE", "DEAD", "DEGRADED"] | str = Field(
        ..., description="Aggregated health of the Spark cluster."
    )
    status: (
        Literal[
            "STATUS_UNSPECIFIED",
            "CREATING",
            "RUNNING",
            "UPDATING",
            "ERROR",
            "STOPPING",
            "STOPPED",
            "STARTING",
        ]
        | str
    ) = Field(..., description="Current status of the Spark cluster.")
    entry_id: str = Field(
        ...,
        alias="entryId",
        description="ID of the DataLens entry of the Spark cluster. Empty when the cluster has no entry.",
    )


class ListSparkClustersResult(APIModel):
    spark_clusters: list[SparkCluster] = Field(
        ..., alias="sparkClusters", description="Spark clusters matching the request."
    )
    next_page_token: str = Field(
        ...,
        alias="nextPageToken",
        description="Token for the next page of Spark clusters.",
    )


class CreateSparkClusterArgs(RequestBody):
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
        description="Name of the Spark cluster.",
        max_length=63,
        pattern="^[a-zA-Z0-9ЁёА-я]\\S{1,61}[a-zA-Z0-9ЁёА-я]$",
    )
    description: str | None = Field(
        default=None, description="Description of the Spark cluster.", max_length=200
    )
    labels: dict[str, Labels] | None = Field(default=None, description="Spark cluster labels.")
    config: CreateSparkClusterArgsConfig
