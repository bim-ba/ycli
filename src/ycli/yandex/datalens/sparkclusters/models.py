"""DataLens Spark cluster models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.spark_clusters import (
    CreateSparkClusterArgsConfig as NewClusterConfig,
)
from ycli.yandex.datalens.schemas.spark_clusters import ListSparkClustersResult as SparkClustersPage
from ycli.yandex.datalens.schemas.spark_clusters import (
    ListSparkResourcePresetsResult as SparkResourcePresetsPage,
)
from ycli.yandex.datalens.schemas.spark_clusters import SparkCluster, SparkResourcePreset

__all__ = [
    "NewClusterConfig",
    "SparkCluster",
    "SparkClustersPage",
    "SparkResourcePreset",
    "SparkResourcePresetsPage",
]
