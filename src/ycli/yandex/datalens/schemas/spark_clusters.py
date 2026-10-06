# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class ListSparkClustersArgs(RequestBody):
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of Spark clusters to return. The default is 100.",
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
    )


class GetSparkClusterArgs(RequestBody):
    id: str = Field(..., description="ID of the Spark cluster to return.")


class DeleteSparkClusterArgs(RequestBody):
    id: str = Field(..., description="ID of the Spark cluster to delete.")


class StartSparkClusterArgs(RequestBody):
    cluster_id: str = Field(..., alias="clusterId", description="ID of the Spark cluster to start.")


class StopSparkClusterArgs(RequestBody):
    cluster_id: str = Field(..., alias="clusterId", description="ID of the Spark cluster to stop.")


class SparkResourcePreset(APIModel):
    id: str | None = Field(default=None, description="ID of the resource preset.")
    cores: str | None = Field(
        default=None,
        description="Number of CPU cores for an instance created with the preset.",
    )
    memory: str | None = Field(
        default=None,
        description="RAM volume for an instance created with the preset, in bytes.",
    )


class ListSparkResourcePresetsResult(APIModel):
    resource_presets: list[SparkResourcePreset] | None = Field(
        default=None,
        alias="resourcePresets",
        description="Spark resource presets available in the cloud environment.",
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of resource presets.",
    )


class ListSparkResourcePresetsArgs(RequestBody):
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment to list resource presets for.",
    )
    page_size: int | None = Field(
        default=None,
        alias="pageSize",
        description="Maximum number of resource presets to return.",
    )
    page_token: str | None = Field(
        default=None,
        alias="pageToken",
        description="Token for the next page of resource presets.",
    )


class GetSparkResourcePresetArgs(RequestBody):
    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the resource preset to return.",
    )
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment the resource preset is requested for.",
    )


class SparkClusterConfigResourcePoolsDriverScalePolicyFixedScale(APIModel):
    size: str | None = Field(default=None, description="Number of instances in the resource pool.")


class SparkClusterConfigResourcePoolsDriverScalePolicyAutoScale(APIModel):
    min_size: str | None = Field(
        default=None,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
    )
    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
    )
    initial_size: str | None = Field(
        default=None,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
    )


class SparkClusterConfigResourcePoolsExecutorScalePolicyFixedScale(APIModel):
    size: str | None = Field(default=None, description="Number of instances in the resource pool.")


class SparkClusterConfigResourcePoolsExecutorScalePolicyAutoScale(APIModel):
    min_size: str | None = Field(
        default=None,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
    )
    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
    )
    initial_size: str | None = Field(
        default=None,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
    )


class SparkClusterConfigDependencies(APIModel):
    """Packages installed in the cluster."""

    pip_packages: list[str] | None = Field(
        default=None,
        alias="pipPackages",
        description="Python packages installed in the cluster.",
    )
    deb_packages: list[str] | None = Field(
        default=None,
        alias="debPackages",
        description="Debian packages installed in the cluster.",
    )


