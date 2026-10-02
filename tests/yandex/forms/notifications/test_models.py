"""Forms notification models parse what the live API returns."""

from ycli.yandex.forms.notifications.models import (
    NotificationAction,
    NotificationDetails,
    NotificationPage,
)

# As GET /notifications?page_size=1 answered on the test organization (2026-10-02).
LIVE_PAGE = {
    "links": {
        "next": "/v1/notifications/?survey_id=6abfe340381ea600272b5f37&page_size=1&id=744734775"
    },
    "result": [
        {
            "id": 744734758,
            "status": "pending",
            "created": "2026-10-02T17:01:08Z",
            "survey_id": "6abfe340381ea600272b5f37",
            "survey_name": "zz-forms-cov-1790960445",
            "hook_id": 18747704,
            "hook_name": "probe",
            "subscription_id": 19060213,
            "answer_id": 2542493937,
            "user_id": 13404023,
            "type": "http",
        }
    ],
}


def test_page_parses_live_answer_and_its_next_link():
    page = NotificationPage.model_validate(LIVE_PAGE)
    assert page.links.next and page.links.next.endswith("id=744734775")
    assert page.result[0].status == "pending" and page.result[0].finished is None


def test_page_without_links_has_no_next_link():
    assert NotificationPage.model_validate({"result": []}).links.next is None


def test_details_keep_context_response_and_error_fields():
    details = NotificationDetails.model_validate(
        {
            "id": 7,
            "status": "error",
            "context": [{"name": "answer", "value": "x"}],
            "error": [{"name": "detail", "value": "timeout", "type": "text"}],
        }
    )
    assert details.context and details.context[0].name == "answer"
    assert details.response is None
    assert details.error and details.error[0].value == "timeout"


def test_action_result_variants():
    ok = NotificationAction.model_validate({"id": 1, "survey_id": "s", "result": {"status": "ok"}})
    background = NotificationAction.model_validate(
        {"id": 2, "survey_id": "s", "result": {"status": "operation", "operation_id": "op-1"}}
    )
    assert ok.result and ok.result.operation_id is None
    assert background.result and background.result.operation_id == "op-1"
