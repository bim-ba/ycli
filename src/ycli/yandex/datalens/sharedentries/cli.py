"""`datalens sharedentries` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption, NextOption
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import AccessBindingDelta, Operation, SubjectWithBindings
from ycli.yandex.datalens.typedefs import DeltaOption, EntryIDArg

app = typer.Typer(
    name="sharedentries",
    help="DataLens shared entries: connections and datasets that lie in a collection.",
    no_args_is_help=True,
)


@app.command("access-bindings-list")
def access_bindings_list(
    entry_id: EntryIDArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    get_inherited_bindings: Annotated[
        bool | None,
        typer.Option(
            "--get-inherited-bindings/--no-get-inherited-bindings",
            help="Also list the inherited roles.",
        ),
    ] = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[SubjectWithBindings]:
    """List who has which role on a shared entry (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.sharedentries.access_bindings_list(
        entry_id, limit=cap, next=next_, get_inherited_bindings=get_inherited_bindings
    )


@app.command("access-bindings-update")
def access_bindings_update(
    entry_id: EntryIDArg,
    deltas: DeltaOption,
    *,
    datalens: DataLensClient,
) -> Operation:
    """Give or take away roles on a shared entry; the roles not named stay as they are.

    Grants access: asks before it is sent (--yes to skip).
    """
    parsed = [AccessBindingDelta.model_validate_json(delta) for delta in deltas]
    return datalens.sharedentries.access_bindings_update(entry_id, deltas=parsed)
