"""Contract cases for Tracker ``/dashboards`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "tracker.dashboards.create",
        args=({"name": "Team board", "layout": "two-columns", "owner": {"id": "alice"}},),
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
        "tracker.dashboards.add_cycle_time_widget",
        args=(
            "11",
            {
                "description": "Cycle time",
                "query": "Queue: DE",
                "fromStatuses": [{"key": "open"}],
                "toStatuses": [{"key": "closed"}],
                "mode": "common-lines",
            },
        ),
        cli=[
            "tracker",
            "dashboards",
            "add-widget",
            "cycletime",
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
            "tracker_dashboards_add_cycle_time_widget",
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
        "tracker.dashboards.add_cycle_time_widget",
        args=("12", {"description": "Bare widget"}),
        cli=[
            "tracker",
            "dashboards",
            "add-widget",
            "cycletime",
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
        args=({"name": "Solo board"},),
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
