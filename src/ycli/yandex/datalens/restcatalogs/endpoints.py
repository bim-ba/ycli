"""DataLens REST catalog operations, declared once (sans-IO).

Both of them are marked experimental in the document DataLens publishes.

Examples:
    >>> first = list_(
    ...     cloud_environment_id="env1",
    ...     filter=None,
    ...     sort_by=None,
    ...     reverse_order=None,
    ...     include_permissions=None,
    ... )
    >>> first.endpoint.body
    {'cloudEnvironmentId': 'env1'}
"""

from collections.abc import Mapping, Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.restcatalogs.models import (
    RestCatalog,
    RestCatalogBucketSettings,
    RestCatalogsPage,
)
from ycli.yandex.datalens.schemas.rest_catalogs import CreateRestCatalogArgs, ListCatalogsArgs


def list_(
    *,
    cloud_environment_id: str | None,
    filter: Sequence[str] | None,  # noqa: A002  # the API's own name for it
    sort_by: str | None,
    reverse_order: bool | None,
    include_permissions: bool | None,
) -> Paged[RestCatalogsPage, RestCatalog]:
    body = ListCatalogsArgs(
        cloudEnvironmentId=cloud_environment_id,
        filter=None if filter is None else list(filter),
        sortBy=sort_by,
        reverseOrder=reverse_order,
        includePermissions=include_permissions,
    )
    return Paged(
        RPC("listCatalogs", RestCatalogsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.rest_catalogs or [],
    )


def create(
    *,
    cloud_environment_id: str,
    name: str,
    bucket_settings: RestCatalogBucketSettings,
    description: str | None,
    labels: Mapping[str, str] | None,
) -> Endpoint[LakehouseOperation]:
    body = CreateRestCatalogArgs(
        cloudEnvironmentId=cloud_environment_id,
        name=name,
        bucketSettings=bucket_settings,
        description=description,
        labels=None if labels is None else dict(labels),
    )
    return RPC("createRestCatalog", LakehouseOperation, json=body, effect=Effect.WRITE)
