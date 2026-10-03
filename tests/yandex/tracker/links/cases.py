"""Contract cases for Tracker issue ``/links`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.links.models import LinkCreate

CASES = [
    Case(
        "tracker.links.list",
        args=("DE-41",),
        cli=["tracker", "links", "list", "DE-41"],
        mcp=("tracker_links_list", {"key": "DE-41"}),
        exchanges=[
            (
                Sent("GET", "issues/DE-41/links"),
                Reply(json=[{"id": 411, "type": {"id": "depends"}, "object": {"key": "DE-40"}}]),
            )
        ],
    ),
    Case(
        "tracker.links.add",
        args=(
            "DE-42",
            LinkCreate.model_validate({"relationship": "is dependent by", "issue": "OPS-9"}),
        ),
        cli=["tracker", "links", "add", "DE-42", "is dependent by", "OPS-9"],
        mcp=(
            "tracker_links_add",
            {"key": "DE-42", "body": {"relationship": "is dependent by", "issue": "OPS-9"}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/DE-42/links",
                    json={"relationship": "is dependent by", "issue": "OPS-9"},
                ),
                Reply(json={"id": 421, "object": {"key": "OPS-9"}}, status=201),
            )
        ],
    ),
    Case(
        "tracker.links.delete",
        args=("DE-43", "431"),
        cli=["tracker", "links", "delete", "DE-43", "431"],
        mcp=("tracker_links_delete", {"key": "DE-43", "link_id": "431"}),
        exchanges=[(Sent("DELETE", "issues/DE-43/links/431"), Reply(status=204))],
    ),
    Case(
        "tracker.links.search",
        args=("DE-44",),
        kwargs={"link_types": ["relates", "subtask"], "fields": ["id", "type"]},
        cli=[
            "tracker",
            "links",
            "search",
            "DE-44",
            "--type",
            "relates",
            "--type",
            "subtask",
            "--field",
            "id",
            "--field",
            "type",
        ],
        mcp=(
            "tracker_links_search",
            {"key": "DE-44", "link_types": ["relates", "subtask"], "fields": ["id", "type"]},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/DE-44/links/_list",
                    {"page": "1", "perPage": "50"},
                    {"fields": ["id", "type"], "linkTypes": ["relates", "subtask"]},
                ),
                Reply(
                    json={
                        "links": [{"id": 441, "type": {"id": "relates"}, "direction": "outward"}]
                    },
                    headers={"X-Total-Pages": "2"},
                ),
            ),
            (
                Sent(
                    "POST",
                    "issues/DE-44/links/_list",
                    {"page": "2", "perPage": "50"},
                    {"fields": ["id", "type"], "linkTypes": ["relates", "subtask"]},
                ),
                Reply(json={"links": [{"id": 442, "type": {"id": "subtask"}}]}),
            ),
        ],
        effect="read",
    ),
    # No filters: an empty body, one page; --limit stops the walk, --all lifts the cap.
    Case(
        "tracker.links.search",
        args=("DE-45",),
        kwargs={"limit": 1},
        cli=["tracker", "links", "search", "DE-45", "--limit", "1"],
        mcp=("tracker_links_search", {"key": "DE-45", "limit": 1}),
        exchanges=[
            (
                Sent("POST", "issues/DE-45/links/_list", {"page": "1", "perPage": "50"}, {}),
                Reply(
                    json={
                        "links": [
                            {
                                "id": 451,
                                "createdBy": {"display": "Ann"},
                                "createdAt": "2024-01-02T03:04:05.000+0000",
                                "status": {"key": "open"},
                                "assignee": {"display": "Bob"},
                            },
                            {"id": 452},
                        ]
                    }
                ),
            )
        ],
        effect="read",
        output=[
            {
                "id": 451,
                "type": None,
                "direction": None,
                "object": None,
                "createdBy": "Ann",
                "updatedBy": None,
                "createdAt": "2024-01-02T03:04:05.000+0000",
                "updatedAt": None,
                "assignee": "Bob",
                "status": "open",
            }
        ],
    ),
    Case(
        "tracker.links.search",
        args=("DE-46",),
        kwargs={"limit": None},
        cli=["tracker", "links", "search", "DE-46", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", "issues/DE-46/links/_list", {"page": "1", "perPage": "50"}, {}),
                Reply(json={"links": [{"id": 461}]}),
            )
        ],
        effect="read",
    ),
]
