"""Contract cases for Tracker ``/dashboards`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.dashboards.models import CycleTimeWidget, DashboardCreate

CASES = [
    Case(
        "tracker.dashboards.create",
        args=(
            DashboardCreate.model_validate(
                {"name": "Team board", "layout": "two-columns", "owner": {"id": "alice"}}
            ),
        ),
        cli=[
            "tracker",
            "dashboards",
            "create",
            "--name",
            "Team board",
            "--layout",
            "two-columns",
            "--owner",
            "alice",
        ],
        mcp=(
            "tracker_dashboards_create",
            {"body": {"name": "Team board", "layout": "two-columns", "owner": {"id": "alice"}}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "dashboards/",
                    json={"name": "Team board", "layout": "two-columns", "owner": {"id": "alice"}},
                ),
                Reply(json={"id": 10, "name": "Team board"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.dashboards.widgets_create_cycle_time",
        args=(
            "11",
            CycleTimeWidget.model_validate(
                {
                    "description": "Cycle time",
                    "query": "Queue: DE",
                    "fromStatuses": [{"key": "open"}],
                    "toStatuses": [{"key": "closed"}],
                    "mode": "common-lines",
                }
            ),
        ),
        cli=[
            "tracker",
            "dashboards",
            "widgets-create-cycle-time",
            "11",
            "--description",
            "Cycle time",
            "--query",
            "Queue: DE",
            "--from-status",
            "open",
            "--to-status",
            "closed",
            "--mode",
            "common-lines",
        ],
        mcp=(
            "tracker_dashboards_widgets_create_cycle_time",
            {
                "dashboard_id": "11",
                "body": {
                    "description": "Cycle time",
                    "query": "Queue: DE",
                    "fromStatuses": [{"key": "open"}],
                    "toStatuses": [{"key": "closed"}],
                    "mode": "common-lines",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "dashboards/11/widgets/cycleTime",
                    json={
                        "description": "Cycle time",
                        "query": "Queue: DE",
                        "fromStatuses": [{"key": "open"}],
                        "toStatuses": [{"key": "closed"}],
                        "mode": "common-lines",
                    },
                ),
                Reply(json={"id": 123456, "description": "Cycle time"}, status=201),
            )
        ],
    ),
    # Only the required options: the CLI leaves every optional key out of the body.
    Case(
        "tracker.dashboards.widgets_create_cycle_time",
        args=("12", CycleTimeWidget.model_validate({"description": "Bare widget"})),
        cli=[
            "tracker",
            "dashboards",
            "widgets-create-cycle-time",
            "12",
            "--description",
            "Bare widget",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST", "dashboards/12/widgets/cycleTime", json={"description": "Bare widget"}
                ),
                Reply(json={"id": 7}, status=201),
            )
        ],
    ),
    Case(
        "tracker.dashboards.create",
        args=(DashboardCreate.model_validate({"name": "Solo board"}),),
        cli=["tracker", "dashboards", "create", "--name", "Solo board"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "dashboards/", json={"name": "Solo board"}),
                Reply(json={"id": 13, "name": "Solo board"}, status=201),
            )
        ],
    ),
]
