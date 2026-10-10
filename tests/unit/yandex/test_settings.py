"""Settings models — grouped env config parsed into refined types, required credentials."""

import pytest
from pydantic import BaseModel, SecretStr, ValidationError

from ycli.settings import (
    AppConfig,
    Credentials,
    HTTPConfig,
    MCPHTTPConfig,
    OAuthAppConfig,
    _EnvSettings,
    missing_credentials,
)


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch):
    """No repo-root .env and no inherited YCLI__* variables leak into these tests."""
    for name in (
        "YCLI__HTTP__TIMEOUT_SECONDS",
        "YCLI__HTTP__RETRIES",
        "YCLI__HTTP__MAX_ITEMS",
        "YCLI__HTTP__MAX_TOOL_ITEMS",
        "YCLI__LOGGING__LEVEL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_app_config_defaults():
    config = AppConfig()
    assert config.http.timeout_seconds == 30.0
    assert config.http.retries == 3
    assert config.http.max_items == 500
    assert config.http.max_tool_items == 50
    assert config.logging.level == "WARNING"
    assert config.logging.format == "text"


def test_app_config_reads_grouped_env(monkeypatch):
    monkeypatch.setenv("YCLI__HTTP__TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("YCLI__HTTP__RETRIES", "7")
    monkeypatch.setenv("YCLI__HTTP__MAX_ITEMS", "42")
    monkeypatch.setenv("YCLI__LOGGING__LEVEL", "debug")
    config = AppConfig()
    assert config.http.timeout_seconds == 12.5
    assert config.http.retries == 7
    assert config.http.max_items == 42
    assert config.logging.level == "DEBUG"


def test_an_empty_setting_reads_as_unset(monkeypatch):
    monkeypatch.setenv("YCLI__HTTP__RETRIES", "")
    assert AppConfig().http.retries == 3


def test_app_config_keyword_arguments_win():
    """The #90 bug: ``AppConfig(timeout_seconds=5)`` used to be silently ignored."""
    config = AppConfig(http={"timeout_seconds": 5, "retries": 0})  # ty: ignore[invalid-argument-type]
    assert config.http.timeout_seconds == 5.0
    assert config.http.retries == 0


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("YCLI__HTTP__TIMEOUT_SECONDS", "0"),
        ("YCLI__HTTP__TIMEOUT_SECONDS", "abc"),
        ("YCLI__HTTP__RETRIES", "-1"),
        ("YCLI__HTTP__MAX_ITEMS", "0"),
        ("YCLI__HTTP__MAX_TOOL_ITEMS", "0"),
        ("YCLI__LOGGING__LEVEL", "bogus"),
    ],
)
def test_app_config_rejects_bad_values(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError):
        AppConfig()


def test_app_config_reads_dotenv(tmp_path):
    (tmp_path / ".env").write_text("YCLI__LOGGING__LEVEL=WARNING\n")
    assert AppConfig().logging.level == "WARNING"


def test_credentials_read_env_and_hide_the_token(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "y0_secret-value")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    credentials = Credentials()
    assert credentials.token.get_secret_value() == "y0_secret-value"
    assert credentials.organization_id == "org"
    assert "secret-value" not in repr(credentials)


