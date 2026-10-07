"""DataLens dashboard models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.dashboard import CreateDashboardResponse as DashboardCreated
from ycli.yandex.datalens.schemas.dashboard import CreateDashboardV2ArgsEntry as DashboardCreate
from ycli.yandex.datalens.schemas.dashboard import GetDashboardV2Result as Dashboard
from ycli.yandex.datalens.schemas.dashboard import UpdateDashboardResponse as DashboardSaved
from ycli.yandex.datalens.schemas.dashboard import UpdateDashboardV2ArgsEntry as DashboardUpdate

__all__ = ["Dashboard", "DashboardCreate", "DashboardCreated", "DashboardSaved", "DashboardUpdate"]
