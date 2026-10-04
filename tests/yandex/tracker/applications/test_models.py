"""Model parsing for Tracker external applications."""

from ycli.yandex.tracker.applications.models import Application


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
