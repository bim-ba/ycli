"""Wiki FastMCP subserver tests — @cache factory, env+responses pattern."""
import pytest
import responses
from fastmcp import Client

from ycli.yandex.wiki import mcp as wiki_mcp

BASE = "https://api.wiki.yandex.net/v1"


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
async def test_pages_get_tool_returns_body(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages",
        json={"id": 1, "slug": "it", "title": "It", "content": "# Hi"},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("pages_get", {"slug": "it"})
    assert result.data == "# Hi"


@responses.activate
async def test_comments_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments",
        json={"results": [{"content": "hi"}]},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("comments_list", {"page_id": 42})
    assert result.data.results[0].content == "hi"


@responses.activate
async def test_pages_meta_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages",
        json={"id": 1, "slug": "it", "title": "It", "attributes": {"comments_count": 3}},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("pages_meta", {"slug": "it"})
    assert result.data.slug == "it"
    assert result.data.attributes.comments_count == 3


@responses.activate
async def test_pages_descendants_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 2, "slug": "it/child"}], "next_cursor": None},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("pages_descendants", {"slug": "it"})
    assert result.data[0].slug == "it/child"
    assert responses.calls[-1].request.params["slug"] == "it"


@responses.activate
async def test_attachments_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "d.png"}]},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("attachments_list", {"page_id": 42})
    assert result.data.results[0].name == "d.png"


async def test_tools_registered_and_read_only():
    async with Client(wiki_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {
        "pages_get",
        "pages_meta",
        "pages_descendants",
        "comments_list",
        "attachments_list",
    } <= set(tools)
    assert tools["pages_get"].annotations.readOnlyHint is True
