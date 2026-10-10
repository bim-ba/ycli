"""DataLens licensing operations, declared once (sans-IO).

Examples:
    >>> limit_get().path
    'rpc/getLicensesLimit'
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR_SIZED_BY_LIMIT
from ycli.yandex.datalens.licensing.models import (
    License,
    LicenseLimits,
    LicenseListed,
    LicensesPage,
)
from ycli.yandex.datalens.schemas.licensing import (
    AssignLicensesArgs,
    GetLicensesArgs,
    SetLicenseLimitArgs,
)
from ycli.yandex.models import ItemList


def licenses_list(
    *,
    user_ids: Sequence[str] | None,
    status: str | None,
    sort_by: str | None,
    order: str | None,
) -> Paged[LicensesPage, LicenseListed]:
    body = GetLicensesArgs(
        userIds=None if user_ids is None else list(user_ids),
        status=status,
        sortBy=sort_by,
        order=order,
    )
    return Paged(
        RPC("getLicenses", LicensesPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR_SIZED_BY_LIMIT,
        lambda page: page.licenses or [],
    )


def licenses_assign(user_ids: Sequence[str]) -> Endpoint[ItemList[License]]:
    body = AssignLicensesArgs(userIds=list(user_ids))
    return RPC(
        "assignLicenses", ItemList[License], json=body, effect=Effect.WRITE, grants_access=True
    )


def limit_get() -> Endpoint[LicenseLimits]:
    # Measured: the operation takes no argument, and answers the same to an empty body.
    return RPC("getLicensesLimit", LicenseLimits, effect=Effect.READ)


def limit_set(value: int) -> Endpoint[LicenseLimits]:
    body = SetLicenseLimitArgs(value=value)
    return RPC("setLicenseLimit", LicenseLimits, json=body, effect=Effect.IDEMPOTENT_WRITE)
