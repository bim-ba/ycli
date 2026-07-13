"""Wiki /recovery_tokens FastMCP subserver tests — the ``recovery_restore`` write tool."""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.wiki.recovery import mcp as recovery_mcp

BASE = "https://api.wiki.yandex.net/v1"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_recovery_restore_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/recovery_tokens/tok-1/recover",
        json={"id": 42, "slug": "data/x"},
        status=200,
    )
    async with Client(recovery_mcp.mcp) as client:
        result = await client.call_tool("recovery_restore", {"token": "tok-1"})
    assert result.data.id == 42
    assert result.data.slug == "data/x"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert request.url.endswith("/recovery_tokens/tok-1/recover")  # ty: ignore[unresolved-attribute]
    assert not request.body  # the token in the path is the whole request


async def test_recovery_restore_carries_honest_write_hints():
    async with Client(recovery_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    annotations = tools["recovery_restore"].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is False  # restore re-creates data, never removes it
    assert annotations.idempotentHint is False
    assert annotations.title
