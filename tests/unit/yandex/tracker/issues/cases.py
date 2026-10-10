"""Contract cases for Tracker ``/issues`` (see tests/contract/)."""

import httpx2

from tests.contract import Case, Reply, Sent, with_query
from tests.unit.yandex.tracker.issues.bulk_cases import BULK_CASES
from tests.unit.yandex.tracker.issues.import_cases import IMPORT_CASES
from ycli.yandex.core import continuation
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.tracker.issues.models import IssueCreate, IssueSearch, IssueUpdate

ISSUE = {"key": "DE-7", "summary": "Fix the login page"}
_SCROLLED = httpx2.Request(
    "POST", "https://api.tracker.yandex.net/v3/issues/_search?scrollType=sorted&scrollId=scroll-1"
)
# The `next` of a search by a scroll in the organization of the tests: it keeps what the
# replies of the scroll carried, its id and its own token.
OF_A_SCROLL = continuation.encode(
    _SCROLLED,
    _SCROLLED,
    way="ScrollPagination",
    skip=0,
    seen=2,
    organization="X-Org-Id: o",
    kept={"scrollId": "scroll-1", "scrollToken": "token-1"},
)
SEARCH = {"page": "1", "perPage": "100"}

CASES = [
    Case(
        "tracker.issues.get",
        args=("DE-7",),
        cli=["tracker", "issues", "get", "DE-7"],
        mcp=("tracker_issues_get", {"issue_key": "DE-7"}),
        exchanges=[(Sent("GET", "issues/DE-7"), Reply(json=ISSUE))],
    ),
    Case(
        "tracker.issues.search",
        args=(
            IssueSearch.model_validate(
                {"filter": {"queue": "DE", "status": "open", "assignee": "alice"}}
            ),
        ),
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
        effect=Effect.READ,
    ),
    Case(
        "tracker.issues.search",
        args=(IssueSearch.model_validate({"query": "Queue: DE"}),),
        kwargs={"limit": 3},
        cli=["tracker", "issues", "search", "Queue: DE", "--limit", "3"],
        mcp=("tracker_issues_search", {"body": {"query": "Queue: DE"}, "limit": 3}),
        exchanges=[
            (
                Sent(
                    "POST", "issues/_search", {"page": "1", "perPage": "3"}, {"query": "Queue: DE"}
                ),
                Reply(json=[ISSUE]),
            )
        ],
        effect=Effect.READ,
    ),
    # By a filter on a field the short listing has no parameter for.
    Case(
        "tracker.issues.search",
        args=(IssueSearch.model_validate({"filter": {"queue": "DE", "priority": "critical"}}),),
        kwargs={"limit": 4},
        cli=None,
        mcp=(
            "tracker_issues_search",
            {"body": {"filter": {"queue": "DE", "priority": "critical"}}, "limit": 4},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/_search",
                    {"page": "1", "perPage": "4"},
                    {"filter": {"queue": "DE", "priority": "critical"}},
                ),
                Reply(json=[ISSUE]),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "tracker.issues.count",
        args=(IssueSearch.model_validate({"filter": {"queue": "DE", "status": "open"}}),),
        cli=["tracker", "issues", "count", "--queue", "DE", "--status", "open"],
        mcp=("tracker_issues_count", {"body": {"filter": {"queue": "DE", "status": "open"}}}),
        exchanges=[
            (
                Sent("POST", "issues/_count", json={"filter": {"queue": "DE", "status": "open"}}),
                Reply(json=12),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "tracker.issues.create",
        args=(
            IssueCreate.model_validate(
                {"queue": "DE", "summary": "New", "type": {"key": "bug"}, "tags": ["ui"]}
            ),
        ),
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
        args=(
            "DE-7",
            IssueUpdate.model_validate({"summary": "Renamed", "priority": {"key": "critical"}}),
        ),
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
            {"issue_key": "DE-7", "body": {"summary": "Renamed", "priority": {"key": "critical"}}},
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
        mcp=("tracker_issues_move", {"issue_key": "DE-7", "queue": "OPS"}),
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
        args=(OF_A_SCROLL,),
        cli=["tracker", "issues", "scroll-clear", "--next", OF_A_SCROLL],
        mcp=("tracker_issues_scroll_clear", {"next": OF_A_SCROLL}),
        exchanges=[
            (Sent("POST", "system/search/scroll/_clear", json={"scroll-1": "token-1"}), Reply())
        ],
        effect=Effect.IDEMPOTENT_WRITE,
    ),
    Case(
        "tracker.issues.count",
        args=(IssueSearch.model_validate({"query": "Queue: DE AND Status: open"}),),
        cli=["tracker", "issues", "count", "--query", "Queue: DE AND Status: open"],
        mcp=("tracker_issues_count", {"body": {"query": "Queue: DE AND Status: open"}}),
        exchanges=[
            (
                Sent("POST", "issues/_count", json={"query": "Queue: DE AND Status: open"}),
                Reply(json=3),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "tracker.issues.create",
        args=(
            IssueCreate.model_validate({"queue": "OPS", "summary": "Only the required options"}),
        ),
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
    # `--description ""` clears the body; `-F` adds fields under the options (an option wins
    # over it), and an explicit null is sent.
    Case(
        "tracker.issues.update",
        args=(
            "DE-8",
            IssueUpdate.model_validate(
                {"summary": "A", "description": "", "assignee": None, "sprint": 7}
            ),
        ),
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
                    json={"summary": "A", "description": "", "assignee": None, "sprint": 7},
                ),
                Reply(json=ISSUE),
            )
        ],
    ),
]

# The query parameters the published API lists beyond the ones above (#196).
CASES += [
    with_query(
        CASES,
        "tracker.issues.get",
        kwargs={"expand": "transitions", "fields": "summary,status"},
        cli=["--expand", "transitions", "--fields", "summary,status"],
        params={"expand": "transitions", "fields": "summary,status"},
    ),
    with_query(
        CASES,
        "tracker.issues.create",
        kwargs={"notify": False},
        cli=["--no-notify"],
        params={"notify": "false"},
    ),
    with_query(
        CASES,
        "tracker.issues.move",
        kwargs={
            "expand": "transitions",
            "initial_status": True,
            "move_all_fields": True,
            "notify": False,
            "notify_author": True,
        },
        cli=[
            "--expand",
            "transitions",
            "--initial-status",
            "--move-all-fields",
            "--no-notify",
            "--notify-author",
        ],
        params={
            "expand": "transitions",
            "initialStatus": "true",
            "moveAllFields": "true",
            "notify": "false",
            "notifyAuthor": "true",
        },
    ),
    with_query(
        CASES,
        "tracker.issues.suggest",
        kwargs={
            "queue": "DE",
            "full": True,
            "fields": "summary",
            "expand": "transitions",
            "embed": "transitions",
        },
        cli=[
            "--queue",
            "DE",
            "--full",
            "--fields",
            "summary",
            "--expand",
            "transitions",
            "--embed",
            "transitions",
        ],
        params={
            "queue": "DE",
            "full": "true",
            "fields": "summary",
            "expand": "transitions",
            "embed": "transitions",
        },
    ),
]
_SCROLL = {
    "expand": "transitions",
    "scrollType": "sorted",
    "perScroll": "2",
    "scrollTTLMillis": "10000",
}
CASES += [
    # Scrolling has no 10 000 cap: each reply names the next page in a header.
    Case(
        "tracker.issues.search",
        args=(IssueSearch.model_validate({"query": "Queue: BIG"}),),
        kwargs={
            "limit": 500,
            "expand": "transitions",
            "scroll_type": "sorted",
            "per_scroll": 2,
            "scroll_ttl_millis": 10000,
        },
        cli=[
            "tracker",
            "issues",
            "search",
            "Queue: BIG",
            "--expand",
            "transitions",
            "--scroll-type",
            "sorted",
            "--per-scroll",
            "2",
            "--scroll-ttl-millis",
            "10000",
        ],
        mcp=(
            "tracker_issues_search",
            {
                "body": {"query": "Queue: BIG"},
                "expand": "transitions",
                "scroll_type": "sorted",
                "per_scroll": 2,
                "scroll_ttl_millis": 10000,
            },
        ),
        exchanges=[
            (
                Sent("POST", "issues/_search", _SCROLL, {"query": "Queue: BIG"}),
                Reply(json=[{"key": "BIG-1"}, {"key": "BIG-2"}], headers={"X-Scroll-Id": "scr-1"}),
            ),
            (
                Sent(
                    "POST",
                    "issues/_search",
                    {**_SCROLL, "scrollId": "scr-1"},
                    {"query": "Queue: BIG"},
                ),
                Reply(json=[{"key": "BIG-3"}], headers={"X-Scroll-Id": "scr-2"}),
            ),
            (
                Sent(
                    "POST",
                    "issues/_search",
                    {**_SCROLL, "scrollId": "scr-2"},
                    {"query": "Queue: BIG"},
                ),
                Reply(json=[]),
            ),
        ],
        effect=Effect.READ,
    ),
]
CASES += BULK_CASES
CASES += IMPORT_CASES
