"""Tracker ``/gaps`` FastMCP tools: employee absences (admin-only; honest ARCH-3 annotations)."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.models import Ack
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    app_config,
    tracker_client,
)
from ycli.yandex.tracker.gaps.models import GapCreated, GapsCreate, UserGapList

mcp = FastMCP("tracker-gaps")


@mcp.tool(
    name="gaps_search", annotations={**RO, "title": "Search Tracker employee absences"}, tags=TAGS
)
def search(
    users: Annotated[
        list[str], Field(description="Logins or ids of the users to look up (up to 100).")
    ],
    date_from: Annotated[
        str | None, Field(description="Window start (ISO 8601); defaults to now.")
    ] = None,
    date_to: Annotated[
        str | None, Field(description="Window end (ISO 8601); must be after ``date_from``.")
    ] = None,
    limit: Annotated[int, Field(description=f"Max users to return; {LIMIT_CAP}")] = 0,
    client: TrackerClient = Depends(tracker_client),
    config: AppConfig = Depends(app_config),
) -> UserGapList:
    """The absences (vacation, illness, trips, duty, …) of the given users that overlap a window.

    A read done via POST; needs Tracker administrator rights. Every requested user appears,
    with an empty ``gaps`` list when they are not absent.
    """
    cap = config.http.cap(limit)
    return client.gaps.search(users, date_from=date_from, date_to=date_to, limit=cap)


@mcp.tool(
    name="gaps_create",
    annotations={**WRITE, "title": "Create Tracker employee absences"},
    tags=WRITE_TAGS,
)
def create(body: GapsCreate, client: TrackerClient = Depends(tracker_client)) -> GapCreated:
    """Create up to 100 employee absences; needs Tracker administrator rights.

    Each gap needs ``user``, ``workflow`` (vacation, paid_day_off, illness, absence, trip,
    conference_trip, conference, learning, maternity or duty), ``from`` and ``to`` (ISO 8601,
    ``from`` earlier). Returns the absences actually saved.
    """
    return client.gaps.create(body)


@mcp.tool(
    name="gaps_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker employee absences"},
    tags=WRITE_TAGS,
)
def delete(
    gap_ids: Annotated[
        list[str], Field(description="Ids of the absences to delete (up to 100), from a search.")
    ],
    client: TrackerClient = Depends(tracker_client),
) -> Ack:
    """Delete employee absences by id (irreversible); ids the API does not know are ignored.

    Needs Tracker administrator rights. Returns an acknowledgement.
    """
    client.gaps.delete(gap_ids)
    return Ack.deleted("gaps", ", ".join(gap_ids))
