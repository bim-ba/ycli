"""`datalens dashboards` commands."""

import json
from typing import Annotated

import typer
from pydantic import BaseModel

from ycli.cli.body_fields import CallerFields
from ycli.cli.typedefs import values_option
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dashboards.models import (
    Dashboard,
    DashboardCreated,
    DashboardSaved,
)
from ycli.yandex.datalens.models import RevisionBranch, SaveMode
from ycli.yandex.datalens.schemas.dashboard import CreateDashboardV2Args, UpdateDashboardV2Args
from ycli.yandex.models import Ack

app = typer.Typer(name="dashboards", help="DataLens dashboards.", no_args_is_help=True)

DashIDArg = Annotated[str, typer.Argument(metavar="DASHBOARD_ID", help="Dashboard id.")]
LockOption = Annotated[
    str | None,
    typer.Option("--lock-token", help="The token of the lock held on it, when it is locked."),
]
ENTRY_HELP = "The dashboard, as a JSON object; --body-file gives it under `entry`."


def _body[M: BaseModel](model: type[M], caller: CallerFields, flags: dict[str, str | None]) -> M:
    """The request as ``model``: the flags given, over -F, over --body-file.

    A flag is given under the API's name of its field, ``entry`` as JSON. The file and ``-F``
    give the request itself, so ``mode`` or ``lockToken`` in a file reaches it like a flag.
    """
    given = {
        name: json.loads(value) if name == "entry" else value
        for name, value in flags.items()
        if value is not None
    }
    return model.model_validate(caller.over(given))


@app.command()
def get(
    dashboard_id: DashIDArg,
    rev_id: Annotated[
        str | None, typer.Option("--rev-id", help="The revision to read; the current by default.")
    ] = None,
    include_permissions: Annotated[
        bool | None,
        typer.Option(
            "--include-permissions/--no-include-permissions",
            help="Also say what you may do with the dashboard.",
        ),
    ] = None,
    include_links: Annotated[
        bool | None,
        typer.Option(
            "--include-links/--no-include-links", help="Also say what the dashboard is linked to."
        ),
    ] = None,
    include_favorite: Annotated[
        bool | None,
        typer.Option(
            "--include-favorite/--no-include-favorite",
            help="Also say whether the dashboard is a favourite.",
        ),
    ] = None,
    branch: Annotated[
        str | None,
        values_option(
            RevisionBranch,
            "--branch",
            help="Which version of it to read; the published one if left out (measured). A save "
            "writes the saved one: read `saved` before you change a dashboard.",
        ),
    ] = None,
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook the dashboard lies in.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> Dashboard:
    """Print one dashboard: its tabs and what stands on them.

    A real dashboard is large (100 KB and more): redirect the output to a file to work with it.
    """
    return datalens.dashboards.get(
        dashboard_id,
        rev_id=rev_id,
        include_permissions=include_permissions,
        include_links=include_links,
        include_favorite=include_favorite,
        branch=branch,
        workbook_id=workbook_id,
    )


@app.command()
def create(
    entry: Annotated[str | None, typer.Option("--entry", help=ENTRY_HELP)] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> DashboardCreated:
    """Create a dashboard from --entry or --body-file.

    `entry.meta` must be an object, `{}` when empty: without it DataLens answers
    `400 entry.meta: expected record, received undefined`.
    """
    body = _body(CreateDashboardV2Args, caller, {"entry": entry})
    return datalens.dashboards.create(body.entry)


@app.command()
def update(
    mode: Annotated[
        str,
        values_option(SaveMode, "--mode", help="Keep the dashboard as a draft, or publish it."),
    ],
    entry: Annotated[str | None, typer.Option("--entry", help=ENTRY_HELP)] = None,
    lock_token: LockOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> DashboardSaved:
    """Save a dashboard as given; `entryId` in the entry says which.

    DataLens does not check a revision here: a save overwrites what was saved since you read it
    (measured).
    """
    flags = {"entry": entry, "mode": mode, "lockToken": lock_token}
    body = _body(UpdateDashboardV2Args, caller, flags)
    return datalens.dashboards.update(body.entry, mode=body.mode.root, lock_token=body.lock_token)


@app.command()
def delete(
    dashboard_id: DashIDArg, lock_token: LockOption = None, *, datalens: DataLensClient
) -> Ack:
    """Delete a dashboard."""
    datalens.dashboards.delete(dashboard_id, lock_token=lock_token)
    return Ack.deleted("dashboard", dashboard_id)
