"""TDD for the tracker checklists MCP subserver (read-only: only ``checklists_get``).

The registration/read-only check targets the resource subserver directly (no wiring needed).
The call test exercises ``client.checklists.get`` through the cached ``TrackerClient`` — that
attribute exists only AFTER the orchestrator wires ``ChecklistsClient`` into ``tracker/client.py``,
so it passes standalone only once wired (flagged for the integrator).
"""

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.checklists import mcp as checklists_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


async def test_checklists_get_registered_read_only():
    async with Client(checklists_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert "checklists_get" in tools
    assert tools["checklists_get"].annotations.readOnlyHint is True


@responses.activate
async def test_checklists_get_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/issues/DE-1/checklistItems",
        json=[{"id": "5f", "text": "step 1", "checked": False}],
        status=200,
    )
    async with Client(checklists_mcp.mcp) as client:
        result = await client.call_tool("checklists_get", {"key": "DE-1"})
    assert result.data[0].text == "step 1"
