"""format_cli_error — the human message (plus next-step hints) for a fatal CLI error."""

import pytest
from pydantic import BaseModel, ValidationError

from ycli.cli.errors import format_cli_error
from ycli.settings import Credentials
from ycli.yandex.errors import YandexAuthError, YandexNotFoundError


def test_auth_error_appends_login_hint():
    message = format_cli_error(YandexAuthError("401 Unauthorized", status=401))
    assert message.startswith("Error: 401 Unauthorized")
    assert "ycli auth login" in message
    assert "YANDEX_ID_OAUTH_TOKEN" in message


def test_permission_error_points_at_access_not_at_signing_in():
    message = format_cli_error(YandexAuthError("403 Forbidden", status=403))
    assert message.startswith("Error: 403 Forbidden")
    assert "lacks access" in message
    assert "auth login" not in message


def test_non_auth_error_has_no_hint():
    message = format_cli_error(YandexNotFoundError("404 Not Found", status=404))
    assert message == "Error: 404 Not Found"
    assert "auth login" not in message


def _missing_credentials_error(monkeypatch, tmp_path) -> ValidationError:
    """Build the real pydantic error raised when neither credential env var is set."""
    monkeypatch.chdir(tmp_path)  # no repo .env
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    with pytest.raises(ValidationError) as exc_info:
        Credentials()  # ty: ignore[missing-argument]
    return exc_info.value


def test_missing_both_credentials_routes_to_auth_login(monkeypatch, tmp_path):
    message = format_cli_error(_missing_credentials_error(monkeypatch, tmp_path))
    assert "ycli auth login" in message
    assert "YANDEX_ID_OAUTH_TOKEN" in message
    assert "YANDEX_ID_ORGANIZATION_ID" in message
    assert "are not set" in message  # plural form for two missing vars
    assert not message.startswith("Error:")  # a friendly banner, not a raw validation dump


def test_missing_single_credential_uses_singular_phrasing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "present")
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    with pytest.raises(ValidationError) as exc_info:
        Credentials()  # ty: ignore[missing-argument]
    message = format_cli_error(exc_info.value)
    assert "YANDEX_ID_ORGANIZATION_ID is not set" in message
    assert "YANDEX_ID_OAUTH_TOKEN" not in message  # the one that IS set is not named


def test_non_credential_validation_error_falls_through_to_generic():
    class _Model(BaseModel):
        count: int

    with pytest.raises(ValidationError) as exc_info:
        _Model(count="not-an-int")  # ty: ignore[invalid-argument-type]
    message = format_cli_error(exc_info.value)
    assert message.startswith("Error:")  # unrelated validation error → generic message
    assert "auth login" not in message


def test_invalid_app_config_names_the_environment_variable(monkeypatch):
    from ycli.settings import AppConfig

    monkeypatch.setenv("YCLI__LOGGING__LEVEL", "bogus")
    monkeypatch.setenv("YCLI__HTTP__RETRIES", "-1")
    with pytest.raises(ValidationError) as caught:
        AppConfig()
    message = format_cli_error(caught.value)
    assert message.startswith("Invalid configuration:")
    assert "YCLI__LOGGING__LEVEL: Input should be" in message
    assert "YCLI__HTTP__RETRIES: Input should be greater than or equal to 0" in message
