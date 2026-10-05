"""Contract cases for Tracker board ``/columns`` (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.columns.models import ColumnCreate, ColumnUpdate

CASES = [
    Case(
        "tracker.columns.list",
        args=(73,),
        cli=["tracker", "columns", "list", "73"],
        mcp=("tracker_columns_list", {"board_id": 73}),
        exchanges=[
            (
                Sent("GET", "boards/73/columns"),
                Reply(json=[{"id": 1, "name": "Open", "statuses": [{"key": "open"}]}]),
            )
        ],
    ),
    Case(
        "tracker.columns.get",
        args=(74, 2),
        cli=["tracker", "columns", "get", "74", "2"],
        mcp=("tracker_columns_get", {"board_id": 74, "column_id": 2}),
        exchanges=[(Sent("GET", "boards/74/columns/2"), Reply(json={"id": 2, "name": "Review"}))],
    ),
    Case(
        "tracker.columns.create",
        args=(75, ColumnCreate(name="Approve", statuses=["needInfo", "adjustment"])),
        cli=[
            "tracker",
            "columns",
            "create",
            "75",
            "--name",
            "Approve",
            "--status",
            "needInfo",
            "--status",
            "adjustment",
        ],
        mcp=(
            "tracker_columns_create",
            {"board_id": 75, "body": {"name": "Approve", "statuses": ["needInfo", "adjustment"]}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "boards/75/columns/",
                    json={"name": "Approve", "statuses": ["needInfo", "adjustment"]},
                ),
                Reply(json={"id": 5, "name": "Approve"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.columns.update",
        args=(76, 6, ColumnUpdate(name="Pause", statuses=["paused", "blocked"])),
        cli=[
            "tracker",
            "columns",
            "update",
            "76",
            "6",
            "--name",
            "Pause",
            "--status",
            "paused",
            "--status",
            "blocked",
        ],
        mcp=(
            "tracker_columns_update",
            {
                "board_id": 76,
                "column_id": 6,
                "body": {"name": "Pause", "statuses": ["paused", "blocked"]},
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "boards/76/columns/6",
                    json={"name": "Pause", "statuses": ["paused", "blocked"]},
                ),
                Reply(json={"id": 6, "name": "Pause"}),
            )
        ],
    ),
    # Only the supplied fields are sent.
    Case(
        "tracker.columns.update",
        args=(77, 7, ColumnUpdate(name="Waiting")),
        cli=["tracker", "columns", "update", "77", "7", "--name", "Waiting"],
        mcp=(
            "tracker_columns_update",
            {"board_id": 77, "column_id": 7, "body": {"name": "Waiting"}},
        ),
        exchanges=[
            (
                Sent("PATCH", "boards/77/columns/7", json={"name": "Waiting"}),
                Reply(json={"id": 7, "name": "Waiting"}),
            )
        ],
    ),
    Case(
        "tracker.columns.delete",
        args=(78, 8),
        cli=["tracker", "columns", "delete", "78", "8"],
        mcp=("tracker_columns_delete", {"board_id": 78, "column_id": 8}),
        exchanges=[(Sent("DELETE", "boards/78/columns/8"), Reply(status=204))],
    ),
]
