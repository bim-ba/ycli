"""TDD for `wiki operations` CLI.

NOTE: these invoke the ROOT ``cli.app`` and need the operations resource MOUNTED — they pass
only after the integrator wires the domain and regens snapshots.
"""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_operations_clone_prints_status():
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone/task-1",
        json={"status": "success", "result": {"page": {"id": 42, "slug": "data/y"}}},
        status=200,
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "operations", "clone", "task-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["status"] == "success"


@responses.activate
def test_operations_gridclone_prints_status():
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone_inline_grid/task-1",
        json={"status": "success", "result": {"grid_id": "g2"}},
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "operations", "gridclone", "task-1"]
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["result"]["grid_id"] == "g2"


def test_operations_help_needs_no_creds(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    result = runner.invoke(cli.app, ["wiki", "operations", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "usage" in result.stdout.lower()
