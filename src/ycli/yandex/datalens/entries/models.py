"""DataLens entry models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.entries import GetEntriesPermissionsResult as EntriesPermissions
from ycli.yandex.datalens.schemas.entries import GetEntriesRelationsEntry as Relation
from ycli.yandex.datalens.schemas.entries import GetEntriesRelationsResult as RelationsPage
from ycli.yandex.datalens.schemas.entries import GetRevisionsResult as RevisionsPage
from ycli.yandex.datalens.schemas.entries import GetRevisionsResultEntriesItem as Revision
from ycli.yandex.datalens.schemas.entries import RenameEntryResultEntry as Renamed
from ycli.yandex.datalens.schemas.navigation import GetEntriesV2ArgsFilters as ListFilters
from ycli.yandex.datalens.schemas.navigation import GetEntriesV2ArgsOrderBy as ListOrder
from ycli.yandex.datalens.schemas.navigation import GetEntriesV2Result as EntriesPage
from ycli.yandex.datalens.schemas.navigation import GetEntriesV2ResultEntriesItem as Entry

__all__ = [
    "EntriesPage",
    "EntriesPermissions",
    "Entry",
    "ListFilters",
    "ListOrder",
    "Relation",
    "RelationsPage",
    "Renamed",
    "Revision",
    "RevisionsPage",
]
