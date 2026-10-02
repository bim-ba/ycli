"""MCP client providers resolve credentials on every call — nothing is cached per process."""

import requests
from fastmcp import Client
from pydantic import SecretStr

from tests.hosts import TRACKER_BASE
from ycli.settings import Credentials
from ycli.yandex.mcp import EnvAuthSource, app_config, client_provider
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues import mcp as issues_mcp


def test_a_rotated_token_applies_to_the_next_call(monkeypatch):
    provide = client_provider(TrackerClient)
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "first")
    with provide() as first:
        assert first.me._session.headers["Authorization"] == "OAuth first"
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "second")
    with provide() as second:
        assert second.me._session.headers["Authorization"] == "OAuth second"


def test_an_explicit_auth_source_wins_over_the_environment():
    class FixedSource:
        def resolve(self) -> Credentials:
            return Credentials(oauth_token=SecretStr("fixed"), organization_id="org-1")

    with client_provider(TrackerClient, FixedSource())() as client:
        assert client.me._session.headers["Authorization"] == "OAuth fixed"
        assert client.me._session.headers["X-Org-Id"] == "org-1"


def test_env_auth_source_and_config_read_the_environment(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org-env")
    monkeypatch.setenv("YCLI__HTTP__RETRIES", "1")
    assert EnvAuthSource().resolve().organization_id == "org-env"
    assert app_config().http.retries == 1


async def test_a_tool_call_closes_the_client_it_built(api, monkeypatch):
    """The per-call client is torn down after the tool returns, so no socket outlives a call."""
    built: list[TrackerClient] = []
    wire = TrackerClient._wire

    def record(client: TrackerClient, transport: requests.Session) -> None:
        built.append(client)
        wire(client, transport)

    monkeypatch.setattr(TrackerClient, "_wire", record)
    api.add("GET", f"{TRACKER_BASE}/issues/DE-1", json={"key": "DE-1"})
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_get", {"key": "DE-1"})
    assert result.data.key == "DE-1"
    [tracker] = built
    assert tracker.issues._session._client.is_closed
