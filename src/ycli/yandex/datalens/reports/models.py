"""DataLens report models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.reports import CreateReportV2Result as ReportCreated
from ycli.yandex.datalens.schemas.reports import GetReportV2Result as Report
from ycli.yandex.datalens.schemas.reports import ReportDataV2 as ReportData
from ycli.yandex.datalens.schemas.reports import ReportMetaV2 as ReportMeta
from ycli.yandex.datalens.schemas.reports import UpdateReportV2Result as ReportSaved
from ycli.yandex.datalens.schemas.shared import EntryAnnotationArg as EntryAnnotation

__all__ = ["EntryAnnotation", "Report", "ReportCreated", "ReportData", "ReportMeta", "ReportSaved"]
