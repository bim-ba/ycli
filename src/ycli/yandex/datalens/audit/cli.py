"""`datalens audit` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.datalens.audit.models import AuditEntry, UserEntryPermissions
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.models import ItemList

app = typer.Typer(name="audit", help="DataLens audit.", no_args_is_help=True)


@app.command("entries-updates-list")
def entries_updates_list(
    from_: Annotated[
        str,
        typer.Option("--from", help="The start of the period: an ISO-8601 time with its zone."),
    ],
    to: Annotated[str | None, typer.Option("--to", help="The end of the period.")] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> ItemList[AuditEntry]:
    """List the entries changed in a period, deleted ones too (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.audit.entries_updates_list(from_, to=to, limit=cap)


@app.command("entry-permissions-get")
def entry_permissions_get(
    entry_ids: Annotated[list[str], typer.Argument(metavar="ENTRY_ID...", help="Entry ids.")],
    user_id: Annotated[
        str, typer.Option("--user-id", help="The user's id, as `createdBy` of an entry gives it.")
    ],
    *,
    datalens: DataLensClient,
) -> UserEntryPermissions:
    """Print what one user may do with each entry: execute, read, edit, admin."""
    return datalens.audit.entry_permissions_get(entry_ids, user_id=user_id)
