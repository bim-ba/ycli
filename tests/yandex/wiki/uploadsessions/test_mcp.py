"""Wiki /upload_sessions FastMCP subserver tests (targets the resource subserver).

``test_uploadsessions_get_tool`` routes through ``client.uploadsessions.get`` — it only passes
once the integrator wires ``UploadSessionsClient`` into ``WikiClient``. The registration /
read-only checks call ``list_tools`` only and pass without wiring.
"""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.wiki.uploadsessions import mcp as uploadsessions_mcp

BASE = "https://api.wiki.yandex.net/v1"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_uploadsessions_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/upload_sessions/s-1",
        json={"session_id": "s-1", "status": "in_progress"},
        status=200,
    )
    async with Client(uploadsessions_mcp.mcp) as client:
        result = await client.call_tool("uploadsessions_get", {"session_id": "s-1"})
    assert result.data.session_id == "s-1"
    assert result.data.status == "in_progress"


async def test_uploadsessions_get_is_registered_and_read_only():
    async with Client(uploadsessions_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "uploadsessions_get" in tools
    assert tools["uploadsessions_get"].annotations.readOnlyHint is True
