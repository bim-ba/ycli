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
    assert result.data[0].content == "hi"


@responses.activate
async def test_comments_thread_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/comments/7/thread",
        json={"results": [{"content": "reply"}], "next_cursor": None},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("comments_thread_list", {"page_id": 42, "comment_id": 7})
    assert result.data[0].content == "reply"


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
    assert responses.calls[-1].request.params["slug"] == "it"  # ty: ignore[unresolved-attribute]


@responses.activate
async def test_pages_grids_list_tool(creds):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/grids",
        json={"results": [{"id": "g1", "title": "Roadmap"}], "next_cursor": None},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("pages_grids_list", {"page_id": 42})
    assert result.data[0].title == "Roadmap"


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
    assert result.data[0].name == "d.png"


async def test_tools_registered_and_read_only():
    async with Client(wiki_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert {
        "pages_get",
        "pages_meta",
        "pages_descendants",
        "pages_grids_list",
        "comments_list",
        "comments_thread_list",
        "attachments_list",
    } <= set(tools)
    for name in ("pages_grids_list", "comments_thread_list"):
        assert tools[name].annotations.readOnlyHint is True
    assert tools["pages_get"].annotations.readOnlyHint is True


async def test_attachments_expose_no_binary_download_tool():
    """Binary downloads are CLI/SDK only — no MCP tool ever emits attachment bytes."""
    async with Client(wiki_mcp.mcp) as client:
        names = {t.name for t in await client.list_tools()}
    assert not any("download" in name for name in names)
    # attachments contributes exactly its list surface — nothing binary.
    assert {n for n in names if n.startswith("attachments_")} == {"attachments_list"}
