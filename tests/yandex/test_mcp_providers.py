"""MCP client providers resolve credentials on every call — nothing is cached per process."""

from pydantic import SecretStr

from ycli.settings import Credentials
from ycli.yandex.mcp import EnvAuthSource, app_config, client_provider
from ycli.yandex.tracker.client import TrackerClient


def test_a_rotated_token_applies_to_the_next_call(monkeypatch):
    provide = client_provider(TrackerClient)
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "first")
    assert provide().me._session.headers["Authorization"] == "OAuth first"
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "second")
    assert provide().me._session.headers["Authorization"] == "OAuth second"


def test_an_explicit_auth_source_wins_over_the_environment():
    class FixedSource:
        def resolve(self) -> Credentials:
            return Credentials(oauth_token=SecretStr("fixed"), organization_id="org-1")

    client = client_provider(TrackerClient, FixedSource())()
    assert client.me._session.headers["Authorization"] == "OAuth fixed"
    assert client.me._session.headers["X-Org-Id"] == "org-1"


def test_env_auth_source_and_config_read_the_environment(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org-env")
    monkeypatch.setenv("YCLI__HTTP__RETRIES", "1")
    assert EnvAuthSource().resolve().organization_id == "org-env"
    assert app_config().http.retries == 1
