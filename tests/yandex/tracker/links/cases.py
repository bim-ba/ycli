"""Contract cases for Tracker issue ``/links`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

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
        args=("DE-42", {"relationship": "is dependent by", "issue": "OPS-9"}),
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
]
