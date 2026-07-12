"""TDD for `wiki grids` CLI.

NOTE: these invoke the ROOT ``cli.app`` and need the grids (and, for ``clone --wait``, the
operations) resource MOUNTED — they pass only after the integrator wires the domain and regens
snapshots. The producer self-validates test_client/test_models/test_mcp instead.
"""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.wiki.yandex.net/v1"
GID = "g-uuid"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_grids_get_dumps_model():
    responses.add(
        responses.GET, f"{BASE}/grids/{GID}", json={"id": GID, "title": "Roadmap"}, status=200
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "grids", "get", GID])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["title"] == "Roadmap"


@responses.activate
def test_grids_create_by_slug():
    responses.add(responses.POST, f"{BASE}/grids", json={"id": GID, "title": "R"}, status=200)
    result = runner.invoke(
        cli.app,
        ["--format", "json", "wiki", "grids", "create", "--title", "R", "--page-slug", "data/x"],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"title": "R", "page": {"slug": "data/x"}}


@responses.activate
def test_grids_create_by_page_id():
    responses.add(responses.POST, f"{BASE}/grids", json={"id": GID}, status=200)
    result = runner.invoke(
        cli.app,
        ["--format", "json", "wiki", "grids", "create", "--title", "R", "--page-id", "42"],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"title": "R", "page": {"id": 42}}


def test_grids_create_requires_page():
    result = runner.invoke(cli.app, ["wiki", "grids", "create", "--title", "R"])
    assert result.exit_code != 0


@responses.activate
def test_grids_update_sends_revision():
    responses.add(responses.POST, f"{BASE}/grids/{GID}", json={"revision": "4"}, status=200)
    result = runner.invoke(
        cli.app,
        ["--format", "json", "wiki", "grids", "update", GID, "--revision", "3", "--title", "New"],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "title": "New"}


@responses.activate
def test_grids_update_with_default_sort_write_shape():
    """``--default-sort`` sends the API's write shape ``[{"<column_slug>": "asc"|"desc"}]``
    verbatim (the read shape ``[{slug, title, direction}]`` is a 400 live)."""
    responses.add(responses.POST, f"{BASE}/grids/{GID}", json={"revision": "4"}, status=200)
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "update",
            GID,
            "--revision",
            "3",
            "--default-sort",
            '[{"col": "asc"}]',
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "default_sort": [{"col": "asc"}]}


@responses.activate
def test_grids_update_default_sort_read_shape_fails_fast():
    """Feeding the READ shape must fail client-side (no silent [{}] strip, no request sent)."""
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "update",
            GID,
            "--revision",
            "3",
            "--default-sort",
            '[{"slug": "a", "direction": "asc"}]',
        ],
    )
    assert result.exit_code != 0
    assert len(responses.calls) == 0


@responses.activate
def test_grids_delete_emits_result():
    responses.add(responses.DELETE, f"{BASE}/grids/{GID}", status=204)
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "grids", "delete", GID])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["action"] == "delete"


@responses.activate
def test_grids_rows_add_sends_revision_and_rows():
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/rows",
        json={"revision": "4", "results": []},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "rows",
            "add",
            GID,
            "--revision",
            "3",
            "--rows",
            '[{"name": "x"}]',
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "rows": [{"name": "x"}]}


@responses.activate
def test_grids_rows_remove_sends_revision_and_ids():
    responses.add(responses.DELETE, f"{BASE}/grids/{GID}/rows", json={"revision": "4"}, status=200)
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "rows",
            "remove",
            GID,
            "--revision",
            "3",
            "--row-id",
            "r1",
            "--row-id",
            "r2",
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "row_ids": ["r1", "r2"]}


@responses.activate
def test_grids_rows_move_sends_revision():
    responses.add(
        responses.POST, f"{BASE}/grids/{GID}/rows/move", json={"revision": "4"}, status=200
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "rows",
            "move",
            GID,
            "--revision",
            "3",
            "--row-id",
            "r1",
            "--position",
            "0",
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "row_id": "r1", "position": 0}


@responses.activate
def test_grids_columns_add_sends_revision_and_columns():
    responses.add(responses.POST, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200)
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "columns",
            "add",
            GID,
            "--revision",
            "3",
            "--columns",
            '[{"title": "C", "type": "string"}]',
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "revision": "3",
        "columns": [{"title": "C", "type": "string", "slug": "c", "required": False}],
    }


@responses.activate
def test_grids_columns_add_derives_slug_from_title():
    """The live API 400s on a slug-less column; the documented slug-less JSON keeps working
    because the slug is derived from the title client-side."""
    responses.add(responses.POST, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200)
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "columns",
            "add",
            GID,
            "--revision",
            "3",
            "--columns",
            '[{"title":"My Col","type":"string"},{"title":"X","type":"number","slug":"n"}]',
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert [c["slug"] for c in sent["columns"]] == ["my_col", "n"]


@responses.activate
def test_grids_columns_add_always_sends_required():
    """Bug 3: the API rejects a column without ``required``; it must always be serialized."""
    responses.add(responses.POST, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200)
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "columns",
            "add",
            GID,
            "--revision",
            "3",
            "--columns",
            '[{"title": "C", "type": "string"}]',
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["columns"][0]["required"] is False


@responses.activate
def test_grids_columns_remove_sends_revision_and_slugs():
    responses.add(
        responses.DELETE, f"{BASE}/grids/{GID}/columns", json={"revision": "4"}, status=200
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "columns",
            "remove",
            GID,
            "--revision",
            "3",
            "--column-slug",
            "name",
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "column_slugs": ["name"]}


@responses.activate
def test_grids_columns_move_sends_revision():
    responses.add(
        responses.POST, f"{BASE}/grids/{GID}/columns/move", json={"revision": "4"}, status=200
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "columns",
            "move",
            GID,
            "--revision",
            "3",
            "--column-slug",
            "name",
            "--columns-count",
            "2",
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"revision": "3", "column_slug": "name", "columns_count": 2}


@responses.activate
def test_grids_cells_update_sends_revision_and_cells():
    responses.add(
        responses.POST, f"{BASE}/grids/{GID}/cells", json={"revision": "4", "cells": []}, status=200
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "grids",
            "cells",
            "update",
            GID,
            "--revision",
            "3",
            "--cells",
            '[{"row_id": 1, "column_slug": "name", "value": "x"}]',
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {
        "revision": "3",
        "cells": [{"row_id": 1, "column_slug": "name", "value": "x"}],
    }


@responses.activate
def test_grids_clone_no_wait_prints_operation():
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/clone",
        json={"operation": {"type": "clone_inline_grid", "id": "task-1"}, "status_url": "u"},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        ["--format", "json", "wiki", "grids", "clone", GID, "--target", "data/y", "--no-wait"],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["operation"]["id"] == "task-1"


@responses.activate
def test_grids_clone_wait_polls_operation_to_terminal():
    responses.add(
        responses.POST,
        f"{BASE}/grids/{GID}/clone",
        json={"operation": {"type": "clone_inline_grid", "id": "task-1"}, "status_url": "u"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone_inline_grid/task-1",
        json={"status": "success", "result": {"grid_id": "g2"}},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        ["--format", "json", "wiki", "grids", "clone", GID, "--target", "data/y", "--with-data"],
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["status"] == "success"
    assert out["result"]["grid_id"] == "g2"


def test_grids_help_needs_no_creds(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    result = runner.invoke(cli.app, ["wiki", "grids", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "usage" in result.stdout.lower()
