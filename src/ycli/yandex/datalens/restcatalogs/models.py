"""DataLens REST catalog models: the public names of the generated classes it uses."""

from typing import Literal

from ycli.yandex.datalens.schemas.rest_catalogs import (
    CreateRestCatalogArgsBucketSettings as RestCatalogBucketSettings,
)
from ycli.yandex.datalens.schemas.rest_catalogs import ListCatalogsResult as RestCatalogsPage
from ycli.yandex.datalens.schemas.rest_catalogs import (
    ListCatalogsResultRestCatalogsItem as RestCatalog,
)

#: What a listing of REST catalogs is sorted by.
RestCatalogSortField = Literal["name", "createdAt", "updatedAt"] | str

__all__ = [
    "RestCatalog",
    "RestCatalogBucketSettings",
    "RestCatalogSortField",
    "RestCatalogsPage",
]
