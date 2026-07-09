"""Model parsing for Tracker external applications."""

from ycli.yandex.tracker.applications.models import Application, ApplicationList


def test_application_parses_self_and_type():
    app = Application.model_validate(
        {
            "self": "https://api.tracker.yandex.net/v3/applications/my-application",
            "id": "my-application",
            "type": "my-application",
            "name": "Application name",
        }
    )
    assert app.id == "my-application" and app.type == "my-application"
    assert app.self_url.endswith("/applications/my-application")  # ty: ignore[unresolved-attribute]


def test_application_list_is_flat_array():
    apps = ApplicationList.model_validate([{"id": "a"}, {"id": "b"}])
    assert [a.id for a in apps.root] == ["a", "b"]
