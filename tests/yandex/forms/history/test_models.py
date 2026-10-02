"""Forms change-log models parse what the live API returns."""

from ycli.yandex.forms.history.models import HistoryPage

# As GET /surveys/{id}/history?limit=2 answered on the test organization (2026-10-02).
LIVE = {
    "iteration_key": 406971226,
    "limit": 2,
    "items": [
        {
            "id": 406971234,
            "created": "2026-10-02T14:29:33Z",
            "user": {
                "identity": {"uid": "101523906", "cloud_uid": "ajen8nffceu4rqs0i39r"},
                "username": "znatnov-sava",
                "display_name": "Сава Знатнов",
            },
            "model": "servicesurveyhooksubscription",
            "action": "POST api-v1:get_subscriptions_public_view",
        }
    ],
}


def test_history_page_parses_live_answer():
    page = HistoryPage.model_validate(LIVE)
    assert page.iteration_key == 406971226 and page.limit == 2
    event = page.items[0]
    assert event.user and event.user.username == "znatnov-sava"
    assert event.model == "servicesurveyhooksubscription"
