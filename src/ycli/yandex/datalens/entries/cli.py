"""`datalens entries` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.entries.models import (
    EntriesPermissions,
    Entry,
    ListFilters,
    ListOrder,
    Relation,
    Renamed,
    Revision,
)
from ycli.yandex.datalens.models import EntryScope
from ycli.yandex.datalens.typedefs import EntryIDArg, PermissionsOption
from ycli.yandex.models import ItemList

app = typer.Typer(name="entries", help="DataLens entries.", no_args_is_help=True)

EntryIDsArg = Annotated[list[str], typer.Argument(metavar="ENTRY_ID...", help="Entry ids.")]


@app.command("list")
def list_(
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    ids: Annotated[
        list[str] | None, typer.Option("--id", help="Keep the entry with this id (repeatable).")
    ] = None,
    scope: Annotated[
        str | None, values_option(EntryScope, "--scope", help="Keep one kind of entry.")
    ] = None,
    scopes: Annotated[
        list[str] | None,
        values_option(EntryScope, "--scopes", help="Keep this kind of entry (repeatable)."),
    ] = None,
    type_: Annotated[
        list[str] | None, typer.Option("--type", help="Keep this type of entry (repeatable).")
    ] = None,
    created_by: Annotated[
        list[str] | None,
        typer.Option("--created-by", help="Keep what this user created (repeatable)."),
    ] = None,
    order_by: Annotated[
        str | None,
        typer.Option(
            "--order-by",
            help='What to sort by, as a JSON object: {"field": "name", "direction": "asc"}.',
        ),
    ] = None,
    exclude_locked: Annotated[
        bool | None,
        typer.Option(
            "--exclude-locked/--no-exclude-locked", help="Leave out what you may not read."
        ),
    ] = None,
    include_links: Annotated[
        bool | None,
        typer.Option("--include-links/--no-include-links", help="Also say what each is linked to."),
    ] = None,
    filters: Annotated[
        str | None,
        typer.Option("--filters", help='A filter, as a JSON object: {"name": "sales"}.'),
    ] = None,
    include_permissions_info: PermissionsOption = None,
    ignore_workbook_entries: Annotated[
        bool | None,
        typer.Option(
            "--ignore-workbook-entries/--no-ignore-workbook-entries",
            help="Leave out the entries of workbooks.",
        ),
    ] = None,
    ignore_shared_entries: Annotated[
        bool | None,
        typer.Option(
            "--ignore-shared-entries/--no-ignore-shared-entries",
            help="Leave out the shared entries.",
        ),
    ] = None,
    include_data: Annotated[
        bool | None,
        typer.Option("--include-data/--no-include-data", help="Also give the content of each."),
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[Entry]:
    """Find entries across the organization (auto-paginated); give --scope, --scopes or --id."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.entries.list(
        limit=cap,
        next=next_,
        ids=ids,
        scope=scope,
        scopes=scopes,
        type=type_,
        created_by=created_by,
        order_by=None if order_by is None else ListOrder.model_validate_json(order_by),
        exclude_locked=exclude_locked,
        include_links=include_links,
        filters=None if filters is None else ListFilters.model_validate_json(filters),
        include_permissions_info=include_permissions_info,
        ignore_workbook_entries=ignore_workbook_entries,
        ignore_shared_entries=ignore_shared_entries,
        include_data=include_data,
    )


@app.command("relations-list")
def relations_list(
    entry_ids: EntryIDsArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    # Its two values are everyday words: as a named set they would be found in every other
    # description that says them, so the option is plain text.
    link_direction: Annotated[
        str | None,
        typer.Option("--link-direction", help="`from`: what they use; `to`: what uses them."),
    ] = None,
    include_permissions_info: PermissionsOption = None,
    scope: Annotated[
        str | None, values_option(EntryScope, "--scope", help="Keep one kind of related entry.")
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[Relation]:
    """List what entries use, or what uses them (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.entries.relations_list(
        entry_ids,
        limit=cap,
        next=next_,
        link_direction=link_direction,
        include_permissions_info=include_permissions_info,
        scope=scope,
    )


@app.command("permissions-get")
def permissions_get(entry_ids: EntryIDsArg, *, datalens: DataLensClient) -> EntriesPermissions:
    """Print what you may do with each entry; a missing one answers `error: NOT_FOUND`."""
    return datalens.entries.permissions_get(entry_ids)


@app.command("revisions-list")
def revisions_list(
    entry_id: EntryIDArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    rev_ids: Annotated[
        list[str] | None, typer.Option("--rev-id", help="Keep this revision (repeatable).")
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[Revision]:
    """List the revisions of an entry (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.entries.revisions_list(entry_id, limit=cap, next=next_, rev_ids=rev_ids)


@app.command()
def rename(
    entry_id: EntryIDArg,
    name: Annotated[str, typer.Option("--name", help="The new name.")],
    *,
    datalens: DataLensClient,
) -> ItemList[Renamed]:
    """Give an entry another name."""
    return datalens.entries.rename(entry_id, name=name)
