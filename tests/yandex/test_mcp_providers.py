"""MCP client providers resolve credentials on every call — nothing is cached per process."""

from fastmcp import Client
from pydantic import SecretStr

from tests.hosts import TRACKER_BASE
from ycli.settings import Credentials
from ycli.yandex.core.session import SyncSession
from ycli.yandex.mcp import EnvAuthSource, app_config, client_provider
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.tracker.issues import mcp as issues_mcp


def test_a_rotated_token_applies_to_the_next_call(api, monkeypatch):
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice"})
    provide = client_provider(TrackerClient)
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "first")
    with provide() as first:
        first.me.get()
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "second")
    with provide() as second:
        second.me.get()
    assert [call.headers["Authorization"] for call in api.calls] == ["OAuth first", "OAuth second"]


def test_an_explicit_auth_source_wins_over_the_environment(api):
    class FixedSource:
        def resolve(self) -> Credentials:
            return Credentials(oauth_token=SecretStr("fixed"), organization_id="org-1")

    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice"})
    with client_provider(TrackerClient, FixedSource())() as client:
        client.me.get()
    assert api.calls[0].headers["Authorization"] == "OAuth fixed"
    assert api.calls[0].headers["X-Org-Id"] == "org-1"


def test_tracker_deps_factory_builds_from_env(api, monkeypatch):
    """dependencies.tracker_client() reads env and returns a working TrackerClient."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    from ycli.yandex.tracker.dependencies import tracker_client

    api.add("GET", f"{TRACKER_BASE}/priorities", json=[])
    with tracker_client() as client:
        assert isinstance(client, TrackerClient)
        assert client.priorities.list().root == []
    assert api.calls[0].headers["Authorization"] == "OAuth tok"


def test_env_auth_source_and_config_read_the_environment(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org-env")
    monkeypatch.setenv("YCLI__HTTP__RETRIES", "1")
    assert EnvAuthSource().resolve().organization_id == "org-env"
    assert app_config().http.retries == 1


async def test_a_tool_call_closes_the_client_it_built(api, monkeypatch):
    """The per-call client is torn down after the tool returns, so no socket outlives a call."""
    built: list[TrackerClient] = []
    wire = TrackerClient._wire

    def record(client: TrackerClient, session: SyncSession) -> None:
        built.append(client)
        wire(client, session)

    monkeypatch.setattr(TrackerClient, "_wire", record)
    api.add("GET", f"{TRACKER_BASE}/issues/DE-1", json={"key": "DE-1"})
    async with Client(issues_mcp.mcp) as client:
        result = await client.call_tool("issues_get", {"key": "DE-1"})
    assert result.data.key == "DE-1"
    [tracker] = built
    assert tracker.issues._session._client.is_closed
