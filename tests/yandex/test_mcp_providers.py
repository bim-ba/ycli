"""MCP client providers resolve credentials on every call — nothing is cached per process."""

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, ValidationError

from tests.hosts import TRACKER_BASE
from ycli.settings import Credentials
from ycli.yandex.core.session import SyncSession
from ycli.yandex.mcp import app_config, caller_credentials, client_provider
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


def test_stdio_credentials_and_config_read_the_environment(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org-env")
    monkeypatch.setenv("YCLI__HTTP__RETRIES", "1")
    assert caller_credentials().organization_id == "org-env"
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


@pytest.mark.parametrize(
    ("unset", "named"),
    [
        (
            ("YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"),
            "YANDEX_ID_OAUTH_TOKEN, YANDEX_ID_ORGANIZATION_ID are not set",
        ),
        (("YANDEX_ID_ORGANIZATION_ID",), "YANDEX_ID_ORGANIZATION_ID is not set"),
    ],
)
async def test_a_tool_call_without_credentials_names_the_missing_variables(
    monkeypatch, tmp_path, unset, named
):
    """Not FastMCP's "Failed to resolve dependency 'client'", which names nothing."""
    monkeypatch.chdir(tmp_path)  # no repo .env
    for name in unset:
        monkeypatch.delenv(name, raising=False)
    async with Client(issues_mcp.mcp) as client:
        with pytest.raises(ToolError) as raised:
            await client.call_tool("issues_get", {"key": "DE-1"})
    assert named in str(raised.value)
    assert "ycli auth login" in str(raised.value)
    assert "resolve dependency" not in str(raised.value)


def test_a_validation_error_unrelated_to_credentials_is_not_reworded(monkeypatch):
    class Other(BaseModel):
        count: int

    with pytest.raises(ValidationError) as unrelated:
        Other(count="x")  # ty: ignore[invalid-argument-type]

    def broken() -> Credentials:
        raise unrelated.value

    monkeypatch.setattr("ycli.yandex.mcp.Credentials", broken)
    with pytest.raises(ValidationError):
        caller_credentials()
