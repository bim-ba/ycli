"""`tracker dashboards` commands — create dashboards and add cycle-time widgets."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.tracker.dashboards.models import (
    CycleTimeWidget,
    DashboardCreate,
    DashboardOwner,
)

app = typer.Typer(name="dashboards", help="Tracker dashboards.", no_args_is_help=True)
add_widget_app = typer.Typer(
    name="add-widget", help="Add a widget to a dashboard.", no_args_is_help=True
)
app.add_typer(add_widget_app)

DashboardIdArg = Annotated[str, typer.Argument(metavar="DASHBOARD_ID", help="Target dashboard id.")]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@add_widget_app.callback()
def _widget_group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Dashboard name.")],
    layout: Annotated[str, typer.Option(help="Layout mode, e.g. two-columns.")] = "",
    owner: Annotated[str, typer.Option(help="Owner login or id (defaults to creator).")] = "",
) -> None:
    """Create a dashboard (POST /dashboards/)."""
    body = DashboardCreate(
        name=name,
        layout=layout or None,
        owner=DashboardOwner(id=owner) if owner else None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.dashboards.create(body=body), app_ctx.strategy, app_ctx.console
    )


@add_widget_app.command("cycletime")
def cycletime(
    ctx: typer.Context,
    dashboard_id: DashboardIdArg,
    description: Annotated[str, typer.Option(help="Widget name.")],
    query: Annotated[str, typer.Option(help="Query-language filter selecting issues.")] = "",
    from_status: Annotated[
        list[str] | None,
        typer.Option("--from-status", help="Status key work starts from (repeatable)."),
    ] = None,
    to_status: Annotated[
        list[str] | None,
        typer.Option("--to-status", help="Status key work ends at (repeatable)."),
    ] = None,
    mode: Annotated[str, typer.Option(help="Display mode, e.g. common-lines.")] = "",
) -> None:
    """Add a cycle-time widget to DASHBOARD_ID (POST /dashboards/{id}/widgets/cycleTime)."""
    body = CycleTimeWidget(
        description=description,
        query=query or None,
        from_statuses=[{"key": s} for s in from_status] if from_status else None,
        to_statuses=[{"key": s} for s in to_status] if to_status else None,
        mode=mode or None,
    ).model_dump(by_alias=True, exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.tracker.dashboards.add_cycle_time_widget(dashboard_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )
