"""Contract cases for Tracker worklog (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from tests.unit.yandex.tracker.worklog.import_cases import IMPORT_CASES
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.tracker.worklog.models import WorklogCreate, WorklogSearch, WorklogUpdate

CASES = [
    # The default cap (500) asks for full 100-row pages and walks id=<last record id>.
    Case(
        "tracker.worklog.list",
        args=("DE-61",),
        kwargs={"limit": 500},
        cli=["tracker", "worklog", "list", "DE-61"],
        mcp=("tracker_worklog_list", {"issue_key": "DE-61"}),
        exchanges=[
            (
                Sent("GET", "issues/DE-61/worklog", {"perPage": "100"}),
                Reply(json=[{"id": 611, "duration": "PT1H"}, {"id": 612, "duration": "PT2H"}]),
            ),
            (
                Sent("GET", "issues/DE-61/worklog", {"perPage": "100", "id": "612"}),
                Reply(json=[{"id": 613, "duration": "PT3H"}]),
            ),
            (
                Sent("GET", "issues/DE-61/worklog", {"perPage": "100", "id": "613"}),
                Reply(json=[]),
            ),
        ],
    ),
    Case(
        "tracker.worklog.list",
        args=("DE-62",),
        kwargs={"limit": 3},
        cli=["tracker", "worklog", "list", "DE-62", "--limit", "3"],
        mcp=("tracker_worklog_list", {"issue_key": "DE-62", "limit": 3}),
        exchanges=[
            (
                Sent("GET", "issues/DE-62/worklog", {"perPage": "3"}),
                Reply(json=[{"id": 621, "duration": "PT30M"}]),
            ),
            (
                Sent("GET", "issues/DE-62/worklog", {"perPage": "3", "id": "621"}),
                Reply(json=[]),
            ),
        ],
    ),
    # `--all` is uncapped; a last record without an id ends the walk.
    Case(
        "tracker.worklog.list",
        args=("DE-63",),
        cli=["tracker", "worklog", "list", "DE-63", "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "issues/DE-63/worklog", {"perPage": "100"}),
                Reply(json=[{"duration": "P1D"}]),
            )
        ],
    ),
    Case(
        "tracker.worklog.search",
        args=(
            WorklogSearch.model_validate(
                {
                    "createdBy": "veikus",
                    "createdAt": {"from": "2018-06-06T00:00:00", "to": "2018-06-07T00:00:00"},
                }
            ),
        ),
        cli=[
            "tracker",
            "worklog",
            "search",
            "--created-by",
            "veikus",
            "--created-from",
            "2018-06-06T00:00:00",
            "--created-to",
            "2018-06-07T00:00:00",
        ],
        mcp=(
            "tracker_worklog_search",
            {
                "body": {
                    "createdBy": "veikus",
                    "createdAt": {"from": "2018-06-06T00:00:00", "to": "2018-06-07T00:00:00"},
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "worklog/_search",
                    json={
                        "createdBy": "veikus",
                        "createdAt": {"from": "2018-06-06T00:00:00", "to": "2018-06-07T00:00:00"},
                    },
                ),
                Reply(json=[{"id": 641, "duration": "PT2H"}]),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "tracker.worklog.search",
        args=(WorklogSearch.model_validate({}),),
        cli=["tracker", "worklog", "search"],
        mcp=("tracker_worklog_search", {"body": {}}),
        exchanges=[(Sent("POST", "worklog/_search", json={}), Reply(json=[]))],
        effect=Effect.READ,
    ),
    # createdAt is sent once for each end of the range.
    Case(
        "tracker.worklog.list_global",
        kwargs={"created_by": "alice", "created_from": "2019-01-01", "created_to": "2019-02-01"},
        cli=[
            "tracker",
            "worklog",
            "list-global",
            "--created-by",
            "alice",
            "--created-from",
            "2019-01-01",
            "--created-to",
            "2019-02-01",
        ],
        mcp=(
            "tracker_worklog_list_global",
            {"created_by": "alice", "created_from": "2019-01-01", "created_to": "2019-02-01"},
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "worklog",
                    {"createdBy": "alice", "createdAt": ["from:2019-01-01", "to:2019-02-01"]},
                ),
                Reply(json=[{"id": 651, "duration": "P3W"}]),
            )
        ],
    ),
    # One end alone.
    Case(
        "tracker.worklog.list_global",
        kwargs={"created_by": "bob", "created_from": "2020-03-04T05:06:07"},
        cli=[
            "tracker",
            "worklog",
            "list-global",
            "--created-by",
            "bob",
            "--created-from",
            "2020-03-04T05:06:07",
        ],
        mcp=(
            "tracker_worklog_list_global",
            {"created_by": "bob", "created_from": "2020-03-04T05:06:07"},
        ),
        exchanges=[
            (
                Sent(
                    "GET", "worklog", {"createdBy": "bob", "createdAt": "from:2020-03-04T05:06:07"}
                ),
                Reply(json=[{"id": 652, "duration": "PT1H"}]),
            )
        ],
    ),
    Case(
        "tracker.worklog.list_global",
        cli=["tracker", "worklog", "list-global"],
        mcp=("tracker_worklog_list_global", {}),
        exchanges=[(Sent("GET", "worklog"), Reply(json=[]))],
    ),
    Case(
        "tracker.worklog.create",
        args=(
            "DE-66",
            WorklogCreate.model_validate(
                {"duration": "PT2H", "start": "2021-03-04T10:00:00.000+0300", "comment": "pairing"}
            ),
        ),
        cli=[
            "tracker",
            "worklog",
            "create",
            "DE-66",
            "--duration",
            "PT2H",
            "--start",
            "2021-03-04T10:00:00.000+0300",
            "--comment",
            "pairing",
        ],
        mcp=(
            "tracker_worklog_create",
            {
                "issue_key": "DE-66",
                "body": {
                    "duration": "PT2H",
                    "start": "2021-03-04T10:00:00.000+0300",
                    "comment": "pairing",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/DE-66/worklog",
                    json={
                        "duration": "PT2H",
                        "start": "2021-03-04T10:00:00.000+0300",
                        "comment": "pairing",
                    },
                ),
                Reply(json={"id": 661, "duration": "PT2H"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.worklog.update",
        args=(
            "DE-67",
            "671",
            WorklogUpdate.model_validate({"duration": "PT45M", "comment": "trimmed"}),
        ),
        cli=[
            "tracker",
            "worklog",
            "update",
            "DE-67",
            "671",
            "--duration",
            "PT45M",
            "--comment",
            "trimmed",
        ],
        mcp=(
            "tracker_worklog_update",
            {
                "issue_key": "DE-67",
                "record_id": "671",
                "body": {"duration": "PT45M", "comment": "trimmed"},
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "issues/DE-67/worklog/671",
                    json={"duration": "PT45M", "comment": "trimmed"},
                ),
                Reply(json={"id": 671, "duration": "PT45M"}),
            )
        ],
    ),
    Case(
        "tracker.worklog.delete",
        args=("DE-68", "681"),
        cli=["tracker", "worklog", "delete", "DE-68", "681"],
        mcp=("tracker_worklog_delete", {"issue_key": "DE-68", "record_id": "681"}),
        exchanges=[(Sent("DELETE", "issues/DE-68/worklog/681"), Reply(status=204))],
    ),
]
CASES += IMPORT_CASES
