"""DataLens dashboard models: the public names of the generated classes this resource uses."""

from pydantic import ConfigDict, Field

from ycli.yandex.datalens.schemas.dashboard import CreateDashboardResponse as DashboardCreated
from ycli.yandex.datalens.schemas.dashboard import CreateDashboardV2ArgsEntry as DashboardCreate
from ycli.yandex.datalens.schemas.dashboard import DashDataV2 as DashboardData
from ycli.yandex.datalens.schemas.dashboard import DashMetaV2 as DashboardMeta
from ycli.yandex.datalens.schemas.dashboard import GetDashboardV2Result as Dashboard
from ycli.yandex.datalens.schemas.dashboard import UpdateDashboardResponse as DashboardSaved
from ycli.yandex.datalens.schemas.dashboard import UpdateDashboardV2ArgsEntry as DashboardUpdate
from ycli.yandex.datalens.schemas.shared import EntryAnnotationArg as EntryAnnotation
from ycli.yandex.datalens.workbook_entries import EntryInWorkbook
from ycli.yandex.models import RequestBody


class DashboardContent(RequestBody):
    """What the file of a dashboard holds: what ``updateDashboard`` takes of the entry.

    Its id and revision are the file's link, and the revision is not sent: DataLens checks
    none on a write (measured in #484).
    """

    annotation: EntryAnnotation | None = Field(default=None, description="Its description.")
    meta: DashboardMeta | None = Field(default=None, description="Metadata of the entry.")
    data: DashboardData | None = Field(
        default=None, description="Its tabs, their widgets and selectors, and its settings."
    )


class DashboardEntry(EntryInWorkbook, DashboardContent):
    """A dashboard of a workbook as its file reads it: the content, the link, the name."""

    model_config = ConfigDict(extra="allow")


__all__ = [
    "Dashboard",
    "DashboardContent",
    "DashboardCreate",
    "DashboardCreated",
    "DashboardData",
    "DashboardEntry",
    "DashboardMeta",
    "DashboardSaved",
    "DashboardUpdate",
    "EntryAnnotation",
]
