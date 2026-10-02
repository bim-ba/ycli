"""Contract cases for Tracker saved ``/filters`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.filters.models import FilterCreate, FilterUpdate

CASES = [
    Case(
        "tracker.filters.get",
        args=("12345",),
        cli=["tracker", "filters", "get", "12345"],
        mcp=("tracker_filters_get", {"filter_id": "12345"}),
        exchanges=[
            (Sent("GET", "filters/12345"), Reply(json={"id": 12345, "name": "My open issues"}))
        ],
    ),
    Case(
        "tracker.filters.create",
        args=(
            FilterCreate(
                name="My open",
                query="Assignee: me() Resolution: empty()",
                filter={"status": "open"},
            ),
        ),
        cli=[
            "tracker",
            "filters",
            "create",
            "--name",
            "My open",
            "--query",
            "Assignee: me() Resolution: empty()",
            "--filter",
            '{"status": "open"}',
        ],
        mcp=(
            "tracker_filters_create",
            {
                "body": {
                    "name": "My open",
                    "query": "Assignee: me() Resolution: empty()",
                    "filter": {"status": "open"},
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "filters/",
                    json={
                        "name": "My open",
                        "filter": {"status": "open"},
                        "query": "Assignee: me() Resolution: empty()",
                    },
                ),
                Reply(json={"id": 12346, "name": "My open"}, status=201),
            )
        ],
    ),
    # No ?version= lock; the filter object is replaced whole.
    Case(
        "tracker.filters.edit",
        args=(
            "12347",
            FilterUpdate(name="Renamed", query="Queue: OPS", filter={"queue": "OPS"}),
        ),
        cli=[
            "tracker",
            "filters",
            "update",
            "12347",
            "--name",
            "Renamed",
            "--query",
            "Queue: OPS",
            "--filter",
            '{"queue": "OPS"}',
        ],
        mcp=(
            "tracker_filters_update",
            {
                "filter_id": "12347",
                "body": {"name": "Renamed", "query": "Queue: OPS", "filter": {"queue": "OPS"}},
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "filters/12347",
                    json={"name": "Renamed", "filter": {"queue": "OPS"}, "query": "Queue: OPS"},
                ),
                Reply(json={"id": 12347, "name": "Renamed"}),
            )
        ],
    ),
    # Only the supplied fields are sent.
    Case(
        "tracker.filters.edit",
        args=("12348", FilterUpdate(name="Only the name")),
        cli=["tracker", "filters", "update", "12348", "--name", "Only the name"],
        mcp=("tracker_filters_update", {"filter_id": "12348", "body": {"name": "Only the name"}}),
        exchanges=[
            (
                Sent("PATCH", "filters/12348", json={"name": "Only the name"}),
                Reply(json={"id": 12348, "name": "Only the name"}),
            )
        ],
    ),
    Case(
        "tracker.filters.delete",
        args=("12349",),
        cli=["tracker", "filters", "delete", "12349"],
        mcp=("tracker_filters_delete", {"filter_id": "12349"}),
        exchanges=[(Sent("DELETE", "filters/12349"), Reply(status=204))],
    ),
]
