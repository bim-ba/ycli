"""Wiki CLI behaviour a contract case cannot express: refusals, ``--wait`` polling, help."""

import json
import re

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import WIKI_BASE as BASE

GID = "7d1c2b3a-4e5f-4a6b-8c7d-9e0f1a2b3c4d"


def _plain(output: str) -> str:
    # CI forces colour: drop the escape codes and the panel border before matching the words.
    return " ".join(re.sub(r"[│╭╮╰╯─]", " ", re.sub(r"\x1b\[[0-9;]*m", "", output)).split())


def test_grids_create_needs_a_page(api):
    res = CliRunner().invoke(cli.app, ["wiki", "grids", "create", "--title", "R"])
    assert res.exit_code != 0
    assert "provide --page-slug or --page-id" in _plain(res.output)
    assert api.calls == []


def test_grids_update_refuses_the_read_shape_of_default_sort(api):
    """The ``{slug, direction}`` read shape is a 400 live, so it fails before sending."""
    argv = ["wiki", "grids", "update", GID, "--revision", "3", "--default-sort"]
    res = CliRunner().invoke(cli.app, [*argv, '[{"slug": "a", "direction": "asc"}]'])
    assert res.exit_code != 0
    assert api.calls == []


@pytest.mark.parametrize(
    ("argv", "trigger", "status_path", "status"),
    [
        (
            ["pages", "clone", "42", "--target", "data/y"],
            "pages/42/clone",
            "operations/clone/task-1",
            {"status": "success", "result": {"page": {"id": 99, "slug": "data/y"}}},
        ),
        (
            ["grids", "clone", GID, "--target", "data/y"],
            f"grids/{GID}/clone",
            "operations/clone_inline_grid/task-1",
            {"status": "success", "result": {"grid_id": "g2"}},
        ),
    ],
)
def test_clone_waits_for_the_operation_by_default(api, argv, trigger, status_path, status):
    api.add("POST", f"{BASE}/{trigger}", json={"operation": {"type": "clone", "id": "task-1"}})
    api.add("GET", f"{BASE}/{status_path}", json=status)
    res = CliRunner().invoke(cli.app, ["--format", "json", "wiki", *argv])
    assert res.exit_code == 0, res.output
    printed = json.loads(res.stdout)
    assert printed["status"] == "success"
    assert printed["result"] == {**printed["result"], **status["result"]}
    assert [request.method for request in api.calls] == ["POST", "GET"]


def test_clone_without_an_operation_id_prints_the_trigger_reply(api):
    api.add("POST", f"{BASE}/pages/42/clone", json={"status_url": "u"})
    res = CliRunner().invoke(
        cli.app, ["--format", "json", "wiki", "pages", "clone", "42", "--target", "data/y"]
    )
    assert res.exit_code == 0, res.output
    assert json.loads(res.stdout)["status_url"] == "u"
    assert len(api.calls) == 1


@pytest.mark.parametrize("group", ["pages", "grids", "operations"])
def test_help_needs_no_credentials(monkeypatch, group):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    res = CliRunner().invoke(cli.app, ["wiki", group, "--help"])
    assert res.exit_code == 0
    assert "usage" in res.stdout.lower()