def test_credentials_accept_the_ycli_fallback_names(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID")
    monkeypatch.setenv("YCLI__AUTH__OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YCLI__AUTH__ORGANIZATION_ID", "org")
    credentials = Credentials()
    assert credentials.token.get_secret_value() == "tok"
    assert credentials.organization_id == "org"


def test_credentials_keyword_arguments():
    credentials = Credentials(oauth_token=SecretStr("tok"), organization_id="org")
    assert credentials.token.get_secret_value() == "tok"


@pytest.mark.parametrize("token", [None, ""])
def test_credentials_missing_or_empty_token_reads_as_missing(monkeypatch, token):
    """An exported-but-empty variable is reported like an unset one (same login hint)."""
    if token is None:
        monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    else:
        monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", token)
    with pytest.raises(ValidationError) as caught:
        Credentials()
    assert missing_credentials(caught.value) == ["YANDEX_ID_OAUTH_TOKEN"]


def test_an_iam_token_stands_in_for_the_oauth_token(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t1.secret")
    credentials = Credentials()
    assert (credentials.kind, credentials.token.get_secret_value()) == ("iam", "t1.secret")
    assert "t1.secret" not in repr(credentials)


def test_the_oauth_token_is_the_default_kind():
    credentials = Credentials()
    assert credentials.kind == "oauth"


def test_two_tokens_at_once_are_refused_and_named(monkeypatch):
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t1.secret")
    with pytest.raises(ValidationError) as caught:
        Credentials()
    (error,) = caught.value.errors()
    assert error["msg"] == (
        "YANDEX_ID_OAUTH_TOKEN and YANDEX_CLOUD_IAM_TOKEN are both set: keep one of them"
    )
    assert missing_credentials(caught.value) == []  # set, not missing: a configuration error


def test_an_error_about_the_credentials_never_quotes_a_value(monkeypatch):
    """The text of the error is what pytest, a log or an SDK caller's traceback shows."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "oauth-value")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "iam-value")
    with pytest.raises(ValidationError) as caught:
        Credentials()
    assert "both set" in str(caught.value)
    assert "oauth-value" not in str(caught.value)
    assert "iam-value" not in str(caught.value)
    assert "oauth-value" not in repr(caught.value)


def test_every_settings_model_hides_its_input_in_errors():
    """A subclass with a configuration of its own still inherits the switch."""
    models = _EnvSettings.__subclasses__()
    assert {OAuthAppConfig, MCPHTTPConfig, Credentials} <= set(models)
    assert all(model.model_config.get("hide_input_in_errors") for model in models)


def test_no_token_and_no_organization_are_both_reported(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID")
    with pytest.raises(ValidationError) as caught:
        Credentials()
    assert sorted(missing_credentials(caught.value)) == [
        "YANDEX_ID_OAUTH_TOKEN",
        "YANDEX_ID_ORGANIZATION_ID",
    ]


def test_credentials_reject_an_empty_keyword_token():
    with pytest.raises(ValidationError):
        Credentials(oauth_token=SecretStr(""), organization_id="org")


def test_oauth_app_config_defaults(monkeypatch):
    monkeypatch.delenv("YANDEX_OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("YANDEX_OAUTH_CLIENT_SECRET", raising=False)
    config = OAuthAppConfig()
    assert config.client_id is None
    assert config.client_secret is None


def test_oauth_app_config_reads_env(monkeypatch):
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_ID", "app-id")
    monkeypatch.setenv("YANDEX_OAUTH_CLIENT_SECRET", "app-secret")
    config = OAuthAppConfig()
    assert config.client_id == "app-id"
    assert config.client_secret is not None
    assert config.client_secret.get_secret_value() == "app-secret"


def test_oauth_app_config_keyword_arguments(monkeypatch):
    monkeypatch.delenv("YANDEX_OAUTH_CLIENT_ID", raising=False)
    assert OAuthAppConfig(client_id="app-id").client_id == "app-id"


def test_cli_callback_uses_configured_log_level(monkeypatch):
    import ycli.cli.app as cli

    captured = {}
    monkeypatch.setenv("YCLI__LOGGING__LEVEL", "ERROR")
    monkeypatch.setattr(
        "ycli.log.configure", lambda level, log_format: captured.setdefault("level", level)
    )
    from typer.testing import CliRunner

    # Root --help doesn't trigger the callback in Typer; use a subcommand invocation instead.
    CliRunner().invoke(cli.app, ["tracker", "issues", "--help"])
    assert captured["level"] == "ERROR"


@pytest.mark.parametrize(
    ("limit", "all_", "cap"),
    [(None, False, 500), (10, False, 10), (10, True, None), (None, True, None)],
)
def test_the_listing_cap_takes_the_limit_then_the_default_and_all_lifts_it(limit, all_, cap):
    assert HTTPConfig(max_items=500).cap(limit, all_=all_) == cap


def test_missing_credentials_names_each_unset_variable(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    with pytest.raises(ValidationError) as unset:
        Credentials()
    assert missing_credentials(unset.value) == [
        "YANDEX_ID_OAUTH_TOKEN",
        "YANDEX_ID_ORGANIZATION_ID",
    ]
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    with pytest.raises(ValidationError) as half:
        Credentials()
    assert missing_credentials(half.value) == ["YANDEX_ID_ORGANIZATION_ID"]


def test_missing_credentials_ignores_everything_else():
    class Other(BaseModel):
        name: str

    with pytest.raises(ValidationError) as other:
        Other()  # ty: ignore[missing-argument]
    assert missing_credentials(other.value) == []  # a missing field, but not a credential
    assert missing_credentials(ValueError("boom")) == []
