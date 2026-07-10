"""format_cli_error — the human message (plus auth hint) for a fatal CLI error."""

from ycli.cli.errors import format_cli_error
from ycli.yandex.errors import YandexAuthError, YandexNotFoundError


def test_auth_error_appends_login_hint():
    message = format_cli_error(YandexAuthError("401 Unauthorized", status=401))
    assert message.startswith("Error: 401 Unauthorized")
    assert "ycli auth login" in message
    assert "YANDEX_ID_OAUTH_TOKEN" in message


def test_non_auth_error_has_no_hint():
    message = format_cli_error(YandexNotFoundError("404 Not Found", status=404))
    assert message == "Error: 404 Not Found"
    assert "auth login" not in message
