"""DataLens workbook import models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.workbook_import import (
    GetWorkbookImportStatusResult as WorkbookImportStatus,
)
from ycli.yandex.datalens.schemas.workbook_import import (
    StartWorkbookImportResult as WorkbookImportStarted,
)

__all__ = ["WorkbookImportStarted", "WorkbookImportStatus"]
