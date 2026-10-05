# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class FixedScale(APIModel):
    size: str = Field(
        ...,
        description="Number of instances in the resource pool.",
        pattern="^(?:[1-9]|[1-9]\\d|100)$",
    )


class ScalePolicy(APIModel):
    """Resource pool scaling policy."""

    fixed_scale: FixedScale = Field(..., alias="fixedScale")
    scale_type: Literal["fixedScale"] = Field(..., alias="scaleType")


class AutoScale(APIModel):
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


class ScalePolicyModel(APIModel):
    """Resource pool scaling policy."""

    auto_scale: AutoScale = Field(..., alias="autoScale")
    scale_type: Literal["autoScale"] = Field(..., alias="scaleType")


class Driver(APIModel):
    """Driver resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: ScalePolicy | ScalePolicyModel = Field(
        ..., alias="scalePolicy", description="Resource pool scaling policy."
    )


class ScalePolicyModel1(APIModel):
    """Resource pool scaling policy."""

    fixed_scale: FixedScale = Field(..., alias="fixedScale")
    scale_type: Literal["fixedScale"] = Field(..., alias="scaleType")


class ScalePolicyModel2(APIModel):
    """Resource pool scaling policy."""

    auto_scale: AutoScale = Field(..., alias="autoScale")
    scale_type: Literal["autoScale"] = Field(..., alias="scaleType")


class Executor(APIModel):
    """Executor resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: ScalePolicyModel1 | ScalePolicyModel2 = Field(
        ..., alias="scalePolicy", description="Resource pool scaling policy."
    )


class ResourcePools(APIModel):
    driver: Driver = Field(..., description="Driver resource pool.")
    executor: Executor = Field(..., description="Executor resource pool.")


class Dependencies(APIModel):
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


class Logging(APIModel):
    """Cluster logging configuration."""

    enabled: bool = Field(..., description="Whether cluster logging is enabled.")


class Config(APIModel):
    spark_version: str = Field(
        ..., alias="sparkVersion", description="Spark version used by the cluster."
    )
    resource_pools: ResourcePools = Field(..., alias="resourcePools")
    dependencies: Dependencies | None = Field(..., description="Packages installed in the cluster.")
    logging: Logging | None = Field(..., description="Cluster logging configuration.")


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
    config: Config
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


class ScalePolicyModel3(APIModel):
    """Resource pool scaling policy."""

    fixed_scale: FixedScale = Field(..., alias="fixedScale")


class ScalePolicyModel4(APIModel):
    """Resource pool scaling policy."""

    auto_scale: AutoScale = Field(..., alias="autoScale")


class DriverModel(APIModel):
    """Driver resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: ScalePolicyModel3 | ScalePolicyModel4 = Field(
        ..., alias="scalePolicy", description="Resource pool scaling policy."
    )


class ScalePolicyModel5(APIModel):
    """Resource pool scaling policy."""

    fixed_scale: FixedScale = Field(..., alias="fixedScale")


class ScalePolicyModel6(APIModel):
    """Resource pool scaling policy."""

    auto_scale: AutoScale = Field(..., alias="autoScale")


class ExecutorModel(APIModel):
    """Executor resource pool."""

    resource_preset_id: str = Field(
        ...,
        alias="resourcePresetId",
        description="ID of the Spark resource preset.",
        max_length=50,
        min_length=1,
    )
    scale_policy: ScalePolicyModel5 | ScalePolicyModel6 = Field(
        ..., alias="scalePolicy", description="Resource pool scaling policy."
    )


class ResourcePoolsModel(APIModel):
    driver: DriverModel = Field(..., description="Driver resource pool.")
    executor: ExecutorModel = Field(..., description="Executor resource pool.")


class DependenciesModel(APIModel):
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


class ConfigModel(APIModel):
    spark_version: str | None = Field(
        default=None,
        alias="sparkVersion",
        description="Spark version. The service default is used when omitted.",
    )
    resource_pools: ResourcePoolsModel = Field(..., alias="resourcePools")
    dependencies: DependenciesModel | None = Field(
        default=None, description="Packages to install in the cluster."
    )
    logging: Logging | None = Field(default=None, description="Cluster logging configuration.")


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
    config: ConfigModel


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
