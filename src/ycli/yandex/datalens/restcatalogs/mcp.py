"""DataLens REST catalogs FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    LIMIT_CAP,
    RO,
    WRITE,
    PermissionsInfo,
    app_config,
    datalens_client,
)
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.restcatalogs.models import (
    RestCatalog,
    RestCatalogBucketSettings,
    RestCatalogSortField,
)
from ycli.yandex.models import ItemList

mcp = FastMCP("datalens-restcatalogs")


@mcp.tool(name="restcatalogs_list", annotations={**RO, "title": "List DataLens REST catalogs"})
def list_(
    cloud_environment_id: Annotated[
        str | None, Field(description="Only the catalogs of this cloud environment.")
    ] = None,
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None,
        Field(description='Conditions such as ``name="…"``; only matching catalogs are kept.'),
    ] = None,
    sort_by: Annotated[
        RestCatalogSortField | None, Field(description="The field to sort by.")
    ] = None,
    reverse_order: Annotated[bool | None, Field(description="Sort the other way round.")] = None,
    include_permissions: PermissionsInfo = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max catalogs to return; {LIMIT_CAP}")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[RestCatalog]:
    """The REST catalogs of the DataLens instance, auto-paginated.

    Experimental in the DataLens API. An instance with none answers an empty list.
    """
    return client.restcatalogs.list(
        cloud_environment_id=cloud_environment_id,
        filter=filter,
        sort_by=sort_by,
        reverse_order=reverse_order,
        include_permissions=include_permissions,
        limit=config.http.cap(limit),
    )


@mcp.tool(
    name="restcatalogs_create", annotations={**WRITE, "title": "Create DataLens REST catalog"}
)
def create(
    cloud_environment_id: Annotated[str, Field(description="The cloud environment to make it in.")],
    name: Annotated[str, Field(description="The catalog's name.")],
    bucket_settings: Annotated[
        RestCatalogBucketSettings,
        Field(description="The settings of its bucket; an empty object is valid."),
    ],
    description: Annotated[str | None, Field(description="A description.")] = None,
    labels: Annotated[
        dict[str, str] | None, Field(description="Labels, a name to a value.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Make a REST catalog and return the operation that makes it.

    It creates a bucket in a cloud, which may be billed: ask the person before calling. Ask
    ``lakehouseoperations_get`` for the operation until ``done``. Experimental in the DataLens
    API, written from its document and never called: not measured.
    """
    return client.restcatalogs.create(
        cloud_environment_id=cloud_environment_id,
        name=name,
        bucket_settings=bucket_settings,
        description=description,
        labels=labels,
    )
