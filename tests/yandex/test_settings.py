"""Settings models — env-driven config with required credentials."""
import pytest
from pydantic import ValidationError

from ycli.yandex.settings import AppConfig, Credentials


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


def test_credentials_missing_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    monkeypatch.chdir(tmp_path)  # ensure no .env file is picked up
    with pytest.raises(ValidationError):
        Credentials()


def test_settings_read_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("YCLI_LOG_LEVEL", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("YCLI_LOG_LEVEL=WARNING\n")
    assert AppConfig().log_level == "WARNING"


def test_cli_callback_uses_configured_log_level(monkeypatch):
    import ycli.cli as cli
    captured = {}
    monkeypatch.setenv("YCLI_LOG_LEVEL", "ERROR")
    monkeypatch.setattr("ycli.cli.configure", lambda level: captured.setdefault("level", level))
    from typer.testing import CliRunner
    # Root --help doesn't trigger the callback in Typer; use a subcommand invocation instead.
    CliRunner().invoke(cli.app, ["tracker", "issues", "--help"])
    assert captured["level"] == "ERROR"
