"""DataLens cloud environment operations, declared once (sans-IO).

Every one of them is marked experimental in the document DataLens publishes.

Examples:
    >>> get("env1", include_permissions=None).body
    {'id': 'env1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cloudenvironments.models import (
    CloudEnvironment,
    CloudEnvironmentNewStorage,
    CloudEnvironmentsPage,
    CloudEnvironmentStorageChange,
)
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.schemas.cloud_environments import (
    CreateCloudEnvironmentArgs,
    DeleteCloudEnvironmentArgs,
    GetCloudEnvironmentArgs,
    ListCloudEnvironmentsArgs,
    UpdateCloudEnvironmentArgs,
)


def list_(
    *,
    filter: Sequence[str] | None,  # noqa: A002  # the API's own name for it
    include_permissions: bool | None,
) -> Paged[CloudEnvironmentsPage, CloudEnvironment]:
    body = ListCloudEnvironmentsArgs(
        filter=None if filter is None else list(filter), includePermissions=include_permissions
    )
    return Paged(
        RPC("listCloudEnvironments", CloudEnvironmentsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.cloud_environments or [],
    )


def get(
    id: str,  # noqa: A002  # the API's own name for it
    *,
    include_permissions: bool | None,
) -> Endpoint[CloudEnvironment]:
    body = GetCloudEnvironmentArgs(id=id, includePermissions=include_permissions)
    return RPC("getCloudEnvironment", CloudEnvironment, json=body, effect=Effect.READ)


def create(
    *,
    name: str,
    cloud_id: str,
    subnet_id: str,
    description: str | None,
    security_group_ids: Sequence[str] | None,
    storage: CloudEnvironmentNewStorage | None,
) -> Endpoint[LakehouseOperation]:
    body = CreateCloudEnvironmentArgs(
        name=name,
        cloudId=cloud_id,
        subnetId=subnet_id,
        description=description,
        securityGroupIds=None if security_group_ids is None else list(security_group_ids),
        storage=storage,
    )
    return RPC("createCloudEnvironment", LakehouseOperation, json=body, effect=Effect.WRITE)


def update(
    id: str,  # noqa: A002  # the API's own name for it
    *,
    name: str | None,
    description: str | None,
    security_group_ids: Sequence[str] | None,
    storage: CloudEnvironmentStorageChange | None,
) -> Endpoint[LakehouseOperation]:
    body = UpdateCloudEnvironmentArgs(
        id=id,
        name=name,
        description=description,
        securityGroupIds=None if security_group_ids is None else list(security_group_ids),
        storage=storage,
    )
    return RPC(
        "updateCloudEnvironment", LakehouseOperation, json=body, effect=Effect.IDEMPOTENT_WRITE
    )


def delete(
    id: str,  # noqa: A002  # the API's own name for it
) -> Endpoint[LakehouseOperation]:
    body = DeleteCloudEnvironmentArgs(id=id)
    return RPC("deleteCloudEnvironment", LakehouseOperation, json=body, effect=Effect.DESTRUCTIVE)
