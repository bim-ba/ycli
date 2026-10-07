"""DataLens cloud environments FastMCP tools (read + write) — Depends DI, native errors."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.cloudenvironments.models import (
    CloudEnvironment,
    CloudEnvironmentNewStorage,
    CloudEnvironmentStorageChange,
)
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    PermissionsInfo,
    app_config,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.models import ItemList

mcp = new_server("datalens-cloudenvironments")

EnvironmentID = Annotated[str, Field(description="Id of the cloud environment.")]
SecurityGroups = Annotated[
    list[str] | None, Field(description="The security groups the environment uses.")
]


@mcp.tool(
    name="cloudenvironments_list", annotations={**RO, "title": "List DataLens cloud environments"}
)
def list_(
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None,
        Field(
            description='Conditions, all of which must hold; each is ``field="value"`` over '
            "``name``, ``cloud_id``, ``status`` or ``created_by_id``."
        ),
    ] = None,
    include_permissions: PermissionsInfo = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max environments to return; {LIMIT_CAP}")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[CloudEnvironment]:
    """The cloud environments of the DataLens instance, auto-paginated.

    Experimental in the DataLens API. An instance with none answers an empty list.
    """
    return client.cloudenvironments.list(
        filter=filter, include_permissions=include_permissions, limit=config.http.cap(limit)
    )


@mcp.tool(
    name="cloudenvironments_get", annotations={**RO, "title": "Get DataLens cloud environment"}
)
def get(
    id: EnvironmentID,  # noqa: A002  # the API's own name for it
    include_permissions: PermissionsInfo = None,
    client: DataLensClient = Depends(datalens_client),
) -> CloudEnvironment:
    """One cloud environment: its cloud, its subnet, its status and its storage.

    Experimental in the DataLens API and written from its document: not measured. An id
    nothing knows answers 403 Permission denied, not 404: it is not a lack of rights.
    """
    return client.cloudenvironments.get(id, include_permissions=include_permissions)


@mcp.tool(
    name="cloudenvironments_create",
    annotations={**WRITE, "title": "Create DataLens cloud environment"},
)
def create(
    name: Annotated[str, Field(description="The environment's name.")],
    cloud_id: Annotated[str, Field(description="The cloud to make it in.")],
    subnet_id: Annotated[str, Field(description="The subnet it uses.")],
    description: Annotated[str | None, Field(description="A description.")] = None,
    security_group_ids: SecurityGroups = None,
    storage: Annotated[
        CloudEnvironmentNewStorage | None,
        Field(description="The settings of its storage bucket; no bucket when left out."),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Make a cloud environment and return the operation that makes it.

    It creates resources in a cloud, which may be billed: ask the person before calling.
    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.cloudenvironments.create(
        name=name,
        cloud_id=cloud_id,
        subnet_id=subnet_id,
        description=description,
        security_group_ids=security_group_ids,
        storage=storage,
    )


@mcp.tool(
    name="cloudenvironments_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens cloud environment"},
)
def update(
    id: EnvironmentID,  # noqa: A002  # the API's own name for it
    name: Annotated[str | None, Field(description="A new name.")] = None,
    description: Annotated[
        str | None, Field(description="A new description; an empty one clears it.")
    ] = None,
    security_group_ids: SecurityGroups = None,
    storage: Annotated[
        CloudEnvironmentStorageChange | None,
        Field(description="New settings of its storage bucket."),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Change the fields given of a cloud environment and return the operation.

    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.cloudenvironments.update(
        id,
        name=name,
        description=description,
        security_group_ids=security_group_ids,
        storage=storage,
    )


@mcp.tool(
    name="cloudenvironments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete DataLens cloud environment"},
)
def delete(
    id: EnvironmentID,  # noqa: A002  # the API's own name for it
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Delete a cloud environment and return the operation that deletes it.

    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.cloudenvironments.delete(id)
