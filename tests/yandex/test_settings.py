"""Settings models — env-driven config with required credentials."""

import pytest
from pydantic import ValidationError

from ycli.settings import AppConfig, Credentials, OAuthAppConfig


def test_app_config_defaults(monkeypatch):
    for var in ("YCLI_TIMEOUT_SECONDS", "YCLI_RETRIES", "YCLI_LOG_LEVEL"):
        monkeypatch.delenv(var, raising=False)
    config = AppConfig()
    assert config.timeout_seconds == 30.0
    assert config.retries == 3
    assert config.log_level == "INFO"


def test_app_config_reads_overrides(monkeypatch):
    monkeypatch.setenv("YCLI_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("YCLI_RETRIES", "7")
    monkeypatch.setenv("YCLI_LOG_LEVEL", "DEBUG")
    config = AppConfig()
    assert config.timeout_seconds == 12.5
    assert config.retries == 7
    assert config.log_level == "DEBUG"


def test_credentials_read_env(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    creds = Credentials()
    assert creds.oauth_token == "tok"
    assert creds.organization_id == "org"
    assert creds.iam_token is None
    assert creds.service_account is None


def test_credentials_missing_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.chdir(tmp_path)  # ensure no .env file is picked up
    with pytest.raises(ValidationError):
        Credentials()


def test_credentials_read_static_iam(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "iam")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud")
    credentials = Credentials()
    assert credentials.iam_token == "iam"
    assert credentials.cloud_organization_id == "cloud"
    assert credentials.uses_service_account_iam is False


def test_credentials_build_service_account(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud")
    monkeypatch.setenv("YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_ID", "key")
    monkeypatch.setenv("YANDEX_CLOUD_SERVICE_ACCOUNT_ID", "account")
    monkeypatch.setenv("YANDEX_CLOUD_SERVICE_ACCOUNT_PRIVATE_KEY", "private")
    service_account = Credentials().service_account
    assert service_account is not None
    assert service_account.to_yandexcloud_dict() == {
        "id": "key",
        "service_account_id": "account",
        "private_key": "private",
    }
    assert Credentials().uses_service_account_iam is True


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_ID": "key"}, "must be set together"),
        (
            {
                "YANDEX_ID_OAUTH_TOKEN": "oauth",
                "YANDEX_ID_ORGANIZATION_ID": "",
                "YANDEX_CLOUD_ORGANIZATION_ID": "",
            },
            "exactly one",
        ),
        ({"YANDEX_CLOUD_ORGANIZATION_ID": "cloud"}, "set YANDEX_ID_OAUTH_TOKEN"),
    ],
)
def test_credentials_reject_invalid_combinations(monkeypatch, tmp_path, updates, message):
    monkeypatch.chdir(tmp_path)
    for name in (
        "YANDEX_ID_OAUTH_TOKEN",
        "YANDEX_ID_ORGANIZATION_ID",
        "YANDEX_CLOUD_IAM_TOKEN",
        "YANDEX_CLOUD_ORGANIZATION_ID",
        "YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_ID",
        "YANDEX_CLOUD_SERVICE_ACCOUNT_ID",
        "YANDEX_CLOUD_SERVICE_ACCOUNT_PRIVATE_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    for name, value in updates.items():
        monkeypatch.setenv(name, value)
    with pytest.raises(ValidationError, match=message):
        Credentials()


def test_credentials_reject_two_organization_ids(monkeypatch):
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud")
    with pytest.raises(ValidationError, match="exactly one"):
        Credentials()


def test_iam_requires_cloud_organization(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "iam")
    with pytest.raises(ValidationError, match="requires YANDEX_CLOUD_ORGANIZATION_ID"):
        Credentials()


def test_empty_optional_values_are_absent(monkeypatch):
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "   ")
    credentials = Credentials()
    assert credentials.iam_token is None


@pytest.mark.parametrize("token_name", ["YANDEX_ID_OAUTH_TOKEN", "YANDEX_CLOUD_IAM_TOKEN"])
def test_higher_priority_token_ignores_partial_service_account(monkeypatch, token_name):
    if token_name == "YANDEX_CLOUD_IAM_TOKEN":
        monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
        monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
        monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud")
    monkeypatch.setenv(token_name, "token")
    monkeypatch.setenv("YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_ID", "stale-key")

    credentials = Credentials()

    assert credentials.service_account is None
    assert credentials.uses_service_account_iam is False


def test_settings_read_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("YCLI_LOG_LEVEL", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("YCLI_LOG_LEVEL=WARNING\n")
    assert AppConfig().log_level == "WARNING"


def test_cli_callback_uses_configured_log_level(monkeypatch):
    import ycli.cli.app as cli

    captured = {}
    monkeypatch.setenv("YCLI_LOG_LEVEL", "ERROR")
    monkeypatch.setattr("ycli.cli.app.configure", lambda level: captured.setdefault("level", level))
    from typer.testing import CliRunner

    # Root --help doesn't trigger the callback in Typer; use a subcommand invocation instead.
    CliRunner().invoke(cli.app, ["tracker", "issues", "--help"])
    assert captured["level"] == "ERROR"


def test_oauth_app_config_defaults(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # ignore any repo-root .env
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
    assert config.client_secret == "app-secret"


def test_max_items_default_and_env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # ignore any repo-root .env
    monkeypatch.delenv("YCLI_MAX_ITEMS", raising=False)
    from ycli.settings import AppConfig

    assert AppConfig().max_items == 500
    monkeypatch.setenv("YCLI_MAX_ITEMS", "42")
    assert AppConfig().max_items == 42
