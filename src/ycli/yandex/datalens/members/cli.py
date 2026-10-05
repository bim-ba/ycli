"""`datalens members` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.members.models import Member, MemberKind, MemberLanguage
from ycli.yandex.models import ItemList

app = typer.Typer(name="members", help="DataLens members.", no_args_is_help=True)


@app.command("list")
def list_(
    limit: LimitOption = None,
    all_: AllOption = False,
    language: Annotated[
        str | None, values_option(MemberLanguage, "--language", help="Language of the names.")
    ] = None,
    search: Annotated[
        str | None, typer.Option("--search", help="Keep the names or addresses that have this.")
    ] = None,
    tab_id: Annotated[
        str | None, values_option(MemberKind, "--tab-id", help="Keep one kind of subject.")
    ] = None,
    filter_: Annotated[
        str | None, typer.Option("--filter", help="A filter expression of the API.")
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> ItemList[Member]:
    """List the users, groups and service accounts a role can be given to (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.members.list(
        limit=cap, language=language, search=search, tab_id=tab_id, filter=filter_
    )
