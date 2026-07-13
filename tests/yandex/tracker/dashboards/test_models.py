"""TDD for Tracker dashboard/widget models — response parse + typed create bodies."""

from ycli.yandex.tracker.dashboards.models import (
    CycleTimeWidget,
    Dashboard,
    DashboardCreate,
    DashboardOwner,
    Widget,
)

DASHBOARD_SAMPLE = {
    "id": 10,
    "version": 1,
    "name": "New Dashboard",
    "createdBy": {"id": "11", "display": "Full Name"},
    "createdAt": "2024-04-15T19:38:42.074+0000",
    "layout": "one-column",
    "owner": {"id": "11", "display": "Full Name"},
    "self": "https://api.tracker.yandex.net/v3/dashboards/10",
}

WIDGET_SAMPLE = {
    "id": 123456,
    "version": 1,
    "description": "My widget",
    "dashboard": {"id": "118899", "display": "My dashboard"},
    "query": "Queue: TEST Assignee: me()",
    "start": "now()-2w",
    "end": "now()-2d",
    "mode": "common-lines-and-points",
    "self": "https://api.tracker.yandex.net/v3/widgets/123456",
}


def test_dashboard_parses_all_fields():
    dashboard = Dashboard.model_validate(DASHBOARD_SAMPLE)
    assert dashboard.id == 10
    assert dashboard.name == "New Dashboard"
    assert dashboard.layout == "one-column"
    assert dashboard.created_by == "Full Name"  # createdBy flattened to display
    assert dashboard.owner == "Full Name"  # owner flattened to display
    assert dashboard.self_url.endswith("/dashboards/10")  # ty: ignore[unresolved-attribute]


def test_widget_parses_all_fields():
    widget = Widget.model_validate(WIDGET_SAMPLE)
    assert widget.id == 123456
    assert widget.description == "My widget"
    assert widget.dashboard == "My dashboard"  # dashboard flattened to display
    assert widget.query.startswith("Queue: TEST")  # ty: ignore[unresolved-attribute]
    assert widget.mode == "common-lines-and-points"


def test_dashboard_create_body():
    body = DashboardCreate(
        name="Team board", layout="two-columns", owner=DashboardOwner(id="user")
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {"name": "Team board", "layout": "two-columns", "owner": {"id": "user"}}


def test_dashboard_create_omits_absent_optionals():
    body = DashboardCreate(name="Solo").model_dump(by_alias=True, exclude_none=True)
    assert body == {"name": "Solo"}


def test_cycle_time_widget_body_uses_camel_case_aliases():
    body = CycleTimeWidget(
        description="My widget",
        query="Queue: TEST",
        from_statuses=[{"key": "open"}],  # ty: ignore[unknown-argument]
        to_statuses=[{"key": "closed"}],  # ty: ignore[unknown-argument]
        filter_id=1234,  # ty: ignore[unknown-argument]
        auto_updatable=True,  # ty: ignore[unknown-argument]
        mode="common-lines",
    ).model_dump(by_alias=True, exclude_none=True)
    assert body == {
        "description": "My widget",
        "query": "Queue: TEST",
        "fromStatuses": [{"key": "open"}],
        "toStatuses": [{"key": "closed"}],
        "filterId": 1234,
        "autoUpdatable": True,
        "mode": "common-lines",
    }
