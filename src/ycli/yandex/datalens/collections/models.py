"""DataLens collection models: the public names of the generated classes this resource uses."""

from typing import Annotated, Literal

from pydantic import Field

from ycli.yandex.datalens.schemas.collection import Collection
from ycli.yandex.datalens.schemas.collection import CreateCollectionResult as CollectionCreated
from ycli.yandex.datalens.schemas.collection import DeleteCollectionResult as CollectionsDeleted
from ycli.yandex.datalens.schemas.collection import (
    GetCollectionBreadcrumbsResultItem as CollectionBreadcrumb,
)
from ycli.yandex.datalens.schemas.collection import GetCollectionResult as CollectionDetails
from ycli.yandex.datalens.schemas.collection import (
    GetRootCollectionPermissionsResult as RootPermissions,
)
from ycli.yandex.datalens.schemas.collection import GetStructureItemsResult as ContentPage
from ycli.yandex.datalens.schemas.collection import (
    GetStructureItemsResultItemsItemVariant1 as ContentCollection,
)
from ycli.yandex.datalens.schemas.collection import (
    GetStructureItemsResultItemsItemVariant2 as ContentWorkbook,
)
from ycli.yandex.datalens.schemas.collection import MoveCollectionsResponse as CollectionsMoved
from ycli.yandex.datalens.schemas.collection import StructureItemEntry as ContentEntry

#: Which kinds of items the content of a collection lists.
ContentMode = Literal["all", "onlyCollections", "onlyWorkbooks", "onlyEntries"] | str
#: One item of a collection: a collection, a workbook or an entry.
ContentItem = Annotated[
    ContentCollection | ContentWorkbook | ContentEntry, Field(discriminator="entity")
]

__all__ = [
    "Collection",
    "CollectionBreadcrumb",
    "CollectionCreated",
    "CollectionDetails",
    "CollectionsDeleted",
    "CollectionsMoved",
    "ContentCollection",
    "ContentEntry",
    "ContentItem",
    "ContentMode",
    "ContentPage",
    "ContentWorkbook",
    "RootPermissions",
]
