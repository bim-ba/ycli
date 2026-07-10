"""TDD for DashboardsClient — responses stub + session DI (create + add widget)."""

import json

import requests
import responses

from ycli.yandex.tracker.dashboards.client import DashboardsClient
from ycli.yandex.tracker.dashboards.models import Dashboard, Widget

BASE = "https://api.tracker.yandex.net/v3"


def _client() -> DashboardsClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return DashboardsClient(session=session)


@responses.activate
def test_create_posts_body_and_returns_dashboard():
    responses.add(
        responses.POST, f"{BASE}/dashboards/", json={"id": 10, "name": "New Dashboard"}, status=201
    )
    dashboard = _client().create(body={"name": "New Dashboard", "layout": "one-column"})
    assert isinstance(dashboard, Dashboard)
    assert dashboard.id == 10 and dashboard.name == "New Dashboard"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "New Dashboard",
        "layout": "one-column",
    }


@responses.activate
def test_add_cycle_time_widget_posts_body():
    responses.add(
        responses.POST,
        f"{BASE}/dashboards/10/widgets/cycleTime",
        json={"id": 123456, "description": "My widget"},
        status=201,
    )
    widget = _client().add_cycle_time_widget(
        "10", body={"description": "My widget", "query": "Queue: TEST"}
    )
    assert isinstance(widget, Widget)
    assert widget.id == 123456
    assert responses.calls[0].request.url.endswith("/dashboards/10/widgets/cycleTime")  # ty: ignore[unresolved-attribute]
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "description": "My widget",
        "query": "Queue: TEST",
    }
