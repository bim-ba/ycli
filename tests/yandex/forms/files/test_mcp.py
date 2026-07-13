"""TDD for forms files MCP subserver — files_verify read + files_delete write.

upload / download move raw bytes (binary payloads), so they intentionally register no tools.
"""

import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import FORMS_BASE as BASE
from ycli.yandex.forms.files import mcp as files_mcp

pytestmark = pytest.mark.integration

SID = "6818ceffe010db4f59d11329"


@responses.activate
async def test_files_verify_tool_posts_references(creds):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/files/verify",
        json=[{"name": "cv.pdf", "path": "a/b/cv.pdf", "check_status": "ready"}],
        status=200,
    )
    async with Client(files_mcp.mcp) as client:
        result = await client.call_tool(
            "files_verify", {"survey_id": SID, "files": [{"path": "a/b/cv.pdf"}]}
        )
    request = responses.calls[0].request
    assert request.method == "POST" and request.url == f"{BASE}/surveys/{SID}/files/verify"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == [{"path": "a/b/cv.pdf"}]
    assert [f.check_status for f in result.data] == ["ready"]


@responses.activate
async def test_files_delete_tool_sends_body(creds):
    responses.add(responses.DELETE, f"{BASE}/files", status=200)
    async with Client(files_mcp.mcp) as client:
        result = await client.call_tool("files_delete", {"path": "a/b/cv.pdf"})
    request = responses.calls[0].request
    assert request.method == "DELETE" and request.url == f"{BASE}/files"
    body = request.body
    assert isinstance(body, bytes)
    assert json.loads(body) == {"path": "a/b/cv.pdf"}
    assert result.data.ok is True and result.data.detail == "deleted file path=a/b/cv.pdf"


async def test_files_tools_registered_with_honest_annotations():
    async with Client(files_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    # upload/download are binary payloads and intentionally have no MCP tools.
    assert set(tools) == {"files_verify", "files_delete"}
    assert tools["files_verify"].annotations.readOnlyHint is True
    delete = tools["files_delete"].annotations
    assert delete.readOnlyHint is False
    assert delete.destructiveHint is True and delete.idempotentHint is False
    assert all(t.annotations.title for t in tools.values())
