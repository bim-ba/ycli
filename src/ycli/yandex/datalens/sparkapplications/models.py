"""DataLens Spark application models: the public names of the generated classes it uses."""

from ycli.yandex.datalens.schemas.spark_applications import (
    ListSparkApplicationLogResult as SparkApplicationLog,
)
from ycli.yandex.datalens.schemas.spark_applications import (
    ListSparkApplicationsResult as SparkApplicationsPage,
)
from ycli.yandex.datalens.schemas.spark_applications import SparkApplication

__all__ = ["SparkApplication", "SparkApplicationLog", "SparkApplicationsPage"]
