"""format_cli_error — the human message (plus next-step hints) for a fatal CLI error."""

import pytest
from pydantic import BaseModel, ValidationError

from ycli.cli.app import main
from ycli.cli.errors import exit_code_for, format_cli_error
from ycli.cli.exit_codes import ExitCode
from ycli.settings import Credentials
from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexConnectionError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
    YandexTimeoutError,
)


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


def test_non_auth_error_has_no_login_hint():
    message = format_cli_error(YandexServerError("503 Unavailable", status=503))
    assert message == "Error: 503 Unavailable"
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


def test_not_found_hint_says_to_check_the_id_and_visibility():
    message = format_cli_error(YandexNotFoundError("404 Not Found", status=404))
    assert message.startswith("Error: 404 Not Found")
    assert "check the id or key" in message


@pytest.mark.parametrize(
    ("retry_after", "wording"),
    [(30.0, "wait 30 s (Retry-After)"), (1.5, "wait 1.5 s"), (None, "wait a little")],
)
def test_rate_limit_hint_names_retry_after_when_the_server_sent_it(retry_after, wording):
    message = format_cli_error(YandexRateLimitError("429", status=429, retry_after=retry_after))
    assert wording in message


def _invalid_app_config(monkeypatch) -> ValidationError:
    from ycli.settings import AppConfig

    monkeypatch.setenv("YCLI__HTTP__RETRIES", "-1")
    with pytest.raises(ValidationError) as caught:
        AppConfig()
    return caught.value


def test_a_missing_credential_exits_as_an_auth_failure(monkeypatch, tmp_path):
    assert exit_code_for(_missing_credentials_error(monkeypatch, tmp_path)) == ExitCode.AUTH


def test_an_invalid_configuration_exits_as_a_usage_error(monkeypatch):
    assert exit_code_for(_invalid_app_config(monkeypatch)) == ExitCode.USAGE


@pytest.mark.parametrize(
    ("error", "code"),
    [
        (YandexAuthError("401", status=401), ExitCode.AUTH),
        (YandexAuthError("403", status=403), ExitCode.AUTH),
        (YandexNotFoundError("404", status=404), ExitCode.NOT_FOUND),
        (YandexRateLimitError("429", status=429), ExitCode.RATE_LIMITED),
        (YandexServerError("503", status=503), ExitCode.TRANSIENT),
        (YandexTimeoutError("polled too long"), ExitCode.TRANSIENT),
        (YandexConnectionError("no route"), ExitCode.TRANSIENT),
        (YandexClientError("400", status=400), ExitCode.FAILURE),
        (RuntimeError("anything unmapped"), ExitCode.FAILURE),
    ],
)
def test_every_error_kind_has_its_exit_code(error, code):
    assert exit_code_for(error) == code


def test_a_non_credential_validation_error_is_a_plain_failure():
    class _Model(BaseModel):
        count: int

    with pytest.raises(ValidationError) as exc_info:
        _Model(count="not-an-int")  # ty: ignore[invalid-argument-type]
    assert exit_code_for(exc_info.value) == ExitCode.FAILURE


@pytest.mark.parametrize(
    ("error", "code"),
    [(YandexNotFoundError("gone", status=404), 3), (YandexServerError("down", status=502), 6)],
)
def test_main_exits_with_the_code_of_the_failure(monkeypatch, capsys, error, code):
    def failing_app() -> None:
        raise error

    monkeypatch.setattr("ycli.cli.app.app", failing_app)
    with pytest.raises(SystemExit) as exited:
        main()
    assert exited.value.code == code
    assert "Error:" in capsys.readouterr().err


def test_the_root_help_lists_the_exit_codes():
    from typer.testing import CliRunner

    from ycli.cli.app import app

    help_text = " ".join(CliRunner().invoke(app, ["--help"]).stdout.split())
    assert "Exit codes: 0 ok" in help_text
    assert "6 transient" in help_text
