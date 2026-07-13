"""TDD for the tracker import MCP subserver — admin-only write tools (import_*)."""

import json

import responses
from fastmcp import Client

from tests.hosts import TRACKER_BASE as BASE
from ycli.yandex.tracker.import_ import mcp as import_mcp


@responses.activate
async def test_import_task_tool(creds):
    responses.add(responses.POST, f"{BASE}/issues/_import", json={"key": "JUNE-2"}, status=201)
    body = {
        "queue": "JUNE",
        "summary": "old task",
        "createdAt": "2020-01-01T00:00:00.000+0000",
        "createdBy": "11",
    }
    async with Client(import_mcp.mcp) as client:
        result = await client.call_tool("import_task", {"body": body})
    assert result.data.key == "JUNE-2"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/_import"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_import_comment_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/comments/_import",
        json={"id": 3, "text": "old comment"},
        status=201,
    )
    body = {"text": "old comment", "createdAt": "2020-01-01T00:00:00.000+0000", "createdBy": "11"}
    async with Client(import_mcp.mcp) as client:
        result = await client.call_tool("import_comment", {"issue_key": "JUNE-2", "body": body})
    assert result.data.text == "old comment"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/JUNE-2/comments/_import"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_import_link_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/links/_import",
        json={"id": 4, "object": {"key": "JUNE-3"}},
        status=201,
    )
    body = {
        "relationship": "relates",
        "issue": "JUNE-3",
        "createdAt": "2020-01-01T00:00:00.000+0000",
        "createdBy": "11",
    }
    async with Client(import_mcp.mcp) as client:
        result = await client.call_tool("import_link", {"issue_key": "JUNE-2", "body": body})
    assert result.data.object.key == "JUNE-3"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/JUNE-2/links/_import"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_import_worklog_tool_parses_array_response(creds):
    # The live endpoint answers with a JSON ARRAY of created records (regression).
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/worklogs/_import",
        json=[{"id": 5, "duration": "PT1H"}],
        status=201,
    )
    body = {
        "start": "2020-01-01T10:00:00.000+0000",
        "duration": "PT1H",
        "createdAt": "2020-01-01T00:00:00.000+0000",
        "createdBy": "11",
    }
    async with Client(import_mcp.mcp) as client:
        result = await client.call_tool("import_worklog", {"issue_key": "JUNE-2", "body": body})
    assert [w.duration for w in result.data] == ["PT1H"]
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/issues/JUNE-2/worklogs/_import"
    assert json.loads(responses.calls[0].request.body) == body  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_import_file_tool_sends_multipart_and_query(creds):
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/attachments/_import",
        json={"id": "6", "name": "log.txt"},
        status=201,
    )
    async with Client(import_mcp.mcp) as client:
        result = await client.call_tool(
            "import_file",
            {
                "issue_key": "JUNE-2",
                "filename": "log.txt",
                "created_at": "2020-01-01T00:00:00.000+0000",
                "created_by": "11",
                "data": "hello import",
            },
        )
    assert result.data.name == "log.txt"
    request = responses.calls[0].request
    request_url = request.url or ""
    assert request.method == "POST"
    assert request_url.startswith(f"{BASE}/issues/JUNE-2/attachments/_import?")
    assert "filename=log.txt" in request_url and "createdBy=11" in request_url
    assert isinstance(request.body, bytes) and b"hello import" in request.body


async def test_import_tools_annotations():
    async with Client(import_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert set(tools) == {
        "import_task",
        "import_comment",
        "import_link",
        "import_worklog",
        "import_file",
    }
    for name, tool in tools.items():
        ann = tool.annotations
        assert ann.readOnlyHint is False, name
        assert ann.destructiveHint is False, name
        assert ann.idempotentHint is False, name
        assert ann.title, name
