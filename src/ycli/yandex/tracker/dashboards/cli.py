"""`tracker dashboards` commands — create dashboards and add cycle-time widgets."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dashboards.models import (
    CycleTimeWidget,
    Dashboard,
    DashboardCreate,
    DashboardOwner,
    Widget,
)

app = typer.Typer(name="dashboards", help="Tracker dashboards.", no_args_is_help=True)

DashboardIDArg = Annotated[str, typer.Argument(metavar="DASHBOARD_ID", help="Target dashboard id.")]


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Dashboard name.")],
    layout: Annotated[str | None, typer.Option(help="Layout mode, e.g. two-columns.")] = None,
    owner: Annotated[
        str | None, typer.Option(help="Owner login or id (defaults to creator).")
    ] = None,
    *,
    tracker: TrackerClient,
) -> Dashboard:
    """Create a dashboard (POST /dashboards/)."""
    body = DashboardCreate(
        name=name,
        layout=layout,
        owner=DashboardOwner(id=owner) if owner is not None else None,
    )
    return tracker.dashboards.create(body=body)


@app.command()
def widgets_create_cycle_time(
    dashboard_id: DashboardIDArg,
    description: Annotated[str, typer.Option(help="Widget name.")],
    query: Annotated[
        str | None, typer.Option(help="Query-language filter selecting issues.")
    ] = None,
    from_status: Annotated[
        list[str] | None,
        typer.Option("--from-status", help="Status key work starts from (repeatable)."),
    ] = None,
    to_status: Annotated[
        list[str] | None,
        typer.Option("--to-status", help="Status key work ends at (repeatable)."),
    ] = None,
    mode: Annotated[str | None, typer.Option(help="Display mode, e.g. common-lines.")] = None,
    *,
    tracker: TrackerClient,
) -> Widget:
    """Add a cycle-time widget to DASHBOARD_ID (POST /dashboards/{id}/widgets/cycleTime)."""
    body = CycleTimeWidget(
        description=description,
        query=query,
        fromStatuses=[{"key": s} for s in from_status] if from_status else None,
        toStatuses=[{"key": s} for s in to_status] if to_status else None,
        mode=mode,
    )
    return tracker.dashboards.widgets_create_cycle_time(dashboard_id, body=body)