class SparkClusterConfigLogging(APIModel):
    """Cluster logging configuration."""

    enabled: bool | None = Field(default=None, description="Whether cluster logging is enabled.")


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1FixedScale(APIModel):
    size: str | None = Field(default=None, description="Number of instances in the resource pool.")


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2AutoScale(APIModel):
    min_size: str | None = Field(
        default=None,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
    )
    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
    )
    initial_size: str | None = Field(
        default=None,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
    )


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1FixedScale(APIModel):
    size: str | None = Field(default=None, description="Number of instances in the resource pool.")


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2AutoScale(APIModel):
    min_size: str | None = Field(
        default=None,
        alias="minSize",
        description="Minimum number of instances in the resource pool.",
    )
    max_size: str | None = Field(
        default=None,
        alias="maxSize",
        description="Maximum number of instances in the resource pool.",
    )
    initial_size: str | None = Field(
        default=None,
        alias="initialSize",
        description="Initial number of instances in the resource pool.",
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

    enabled: bool | None = Field(default=None, description="Whether cluster logging is enabled.")


class SparkClusterConfigResourcePoolsDriverScalePolicy(APIModel):
    """Resource pool scaling policy."""

    fixed_scale: SparkClusterConfigResourcePoolsDriverScalePolicyFixedScale | None = Field(
        default=None, alias="fixedScale"
    )
    scale_type: Literal["fixedScale", "autoScale"] | str | None = Field(
        default=None, alias="scaleType"
    )
    auto_scale: SparkClusterConfigResourcePoolsDriverScalePolicyAutoScale | None = Field(
        default=None, alias="autoScale"
    )


class SparkClusterConfigResourcePoolsExecutorScalePolicy(APIModel):
    """Resource pool scaling policy."""

    fixed_scale: SparkClusterConfigResourcePoolsExecutorScalePolicyFixedScale | None = Field(
        default=None, alias="fixedScale"
    )
    scale_type: Literal["fixedScale", "autoScale"] | str | None = Field(
        default=None, alias="scaleType"
    )
    auto_scale: SparkClusterConfigResourcePoolsExecutorScalePolicyAutoScale | None = Field(
        default=None, alias="autoScale"
    )


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1(APIModel):
    fixed_scale: (
        CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1FixedScale | None
    ) = Field(default=None, alias="fixedScale")


class CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2(APIModel):
    auto_scale: (
        CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2AutoScale | None
    ) = Field(default=None, alias="autoScale")


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1(APIModel):
    fixed_scale: (
        CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1FixedScale | None
    ) = Field(default=None, alias="fixedScale")


class CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2(APIModel):
    auto_scale: (
        CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2AutoScale | None
    ) = Field(default=None, alias="autoScale")


class SparkClusterConfigResourcePoolsDriver(APIModel):
    """Driver resource pool."""

    resource_preset_id: str | None = Field(
        default=None,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
    )
    scale_policy: SparkClusterConfigResourcePoolsDriverScalePolicy | None = Field(
        default=None, alias="scalePolicy"
    )


class SparkClusterConfigResourcePoolsExecutor(APIModel):
    """Executor resource pool."""

    resource_preset_id: str | None = Field(
        default=None,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
    )
    scale_policy: SparkClusterConfigResourcePoolsExecutorScalePolicy | None = Field(
        default=None, alias="scalePolicy"
    )


class CreateSparkClusterArgsConfigResourcePoolsDriver(APIModel):
    """Driver resource pool."""

    resource_preset_id: str | None = Field(
        default=None,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
    )
    scale_policy: (
        CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant1
        | CreateSparkClusterArgsConfigResourcePoolsDriverScalePolicyVariant2
        | None
    ) = Field(default=None, alias="scalePolicy", description="Resource pool scaling policy.")


class CreateSparkClusterArgsConfigResourcePoolsExecutor(APIModel):
    """Executor resource pool."""

    resource_preset_id: str | None = Field(
        default=None,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
    )
    scale_policy: (
        CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant1
        | CreateSparkClusterArgsConfigResourcePoolsExecutorScalePolicyVariant2
        | None
    ) = Field(default=None, alias="scalePolicy", description="Resource pool scaling policy.")


class SparkClusterConfigResourcePools(APIModel):
    driver: SparkClusterConfigResourcePoolsDriver | None = None
    executor: SparkClusterConfigResourcePoolsExecutor | None = None


class CreateSparkClusterArgsConfigResourcePools(APIModel):
    driver: CreateSparkClusterArgsConfigResourcePoolsDriver | None = None
    executor: CreateSparkClusterArgsConfigResourcePoolsExecutor | None = None


class SparkClusterConfig(APIModel):
    spark_version: str | None = Field(
        default=None,
        alias="sparkVersion",
        description="Spark version used by the cluster.",
    )
    resource_pools: SparkClusterConfigResourcePools | None = Field(
        default=None, alias="resourcePools"
    )
    dependencies: SparkClusterConfigDependencies | None = None
    logging: SparkClusterConfigLogging | None = None


class CreateSparkClusterArgsConfig(APIModel):
    spark_version: str | None = Field(
        default=None,
        alias="sparkVersion",
        description="Spark version. The service default is used when omitted.",
    )
    resource_pools: CreateSparkClusterArgsConfigResourcePools | None = Field(
        default=None, alias="resourcePools"
    )
    dependencies: CreateSparkClusterArgsConfigDependencies | None = None
    logging: CreateSparkClusterArgsConfigLogging | None = None


class SparkCluster(APIModel):
    id: str | None = Field(default=None, description="ID of the Spark cluster.")
    cluster_id: str | None = Field(
        default=None, alias="clusterId", description="ID of the managed Spark cluster."
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the DataLens collection that contains the cluster.",
    )
    cloud_environment_id: str | None = Field(
        default=None,
        alias="cloudEnvironmentId",
        description="ID of the associated cloud environment.",
    )
    name: str | None = Field(default=None, description="Name of the Spark cluster.")
    description: str | None = Field(default=None, description="Description of the Spark cluster.")
    labels: dict[str, str] | None = Field(default=None, description="Spark cluster labels.")
    config: SparkClusterConfig | None = None
    health: Literal["HEALTH_UNKNOWN", "ALIVE", "DEAD", "DEGRADED"] | str | None = Field(
        default=None, description="Aggregated health of the Spark cluster."
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
        | None
    ) = Field(default=None, description="Current status of the Spark cluster.")
    entry_id: str | None = Field(
        default=None,
        alias="entryId",
        description="ID of the DataLens entry of the Spark cluster. Empty when the cluster has no entry.",
    )


class ListSparkClustersResult(APIModel):
    spark_clusters: list[SparkCluster] | None = Field(
        default=None,
        alias="sparkClusters",
        description="Spark clusters matching the request.",
    )
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for the next page of Spark clusters.",
    )


class CreateSparkClusterArgs(RequestBody):
    collection_id: str = Field(
        ...,
        alias="collectionId",
        description="ID of the DataLens collection in which to create the cluster.",
    )
    cloud_environment_id: str = Field(
        ...,
        alias="cloudEnvironmentId",
        description="ID of the cloud environment in which to create the cluster.",
    )
    name: str = Field(..., description="Name of the Spark cluster.")
    description: str | None = Field(default=None, description="Description of the Spark cluster.")
    labels: dict[str, str] | None = Field(default=None, description="Spark cluster labels.")
    config: CreateSparkClusterArgsConfig
