"""DataLens cloud environment models: the public names of the generated classes it uses."""

from ycli.yandex.datalens.schemas.cloud_environments import CloudEnvironment
from ycli.yandex.datalens.schemas.cloud_environments import (
    CreateCloudEnvironmentArgsStorage as CloudEnvironmentNewStorage,
)
from ycli.yandex.datalens.schemas.cloud_environments import (
    ListCloudEnvironmentsResult as CloudEnvironmentsPage,
)
from ycli.yandex.datalens.schemas.cloud_environments import (
    UpdateCloudEnvironmentArgsStorage as CloudEnvironmentStorageChange,
)

__all__ = [
    "CloudEnvironment",
    "CloudEnvironmentNewStorage",
    "CloudEnvironmentStorageChange",
    "CloudEnvironmentsPage",
]
