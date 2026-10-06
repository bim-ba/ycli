"""`datalens licensing` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.licensing.models import (
    License,
    LicenseLimits,
    LicenseListed,
    LicenseSortField,
    LicenseStatus,
)
from ycli.yandex.models import ItemList, SortDirection

BILLED = (
    "A licence is a seat DataLens bills for. Written from the DataLens document and never "
    "called: not measured."
)
app = typer.Typer(
    name="licensing", help="Licences (seats) of the DataLens instance.", no_args_is_help=True
)


@app.command("licenses-list")
def licenses_list(
    user_ids: Annotated[
        list[str] | None,
        typer.Option("--user-ids", help="Only the licences of this user (repeatable)."),
    ] = None,
    status: Annotated[
        str | None, values_option(LicenseStatus, "--status", help="Only licences in this state.")
    ] = None,
    sort_by: Annotated[
        str | None, values_option(LicenseSortField, "--sort-by", help="The field to sort by.")
    ] = None,
    order: Annotated[
        str | None, values_option(SortDirection, "--order", help="The order of the sort.")
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> ItemList[LicenseListed]:
    """List the licences of the instance: whose, of which type, active or not (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.licensing.licenses_list(
        user_ids=user_ids or None, status=status, sort_by=sort_by, order=order, limit=cap
    )


@app.command("licenses-assign", epilog=BILLED)
def licenses_assign(
    user_ids: Annotated[list[str], typer.Argument(metavar="USER_ID...", help="User ids.")],
    *,
    datalens: DataLensClient,
) -> ItemList[License]:
    """Give each of these users a licence."""
    return datalens.licensing.licenses_assign(user_ids)


@app.command("limit-get")
def limit_get(*, datalens: DataLensClient) -> LicenseLimits:
    """Print how many licences the instance may hold, now and next, and how many are active."""
    return datalens.licensing.limit_get()


@app.command("limit-set", epilog=BILLED)
def limit_set(
    value: Annotated[
        int, typer.Argument(metavar="VALUE", help="The most licences the instance may hold.")
    ],
    *,
    datalens: DataLensClient,
) -> LicenseLimits:
    """Set how many licences the instance may hold."""
    return datalens.licensing.limit_set(value)
