"""Wiki /grids MCP subserver tests — the ``grids_get`` read plus every grid write tool."""

import json

import pytest
import responses
from fastmcp import Client

from tests.hosts import WIKI_BASE as BASE
from ycli.yandex.wiki.grids import mcp as grids_mcp

GID = "g-uuid"


@responses.activate
async def test_grids_get_tool_returns_grid(creds):
    responses.add(
        responses.GET,
        f"{BASE}/grids/{GID}",
        json={"id": GID, "title": "Roadmap", "revision": "3"},
        status=200,
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool("grids_get", {"grid_id": GID})
    assert result.data.title == "Roadmap"
    assert result.data.revision == "3"


@responses.activate
async def test_grids_get_forwards_query_params(creds):
    responses.add(responses.GET, f"{BASE}/grids/{GID}", json={"id": GID}, status=200)
    async with Client(grids_mcp.mcp) as client:
        await client.call_tool("grids_get", {"grid_id": GID, "only_cols": "name"})
    assert responses.calls[0].request.params["only_cols"] == "name"  # ty: ignore[unresolved-attribute]


async def test_grids_get_is_read_only():
    async with Client(grids_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["grids_get"].annotations.readOnlyHint is True


@responses.activate
async def test_grids_create_tool(creds):
    responses.add(responses.POST, f"{BASE}/grids", json={"id": GID, "title": "Roadmap"}, status=200)
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_create", {"body": {"title": "Roadmap", "page": {"slug": "data/x"}}}
        )
    assert result.data.id == GID
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"title": "Roadmap", "page": {"slug": "data/x"}}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_grids_update_tool(creds):
    responses.add(responses.POST, f"{BASE}/grids/{GID}", json={"revision": "4"}, status=200)
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_update", {"grid_id": GID, "body": {"revision": "3", "title": "New"}}
        )
    assert result.data.revision == "4"
    request = responses.calls[0].request
    assert request.method == "POST"  # POST-not-PATCH quirk
    assert json.loads(request.body) == {"revision": "3", "title": "New"}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_grids_delete_tool_synthesizes_ack(creds):
    responses.add(responses.DELETE, f"{BASE}/grids/{GID}", status=204)
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool("grids_delete", {"grid_id": GID})
    assert result.data.ok is True
    assert result.data.detail == f"deleted grid {GID}"
    request = responses.calls[0].request
    assert request.method == "DELETE"
    assert request.url.endswith(f"/grids/{GID}")  # ty: ignore[unresolved-attribute]


@responses.activate
async def test_grids_add_rows_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/rows",
        json={"revision": "4", "results": [{"id": "r1"}]},
        status=200,
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_add_rows", {"grid_id": GID, "body": {"revision": "3", "rows": [{"name": "x"}]}}
        )
    assert result.data.revision == "4"
    assert result.data.results[0].id == "r1"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"revision": "3", "rows": [{"name": "x"}]}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_grids_remove_rows_tool_sends_delete_with_body(creds):
    responses.add(responses.DELETE, f"{BASE}/grids/{GID}/rows", json={"revision": "4"}, status=200)
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_remove_rows", {"grid_id": GID, "body": {"revision": "3", "row_ids": ["r1"]}}
        )
    assert result.data.revision == "4"
    request = responses.calls[0].request
    assert request.method == "DELETE"
    assert json.loads(request.body) == {"revision": "3", "row_ids": ["r1"]}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_grids_move_rows_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/grids/{GID}/rows/move", json={"revision": "4"}, status=200
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_move_rows",
            {"grid_id": GID, "body": {"revision": "3", "row_id": "r1", "position": 0}},
        )
    assert result.data.revision == "4"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"revision": "3", "row_id": "r1", "position": 0}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_grids_add_columns_tool(creds):
    responses.add(responses.POST, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200)
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_add_columns",
            {
                "grid_id": GID,
                "body": {"revision": "3", "columns": [{"title": "C", "type": "string"}]},
            },
        )
    assert result.data.revision == "4"
    request = responses.calls[0].request
    assert request.method == "POST"
    # slug is derived from the title client-side — the live API rejects slug-less columns
    assert json.loads(request.body) == {  # ty: ignore[invalid-argument-type]
        "revision": "3",
        "columns": [{"title": "C", "type": "string", "slug": "c", "required": False}],
    }


@responses.activate
async def test_grids_remove_columns_tool_sends_delete_with_body(creds):
    responses.add(
        responses.DELETE, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_remove_columns",
            {"grid_id": GID, "body": {"revision": "3", "column_slugs": ["name"]}},
        )
    assert result.data.revision == "4"
    request = responses.calls[0].request
    assert request.method == "DELETE"
    assert json.loads(request.body) == {"revision": "3", "column_slugs": ["name"]}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_grids_move_columns_tool(creds):
    responses.add(
        responses.POST, f"{BASE}/grids/{GID}/columns/move", json={"revision": "4"}, status=200
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_move_columns",
            {"grid_id": GID, "body": {"revision": "3", "column_slug": "name", "position": 0}},
        )
    assert result.data.revision == "4"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"revision": "3", "column_slug": "name", "position": 0}  # ty: ignore[invalid-argument-type]


@responses.activate
async def test_grids_update_cells_tool(creds):
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/cells",
        json={"revision": "4", "cells": [{"row_id": "1", "column_slug": "name", "value": "x"}]},
        status=200,
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_update_cells",
            {
                "grid_id": GID,
                "body": {
                    "revision": "3",
                    "cells": [{"row_id": 1, "column_slug": "name", "value": "x"}],
                },
            },
        )
    assert result.data.revision == "4"
    assert result.data.cells[0].value == "x"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {  # ty: ignore[invalid-argument-type]
        "revision": "3",
        "cells": [{"row_id": 1, "column_slug": "name", "value": "x"}],
    }


@responses.activate
async def test_grids_clone_tool_returns_operation(creds):
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/clone",
        json={"operation": {"type": "clone_inline_grid", "id": "task-1"}},
        status=200,
    )
    async with Client(grids_mcp.mcp) as client:
        result = await client.call_tool(
            "grids_clone", {"grid_id": GID, "body": {"target": "data/y"}}
        )
    assert result.data.operation.id == "task-1"
    request = responses.calls[0].request
    assert request.method == "POST"
    assert json.loads(request.body) == {"target": "data/y", "with_data": False}  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("tool_name", "destructive", "idempotent"),
    [
        ("grids_create", False, False),
        ("grids_update", False, True),
        ("grids_delete", True, False),
        ("grids_add_rows", False, False),
        ("grids_remove_rows", True, False),
        ("grids_move_rows", False, False),
        ("grids_add_columns", False, False),
        ("grids_remove_columns", True, False),
        ("grids_move_columns", False, False),
        ("grids_update_cells", False, True),
        ("grids_clone", False, False),
    ],
)
async def test_grids_write_tools_carry_honest_hints(tool_name, destructive, idempotent):
    async with Client(grids_mcp.mcp) as client:
        tools = {t.name: t for t in await client.list_tools()}
    annotations = tools[tool_name].annotations
    assert annotations.readOnlyHint is False
    assert annotations.destructiveHint is destructive
    assert annotations.idempotentHint is idempotent
    assert annotations.title
