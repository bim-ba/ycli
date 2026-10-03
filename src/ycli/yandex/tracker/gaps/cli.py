"""`tracker gaps` commands: employee absences (admin-only)."""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.models import Ack, ItemList
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.gaps.models import GapCreated, GapInput, GapsCreate, GapWorkflow, UserGaps

app = typer.Typer(name="gaps", help="Tracker employee absences (admin).", no_args_is_help=True)


@app.command()
def create(
    user: Annotated[str | None, typer.Option(help="Login or id of the absent user.")] = None,
    workflow: Annotated[GapWorkflow | None, typer.Option(help="Kind of absence.")] = None,
    date_from: Annotated[
        str | None, typer.Option("--from", help="Start of the absence (ISO 8601).")
    ] = None,
    date_to: Annotated[
        str | None, typer.Option("--to", help="End of the absence (ISO 8601).")
    ] = None,
    gap_id: Annotated[
        str | None, typer.Option("--id", help="Identifier of the absence (generated if omitted).")
    ] = None,
    full_day: Annotated[
        bool | None, typer.Option("--full-day/--part-day", help="Whether it covers whole days.")
    ] = None,
    work_in_absence: Annotated[
        bool | None,
        typer.Option("--work-in-absence/--no-work-in-absence", help="Whether the user works."),
    ] = None,
    gap: Annotated[
        list[str] | None,
        typer.Option("--gap", help="More absences as JSON objects of the API docs (repeatable)."),
    ] = None,
    *,
    tracker: TrackerClient,
) -> GapCreated:
    """Create absences (POST /gaps): one from --user/--workflow/--from/--to, more from --gap.

    Example: --user ann --workflow trip --from 2026-07-10T00:00Z --to 2026-07-20T00:00Z
    """
    gaps = []
    if user is not None or workflow is not None or date_from is not None or date_to is not None:
        if user is None or workflow is None or date_from is None or date_to is None:
            raise typer.BadParameter("--user, --workflow, --from and --to go together")
        gaps.append(
            GapInput(
                id=gap_id,
                user=user,
                workflow=workflow,
                date_from=date_from,
                date_to=date_to,
                full_day=full_day,
                work_in_absence=work_in_absence,
            )
        )
    for raw in gap or []:
        try:
            gaps.append(GapInput.model_validate(json.loads(raw)))
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(f"--gap must be valid JSON: {exc}") from exc
    if not gaps:
        raise typer.BadParameter("give an absence: --user/--workflow/--from/--to or --gap")
    return tracker.gaps.create(GapsCreate(gaps=gaps))


@app.command()
def search(
    users: Annotated[
        list[str], typer.Argument(metavar="USER...", help="Logins or ids (up to 100).")
    ],
    date_from: Annotated[
        str | None, typer.Option("--from", help="Window start (ISO 8601); default: now.")
    ] = None,
    date_to: Annotated[
        str | None, typer.Option("--to", help="Window end (ISO 8601); must be after --from.")
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    tracker: TrackerClient,
) -> ItemList[UserGaps]:
    """Find the absences of USER... overlapping a window (POST /gaps/_search; --all for all)."""
    cap = config.http.cap(limit, all_=all_)
    return tracker.gaps.search(users, date_from=date_from, date_to=date_to, limit=cap)


@app.command()
def delete(
    gap_ids: Annotated[
        list[str], typer.Argument(metavar="GAP_ID...", help="Absence ids to delete (up to 100).")
    ],
    *,
    tracker: TrackerClient,
) -> Ack:
    """Delete absences by id (DELETE /gaps?gapIds=…); unknown ids are ignored."""
    tracker.gaps.delete(gap_ids)
    return Ack.deleted("gaps", ", ".join(gap_ids))
