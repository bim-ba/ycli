"""Wiki FastMCP subserver tests — Depends DI, native errors, in-memory client."""
import requests
import responses
from fastmcp import Client

from ycli.yandex.wiki import mcp as wiki_mcp
from ycli.yandex.wiki.client import WikiClient

BASE = "https://api.wiki.yandex.net/v1"


def _stub() -> WikiClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return WikiClient(session=s)


@responses.activate
async def test_pages_get_tool_returns_body(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub()))
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
async def test_comments_list_tool(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub()))
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
async def test_pages_meta_tool(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub()))
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
async def test_pages_descendants_tool(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub()))
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 2, "slug": "it/child"}], "next_cursor": None},
        status=200,
    )
    async with Client(wiki_mcp.mcp) as client:
        result = await client.call_tool("pages_descendants", {"slug": "it"})
    assert result.data.results[0].slug == "it/child"
    assert result.data.next_cursor is None  # null round-trips (pagination contract)
    assert responses.calls[-1].request.params["slug"] == "it"  # slug threaded into the query


@responses.activate
async def test_attachments_list_tool(monkeypatch):
    monkeypatch.setattr(WikiClient, "from_env", classmethod(lambda cls: _stub()))
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
