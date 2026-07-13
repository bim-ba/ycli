"""TDD for the tracker dashboards MCP subserver — write tools with honest annotations."""

import json

import pytest
import responses
from fastmcp import Client

from ycli.yandex.tracker.dashboards import mcp as dashboards_mcp

BASE = "https://api.tracker.yandex.net/v3"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_dashboards_create_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/dashboards/", json={"id": 42, "name": "My dash"}, status=201
    )
    async with Client(dashboards_mcp.mcp) as client:
        result = await client.call_tool("dashboards_create", {"body": {"name": "My dash"}})
    assert result.data.name == "My dash"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/dashboards/"
    assert json.loads(responses.calls[0].request.body) == {"name": "My dash"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_dashboards_add_cycle_time_widget_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/dashboards/42/widgets/cycleTime",
        json={"id": 7, "version": 1},
        status=201,
    )
    async with Client(dashboards_mcp.mcp) as client:
        result = await client.call_tool(
            "dashboards_add_cycle_time_widget",
            {"dashboard_id": "42", "body": {"name": "Cycle time", "queue": "DE"}},
        )
    assert result.data.id == 7
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/dashboards/42/widgets/cycleTime"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "name": "Cycle time",
        "queue": "DE",
    }


async def test_dashboard_tools_annotations():
    async with Client(dashboards_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {"dashboards_create", "dashboards_add_cycle_time_widget"}
    for name, tool in tools.items():
        ann = tool.annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is False, name
        assert ann.idempotentHint is False, name
        assert ann.title, name
