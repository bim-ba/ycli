"""TDD for GridsClient — reads (get) plus writes; every mutating body asserts ``revision`` sent."""

import json

import requests
import responses

from ycli.yandex.wiki.grids.client import GridsClient
from ycli.yandex.wiki.grids.models import (
    CellsUpdateResult,
    Grid,
    GridActionResult,
    GridCloneOperation,
    RevisionResult,
    RowsAddResult,
)

BASE = "https://api.wiki.yandex.net/v1"
GID = "g-uuid"


def _client() -> GridsClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return GridsClient(session=session)


@responses.activate
def test_get_deserializes_grid_and_passes_query():
    responses.add(
        responses.GET,
        f"{BASE}/grids/{GID}",
        json={"id": GID, "title": "Roadmap", "revision": "3"},
        status=200,
    )
    grid = _client().get(GID, only_cols="name,owner", sort="name")
    assert isinstance(grid, Grid)
    assert grid.revision == "3" and grid.title == "Roadmap"
    params = responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
    assert params["only_cols"] == "name,owner"
    assert params["sort"] == "name"


@responses.activate
def test_get_omits_absent_query_params():
    responses.add(responses.GET, f"{BASE}/grids/{GID}", json={"id": GID}, status=200)
    _client().get(GID)
    assert "fields" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]
    assert "filter" not in responses.calls[0].request.params  # ty: ignore[unresolved-attribute]


@responses.activate
def test_create_posts_body_and_returns_grid():
    responses.add(responses.POST, f"{BASE}/grids", json={"id": GID, "title": "Roadmap"}, status=200)
    grid = _client().create(body={"title": "Roadmap", "page": {"slug": "data/x"}})
    assert isinstance(grid, Grid)
    assert grid.id == GID
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "title": "Roadmap",
        "page": {"slug": "data/x"},
    }


@responses.activate
def test_update_posts_revision_and_returns_revision():
    responses.add(responses.POST, f"{BASE}/grids/{GID}", json={"revision": "4"}, status=200)
    out = _client().update(GID, body={"revision": "3", "title": "New"})
    assert isinstance(out, RevisionResult)
    assert out.revision == "4"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["revision"] == "3"
    assert responses.calls[0].request.url.endswith(f"/grids/{GID}")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_delete_returns_synthesized_result():
    responses.add(responses.DELETE, f"{BASE}/grids/{GID}", status=204)
    out = _client().delete(GID)
    assert isinstance(out, GridActionResult)
    assert out.grid_id == GID and out.action == "delete" and out.ok is True
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_add_rows_posts_revision_and_returns_rows():
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/rows",
        json={"revision": "4", "results": [{"id": "r1", "row": [1]}]},
        status=200,
    )
    out = _client().add_rows(GID, body={"revision": "3", "rows": [{"name": "x"}]})
    assert isinstance(out, RowsAddResult)
    assert out.results[0].id == "r1"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["revision"] == "3"
    assert sent["rows"] == [{"name": "x"}]


@responses.activate
def test_remove_rows_is_delete_with_body_carrying_revision():
    responses.add(responses.DELETE, f"{BASE}/grids/{GID}/rows", json={"revision": "4"}, status=200)
    out = _client().remove_rows(GID, body={"revision": "3", "row_ids": ["r1"]})
    assert isinstance(out, RevisionResult)
    assert out.revision == "4"
    assert responses.calls[0].request.method == "DELETE"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "row_ids": ["r1"]}


@responses.activate
def test_move_rows_posts_revision():
    responses.add(
        responses.POST, f"{BASE}/grids/{GID}/rows/move", json={"revision": "4"}, status=200
    )
    out = _client().move_rows(GID, body={"revision": "3", "row_id": "r1", "position": 0})
    assert out.revision == "4"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["revision"] == "3"


@responses.activate
def test_add_columns_posts_revision():
    responses.add(responses.POST, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200)
    out = _client().add_columns(
        GID, body={"revision": "3", "columns": [{"title": "C", "type": "string"}]}
    )
    assert out.revision == "4"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["revision"] == "3"
    assert sent["columns"] == [{"title": "C", "type": "string"}]


@responses.activate
def test_remove_columns_is_delete_with_body_carrying_revision():
    responses.add(
        responses.DELETE, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200
    )
    out = _client().remove_columns(GID, body={"revision": "3", "column_slugs": ["name"]})
    assert out.revision == "4"
    assert responses.calls[0].request.method == "DELETE"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "column_slugs": ["name"]}


@responses.activate
def test_move_columns_posts_revision():
    responses.add(
        responses.POST, f"{BASE}/grids/{GID}/columns/move", json={"revision": "4"}, status=200
    )
    out = _client().move_columns(GID, body={"revision": "3", "column_slug": "name", "position": 0})
    assert out.revision == "4"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["revision"] == "3"


@responses.activate
def test_update_cells_posts_revision_and_returns_cells():
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/cells",
        json={"revision": "4", "cells": [{"row_id": "r1", "column_slug": "name", "value": "x"}]},
        status=200,
    )
    out = _client().update_cells(
        GID,
        body={"revision": "3", "cells": [{"row_id": 1, "column_slug": "name", "value": "x"}]},
    )
    assert isinstance(out, CellsUpdateResult)
    assert out.cells[0].value == "x"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["revision"] == "3"


@responses.activate
def test_clone_posts_body_and_returns_operation():
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/clone",
        json={"operation": {"type": "clone_inline_grid", "id": "task-1"}, "status_url": "u"},
        status=200,
    )
    out = _client().clone(GID, body={"target": "data/y", "with_data": True})
    assert isinstance(out, GridCloneOperation)
    assert out.operation is not None and out.operation.id == "task-1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "target": "data/y",
        "with_data": True,
    }
