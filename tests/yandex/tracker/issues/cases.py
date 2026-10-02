"""Contract cases for Tracker ``/issues`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

ISSUE = {"key": "DE-7", "summary": "Fix the login page"}
SEARCH = {"page": "1", "perPage": "100"}

CASES = [
    Case(
        "tracker.issues.get",
        args=("DE-7",),
        cli=["tracker", "issues", "get", "DE-7"],
        mcp=("tracker_issues_get", {"key": "DE-7"}),
        exchanges=[(Sent("GET", "issues/DE-7"), Reply(json=ISSUE))],
    ),
    Case(
        "tracker.issues.search",
        args=({"filter": {"queue": "DE", "status": "open", "assignee": "alice"}},),
        kwargs={"limit": 500},
        cli=[
            "tracker",
            "issues",
            "list",
            "--queue",
            "DE",
            "--status",
            "open",
            "--assignee",
            "alice",
        ],
        mcp=("tracker_issues_list", {"queue": "DE", "status": "open", "assignee": "alice"}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/_search",
                    SEARCH,
                    {"filter": {"queue": "DE", "status": "open", "assignee": "alice"}},
                ),
                Reply(json=[ISSUE]),
            )
        ],
        effect="read",
    ),
    Case(
        "tracker.issues.search",
        args=({"query": "Queue: DE"},),
        kwargs={"limit": 3},
        cli=["tracker", "issues", "search", "Queue: DE", "--limit", "3"],
        mcp=("tracker_issues_search", {"query": "Queue: DE", "limit": 3}),
        exchanges=[
            (
                Sent(
                    "POST", "issues/_search", {"page": "1", "perPage": "3"}, {"query": "Queue: DE"}
                ),
                Reply(json=[ISSUE]),
            )
        ],
        effect="read",
    ),
    Case(
        "tracker.issues.count",
        args=({"filter": {"queue": "DE", "status": "open"}},),
        cli=["tracker", "issues", "count", "--queue", "DE", "--status", "open"],
        mcp=("tracker_issues_count", {"queue": "DE", "status": "open"}),
        exchanges=[
            (
                Sent("POST", "issues/_count", json={"filter": {"queue": "DE", "status": "open"}}),
                Reply(json=12),
            )
        ],
        effect="read",
    ),
    Case(
        "tracker.issues.create",
        args=({"queue": "DE", "summary": "New", "type": {"key": "bug"}, "tags": ["ui"]},),
        cli=[
            "tracker",
            "issues",
            "create",
            "--queue",
            "DE",
            "--summary",
            "New",
            "--type",
            "bug",
            "--tag",
            "ui",
        ],
        mcp=(
            "tracker_issues_create",
            {"body": {"queue": "DE", "summary": "New", "type": {"key": "bug"}, "tags": ["ui"]}},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/",
                    json={"queue": "DE", "summary": "New", "type": {"key": "bug"}, "tags": ["ui"]},
                ),
                Reply(json=ISSUE, status=201),
            )
        ],
    ),
    Case(
        "tracker.issues.update",
        args=("DE-7", {"summary": "Renamed", "priority": {"key": "critical"}}),
        cli=[
            "tracker",
            "issues",
            "update",
            "DE-7",
            "--summary",
            "Renamed",
            "--priority",
            "critical",
        ],
        mcp=(
            "tracker_issues_update",
            {"key": "DE-7", "body": {"summary": "Renamed", "priority": {"key": "critical"}}},
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "issues/DE-7",
                    json={"summary": "Renamed", "priority": {"key": "critical"}},
                ),
                Reply(json=ISSUE),
            )
        ],
    ),
    Case(
        "tracker.issues.move",
        args=("DE-7", "OPS"),
        cli=["tracker", "issues", "move", "DE-7", "OPS"],
        mcp=("tracker_issues_move", {"key": "DE-7", "queue": "OPS"}),
        exchanges=[(Sent("POST", "issues/DE-7/_move", {"queue": "OPS"}), Reply(json=ISSUE))],
    ),
    Case(
        "tracker.issues.suggest",
        args=("login",),
        cli=["tracker", "issues", "suggest", "login"],
        mcp=("tracker_issues_suggest", {"text": "login"}),
        exchanges=[(Sent("GET", "issues/_suggest", {"input": "login"}), Reply(json=[ISSUE]))],
    ),
    Case(
        "tracker.issues.scroll_clear",
        args=({"scroll-1": "token-1"},),
        cli=["tracker", "issues", "scroll-clear", "--pair", "scroll-1=token-1"],
        mcp=("tracker_issues_scroll_clear", {"body": {"scroll-1": "token-1"}}),
        exchanges=[
            (Sent("POST", "system/search/scroll/_clear", json={"scroll-1": "token-1"}), Reply())
        ],
        effect="idempotent_write",
    ),
    Case(
        "tracker.issues.count",
        args=({"query": "Queue: DE AND Status: open"},),
        cli=["tracker", "issues", "count", "--query", "Queue: DE AND Status: open"],
        mcp=("tracker_issues_count", {"query": "Queue: DE AND Status: open"}),
        exchanges=[
            (
                Sent("POST", "issues/_count", json={"query": "Queue: DE AND Status: open"}),
                Reply(json=3),
            )
        ],
        effect="read",
    ),
    Case(
        "tracker.issues.create",
        args=({"queue": "OPS", "summary": "Only the required options"},),
        cli=[
            "tracker",
            "issues",
            "create",
            "--queue",
            "OPS",
            "--summary",
            "Only the required options",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST", "issues/", json={"queue": "OPS", "summary": "Only the required options"}
                ),
                Reply(json=ISSUE, status=201),
            )
        ],
    ),
    # `--description ""` clears the body; `--field` merges last, overriding an option, and an
    # explicit null is sent.
    Case(
        "tracker.issues.update",
        args=("DE-8", {"summary": "B", "description": "", "assignee": None, "sprint": 7}),
        cli=[
            "tracker",
            "issues",
            "update",
            "DE-8",
            "--summary",
            "A",
            "--description",
            "",
            "-F",
            "summary=B",
            "-F",
            "assignee=null",
            "-F",
            "sprint=7",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "issues/DE-8",
                    json={"summary": "B", "description": "", "assignee": None, "sprint": 7},
                ),
                Reply(json=ISSUE),
            )
        ],
    ),
]
