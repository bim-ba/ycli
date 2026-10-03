"""Contract cases for Forms notifications and show-errors (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.notifications.models import NotificationFilter

SID = "686d0a1b2c3d4e5f000000f0"


def _run(notification_id: int, status: str) -> dict:
    # The shape GET /notifications answered on the test organization (2026-10-02).
    return {
        "id": notification_id,
        "status": status,
        "created": "2026-10-02T17:01:08Z",
        "finished": "2026-10-02T17:05:00Z",
        "survey_id": SID,
        "survey_name": "Feedback",
        "hook_id": 31,
        "hook_name": "CRM",
        "subscription_id": 41,
        "answer_id": 51,
        "user_id": 13404023,
        "type": "http",
        "comment": "retry 3",
    }


FIRST = _run(9001, "error")
SECOND = _run(9002, "pending")
THIRD = _run(9003, "error")

FILTERS = {
    "survey_id": SID,
    "hook_id": "31",
    "subscription_id": "41",
    "answer_id": "51",
    "status": ["error", "pending"],
    "created_gt": "2026-09-01T00:00:00Z",
    "created_lt": "2026-09-30T00:00:00Z",
    "finished_gt": "2026-09-02T00:00:00Z",
    "finished_lt": "2026-09-29T00:00:00Z",
    "visible": "true",
    "type": "http",
    "ordering": "desc",
    "page_size": "100",
}
# The API prints the next page as a host-relative link to the same listing with a cursor added.
NEXT = (
    f"/v1/notifications/?survey_id={SID}&hook_id=31&subscription_id=41&answer_id=51"
    "&status=error&status=pending&created_gt=2026-09-01T00%3A00%3A00Z"
    "&created_lt=2026-09-30T00%3A00%3A00Z&finished_gt=2026-09-02T00%3A00%3A00Z"
    "&finished_lt=2026-09-29T00%3A00%3A00Z&visible=true&type=http&ordering=desc"
    "&page_size=100&id=9002"
)
DETAILS = {
    **_run(9100, "error"),
    "context": [{"name": "answer", "value": "ans 1", "type": "text"}],
    "response": [{"name": "status", "value": "502", "type": "text"}],
    "error": [{"name": "detail", "value": '{"error": "bad gateway"}', "type": "json"}],
}

CASES = [
    Case(
        "forms.notifications.list",
        args=(
            NotificationFilter(
                survey_id=SID,
                hook_id=31,
                subscription_id=41,
                answer_id=51,
                status=["error", "pending"],
                created_since="2026-09-01T00:00:00Z",
                created_until="2026-09-30T00:00:00Z",
                finished_since="2026-09-02T00:00:00Z",
                finished_until="2026-09-29T00:00:00Z",
                visible=True,
                integration_type="http",
                ordering="desc",
            ),
        ),
        kwargs={"limit": 500},
        cli=[
            "forms",
            "notifications",
            "list",
            "--survey-id",
            SID,
            "--hook-id",
            "31",
            "--subscription-id",
            "41",
            "--answer-id",
            "51",
            "--status",
            "error",
            "--status",
            "pending",
            "--created-since",
            "2026-09-01T00:00:00Z",
            "--created-until",
            "2026-09-30T00:00:00Z",
            "--finished-since",
            "2026-09-02T00:00:00Z",
            "--finished-until",
            "2026-09-29T00:00:00Z",
            "--visible",
            "--type",
            "http",
            "--ordering",
            "desc",
        ],
        mcp=(
            "forms_notifications_list",
            {
                "survey_id": SID,
                "hook_id": 31,
                "subscription_id": 41,
                "answer_id": 51,
                "status": ["error", "pending"],
                "created_since": "2026-09-01T00:00:00Z",
                "created_until": "2026-09-30T00:00:00Z",
                "finished_since": "2026-09-02T00:00:00Z",
                "finished_until": "2026-09-29T00:00:00Z",
                "visible": True,
                "integration_type": "http",
                "ordering": "desc",
            },
        ),
        exchanges=[
            (
                Sent("GET", "notifications", FILTERS),
                Reply(json={"links": {"next": NEXT}, "result": [FIRST, SECOND]}),
            ),
            (
                Sent("GET", "notifications", {**FILTERS, "id": "9002"}),
                Reply(json={"links": {}, "result": [THIRD]}),
            ),
        ],
        output=[FIRST, SECOND, THIRD],
    ),
    Case(
        "forms.notifications.list",
        args=(NotificationFilter(survey_id="686d0a1b2c3d4e5f000000f1"),),
        kwargs={"limit": 1},
        cli=[
            "forms",
            "notifications",
            "list",
            "--survey-id",
            "686d0a1b2c3d4e5f000000f1",
            "--limit",
            "1",
        ],
        mcp=(
            "forms_notifications_list",
            {"survey_id": "686d0a1b2c3d4e5f000000f1", "limit": 1},
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    "notifications",
                    {"survey_id": "686d0a1b2c3d4e5f000000f1", "page_size": "100"},
                ),
                Reply(
                    json={"links": {"next": "/v1/notifications/?id=9"}, "result": [FIRST, SECOND]}
                ),
            ),
        ],
        output=[FIRST],
    ),
    # Everything, with no filter: `--all` lifts the cap, so the SDK is asked for no limit.
    Case(
        "forms.notifications.list",
        args=(NotificationFilter(visible=False),),
        kwargs={"limit": None},
        cli=["forms", "notifications", "list", "--all", "--no-visible"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "notifications", {"visible": "false", "page_size": "100"}),
                Reply(json={"links": {}, "result": [THIRD]}),
            ),
        ],
        output=[THIRD],
    ),
    Case(
        "forms.notifications.get",
        args=(9100,),
        cli=["forms", "notifications", "get", "9100"],
        mcp=("forms_notifications_get", {"notification_id": 9100}),
        exchanges=[(Sent("GET", "notifications/9100"), Reply(json=DETAILS))],
    ),
    Case(
        "forms.notifications.status_get",
        args=(9101,),
        cli=["forms", "notifications", "status-get", "9101"],
        mcp=("forms_notifications_status_get", {"notification_id": 9101}),
        exchanges=[
            (
                Sent("GET", "notifications/9101/status"),
                Reply(json={"id": 9101, "status": "success"}),
            )
        ],
    ),
    Case(
        "forms.notifications.restart",
        args=(9102,),
        cli=["forms", "notifications", "restart", "9102"],
        mcp=("forms_notifications_restart", {"notification_id": 9102}),
        exchanges=[
            (
                Sent("POST", "notifications/9102/restart"),
                Reply(
                    json={
                        "id": 9102,
                        "survey_id": SID,
                        "subscription_id": 41,
                        "result": {"status": "operation", "operation_id": "op-5521"},
                    }
                ),
            )
        ],
    ),
    Case(
        "forms.notifications.cancel",
        args=(9103,),
        cli=["forms", "notifications", "cancel", "9103"],
        mcp=("forms_notifications_cancel", {"notification_id": 9103}),
        exchanges=[
            (
                Sent("POST", "notifications/9103/cancel"),
                Reply(
                    json={
                        "id": 9103,
                        "survey_id": SID,
                        "subscription_id": 42,
                        "result": {"status": "fail", "detail": "already finished"},
                    }
                ),
            )
        ],
    ),
    Case(
        "forms.notifications.errors_list",
        args=("686d0a1b2c3d4e5f000000f2",),
        cli=["forms", "notifications", "errors-list", "686d0a1b2c3d4e5f000000f2"],
        mcp=("forms_notifications_errors_list", {"survey_id": "686d0a1b2c3d4e5f000000f2"}),
        exchanges=[
            (Sent("GET", "surveys/686d0a1b2c3d4e5f000000f2/show-errors"), Reply(json=[9001, 9003]))
        ],
    ),
]
