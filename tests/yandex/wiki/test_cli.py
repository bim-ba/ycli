"""Wiki CLI behaviour a contract case cannot express: refusals, ``--wait`` polling, help."""

import json
import re

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import WIKI_BASE as BASE

GID = "7d1c2b3a-4e5f-4a6b-8c7d-9e0f1a2b3c4d"


def _plain(output: str) -> str:
    # CI forces colour: drop the escape codes and the panel border before matching the words.
    return " ".join(re.sub(r"[│╭╮╰╯─]", " ", re.sub(r"\x1b\[[0-9;]*m", "", output)).split())


def _refused(argv: list[str]) -> list[tuple[str, str]]:
    """The pydantic errors a command raises before sending (the root prints them)."""
    result = CliRunner().invoke(cli.app, ["wiki", *argv])
    assert isinstance(result.exception, ValidationError), result.output
    return [
        (str(error["loc"][0] if error["loc"] else ""), error["type"])
        for error in result.exception.errors()
    ]


@pytest.mark.parametrize(
    ("flags", "missing"),
    [(["--created-from", "2026-01-01"], "to"), (["--modified-to", "2026-02-01"], "from")],
)
def test_an_open_ended_search_window_names_the_missing_end(api, flags, missing):
    assert _refused(["search", "query", "plan", *flags]) == [(missing, "missing")]
    assert api.calls == []


def test_a_group_grant_needs_both_its_directory_and_its_id(api):
    argv = ["access", "create", "1", "--role", "reader", "--group-id", "7"]
    assert _refused(argv) == [("src", "missing")]
    assert api.calls == []


def test_a_grant_names_a_user_or_a_group(api):
    assert _refused(["access", "create", "1", "--role", "reader"]) == [("", "value_error")]
    assert api.calls == []


def test_grids_create_needs_a_page(api):
    res = CliRunner().invoke(cli.app, ["wiki", "grids", "create", "--title", "R"])
    assert res.exit_code != 0
    assert "provide --page-slug or --page-id" in _plain(res.output)
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


def test_move_waits_for_the_operation_by_default(api):
    api.add("POST", f"{BASE}/pages/move", json={"operation": {"type": "move", "id": "task-9"}})
    api.add(
        "GET",
        f"{BASE}/operations/move/task-9",
        json={"status": "success", "result": {"page_count": 3}},
    )
    res = CliRunner().invoke(cli.app, ["--format", "json", "wiki", "pages", "move", "a/x", "b/x"])
    assert res.exit_code == 0, res.output
    printed = json.loads(res.stdout)
    assert printed["status"] == "success"
    assert printed["result"] == {"page_count": 3}
    assert [request.method for request in api.calls] == ["POST", "GET"]


def test_move_without_an_operation_id_prints_the_trigger_reply(api):
    api.add("POST", f"{BASE}/pages/move", json={"status_url": "u"})
    res = CliRunner().invoke(cli.app, ["--format", "json", "wiki", "pages", "move", "a/x", "b/x"])
    assert res.exit_code == 0, res.output
    assert json.loads(res.stdout)["status_url"] == "u"
    assert len(api.calls) == 1


@pytest.mark.parametrize(
    ("argv", "refused"),
    [
        (["grids", "columns", "suggest", GID], ("", "value_error")),
        (["grids", "columns", "suggest", GID, "--title", "A", "--slug", "a"], ("", "value_error")),
    ],
)
def test_undocumented_writes_refuse_what_the_api_would_before_sending(api, argv, refused):
    assert _refused(argv) == [refused]
    assert api.calls == []


@pytest.mark.parametrize(
    ("argv", "path", "sent"),
    [
        (
            ["attachments", "list", "7", "--order-by", "weight", "--order-direction", "up"],
            "pages/7/attachments",
            {"order_by": "weight", "order_direction": "up"},
        ),
        (
            ["comments", "list", "7", "--status", "open"],
            "pages/7/comments",
            {"status_filter": "open"},
        ),
        (
            ["resources", "list", "7", "--order-by", "name"],
            "pages/7/resources",
            {"order_by": "name"},
        ),
    ],
)
def test_a_value_outside_a_known_set_is_sent_as_given(api, argv, path, sent):
    """A set names the values Yandex publishes; another one is the API's to refuse (#278)."""
    api.add("GET", f"{BASE}/{path}", json={"results": []})
    result = CliRunner().invoke(cli.app, ["wiki", *argv])
    assert result.exit_code == 0, result.output
    query = dict(api.calls[-1].url.params)
    assert {name: query[name] for name in sent} == sent


def test_an_option_shows_the_values_of_its_set():
    result = CliRunner().invoke(cli.app, ["wiki", "attachments", "list", "--help"])
    help_text = " ".join(result.output.replace("│", " ").split())
    assert "One of: name, size, created_at." in help_text
    assert "One of: asc, desc." in help_text


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
