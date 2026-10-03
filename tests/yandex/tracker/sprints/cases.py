"""Contract cases for Tracker ``/sprints`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.sprints.models import SprintBoardInput, SprintCreate, SprintUpdate

CASES = [
    Case(
        "tracker.sprints.list",
        args=(3,),
        cli=["tracker", "sprints", "list", "3"],
        mcp=("tracker_sprints_list", {"board_id": 3}),
        exchanges=[
            (Sent("GET", "boards/3/sprints"), Reply(json=[{"id": 4401, "name": "Sprint 1"}]))
        ],
    ),
    Case(
        "tracker.sprints.get",
        args=(4402,),
        cli=["tracker", "sprints", "get", "4402"],
        mcp=("tracker_sprints_get", {"sprint_id": 4402}),
        exchanges=[
            (
                Sent("GET", "sprints/4402"),
                Reply(json={"id": 4402, "status": "in_progress", "board": {"id": "3"}}),
            )
        ],
    ),
    Case(
        "tracker.sprints.create",
        args=(
            SprintCreate(
                name="Sprint 9",
                board=SprintBoardInput(id="17"),
                start_date="2026-10-05",
                end_date="2026-10-19",
            ),
        ),
        cli=[
            "tracker",
            "sprints",
            "create",
            "--board-id",
            "17",
            "--name",
            "Sprint 9",
            "--start-date",
            "2026-10-05",
            "--end-date",
            "2026-10-19",
        ],
        mcp=(
            "tracker_sprints_create",
            {
                "body": {
                    "name": "Sprint 9",
                    "board": {"id": "17"},
                    "start_date": "2026-10-05",
                    "end_date": "2026-10-19",
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "sprints",
                    json={
                        "name": "Sprint 9",
                        "board": {"id": "17"},
                        "startDate": "2026-10-05",
                        "endDate": "2026-10-19",
                    },
                ),
                Reply(json={"id": 4403, "name": "Sprint 9"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.sprints.update",
        args=(
            4404,
            SprintUpdate(
                name="Updated", start_date="2026-11-02", end_date="2026-11-16", status="draft"
            ),
        ),
        kwargs={"version": 5},
        cli=[
            "tracker",
            "sprints",
            "update",
            "4404",
            "--name",
            "Updated",
            "--start-date",
            "2026-11-02",
            "--end-date",
            "2026-11-16",
            "--status",
            "draft",
            "--version",
            "5",
        ],
        mcp=(
            "tracker_sprints_update",
            {
                "sprint_id": 4404,
                "body": {
                    "name": "Updated",
                    "start_date": "2026-11-02",
                    "end_date": "2026-11-16",
                    "status": "draft",
                },
                "version": 5,
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "sprints/4404",
                    {"version": "5"},
                    {
                        "name": "Updated",
                        "startDate": "2026-11-02",
                        "endDate": "2026-11-16",
                        "status": "draft",
                    },
                ),
                Reply(json={"id": 4404, "name": "Updated"}),
            )
        ],
    ),
    # Without a version no ?version= is sent.
    Case(
        "tracker.sprints.update",
        args=(4405, SprintUpdate(name="Unlocked")),
        cli=["tracker", "sprints", "update", "4405", "--name", "Unlocked"],
        mcp=("tracker_sprints_update", {"sprint_id": 4405, "body": {"name": "Unlocked"}}),
        exchanges=[
            (
                Sent("PATCH", "sprints/4405", json={"name": "Unlocked"}),
                Reply(json={"id": 4405, "name": "Unlocked"}),
            )
        ],
    ),
    Case(
        "tracker.sprints.delete",
        args=(4406,),
        cli=["tracker", "sprints", "delete", "4406"],
        mcp=("tracker_sprints_delete", {"sprint_id": 4406}),
        exchanges=[(Sent("DELETE", "sprints/4406"), Reply(status=204))],
    ),
    Case(
        "tracker.sprints.start",
        args=(4407,),
        kwargs={"version": 6},
        cli=["tracker", "sprints", "start", "4407", "--version", "6"],
        mcp=("tracker_sprints_start", {"sprint_id": 4407, "version": 6}),
        exchanges=[
            (
                Sent("POST", "sprints/4407/_start", {"version": "6"}),
                Reply(json={"id": 4407, "status": "in_progress"}),
            )
        ],
    ),
    Case(
        "tracker.sprints.start",
        args=(4408,),
        cli=["tracker", "sprints", "start", "4408"],
        mcp=("tracker_sprints_start", {"sprint_id": 4408}),
        exchanges=[
            (Sent("POST", "sprints/4408/_start"), Reply(json={"id": 4408, "status": "in_progress"}))
        ],
    ),
    Case(
        "tracker.sprints.archive",
        args=(4409,),
        kwargs={"version": 7},
        cli=["tracker", "sprints", "archive", "4409", "--version", "7"],
        mcp=("tracker_sprints_archive", {"sprint_id": 4409, "version": 7}),
        exchanges=[
            (
                Sent("POST", "sprints/4409/_archive", {"version": "7"}),
                Reply(json={"id": 4409, "status": "archived"}),
            )
        ],
    ),
]
