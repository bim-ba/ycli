"""DataLens workbook models: the public names of the generated classes this resource uses."""

from typing import Literal

from ycli.yandex.datalens.schemas.workbook import CreateWorkbookResult as WorkbookCreated
from ycli.yandex.datalens.schemas.workbook import DeleteWorkbooksResponse as WorkbooksDeleted
from ycli.yandex.datalens.schemas.workbook import GetWorkbookEntriesArgsFilters as EntriesFilters
from ycli.yandex.datalens.schemas.workbook import GetWorkbookEntriesArgsOrderBy as EntriesOrder
from ycli.yandex.datalens.schemas.workbook import GetWorkbookEntriesEntry as WorkbookEntry
from ycli.yandex.datalens.schemas.workbook import GetWorkbookEntriesResult as EntriesPage
from ycli.yandex.datalens.schemas.workbook import GetWorkbookResult as WorkbookDetails
from ycli.yandex.datalens.schemas.workbook import GetWorkbooksListResult as WorkbooksPage
from ycli.yandex.datalens.schemas.workbook import (
    GetWorkbooksListResultWorkbooksItem as WorkbookListed,
)
from ycli.yandex.datalens.schemas.workbook import MoveWorkbooksResponse as WorkbooksMoved
from ycli.yandex.datalens.schemas.workbook import Workbook

#: What kind of entry a workbook holds.
EntryScope = (
    Literal[
        "dash",
        "report",
        "widget",
        "dataset",
        "folder",
        "connection",
        "compute",
        "artifact",
        "sql_query",
    ]
    | str
)

__all__ = [
    "EntriesFilters",
    "EntriesOrder",
    "EntriesPage",
    "EntryScope",
    "Workbook",
    "WorkbookCreated",
    "WorkbookDetails",
    "WorkbookEntry",
    "WorkbookListed",
    "WorkbooksDeleted",
    "WorkbooksMoved",
    "WorkbooksPage",
]
