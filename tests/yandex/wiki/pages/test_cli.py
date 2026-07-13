"""TDD for `wiki pages` CLI."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import WIKI_BASE as BASE

pytestmark = pytest.mark.integration

runner = CliRunner()


@responses.activate
def test_pages_get_prints_body():
    responses.add(
        responses.GET,
        f"{BASE}/pages",
        json={"id": 1, "slug": "data/x", "title": "T", "content": "# B"},
        status=200,
    )
    result = runner.invoke(cli.app, ["wiki", "pages", "get", "data/x"])
    assert result.exit_code == 0
    assert "# B" in result.stdout


@responses.activate
def test_pages_create_dumps_model_json():
    responses.add(
        responses.POST, f"{BASE}/pages", json={"id": 7, "slug": "data/x", "title": "T"}, status=200
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "pages",
            "create",
            "--slug",
            "data/x",
            "--title",
            "T",
            "--content",
            "# B",
        ],
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 7 and out["slug"] == "data/x"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"slug": "data/x", "title": "T", "content": "# B"}


@responses.activate
def test_pages_descendants_dumps_flat_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 2, "slug": "data/x/child"}], "next_cursor": None},
        status=200,
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "pages", "descendants", "data/x"])
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out[0]["slug"] == "data/x/child"
    req = responses.calls[-1].request
    assert req.params["slug"] == "data/x"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_pages_descendants_limit_option():
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={
            "results": [{"id": 1, "slug": "data/x/a"}, {"id": 2, "slug": "data/x/b"}],
            "next_cursor": None,
        },
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "pages", "descendants", "data/x", "--limit", "1"]
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert len(out) == 1
    assert out[0]["slug"] == "data/x/a"


@responses.activate
def test_pages_descendants_all_flag():
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 1, "slug": "data/x/a"}], "next_cursor": "c1"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/pages/descendants",
        json={"results": [{"id": 2, "slug": "data/x/b"}], "next_cursor": None},
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "pages", "descendants", "data/x", "--all"]
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    slugs = [item["slug"] for item in out]
    assert "data/x/a" in slugs
    assert "data/x/b" in slugs


@responses.activate
def test_pages_update_dumps_model_json():
    responses.add(
        responses.POST,
        f"{BASE}/pages/77",
        json={"id": 77, "slug": "data/x", "title": "New"},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        ["--format", "json", "wiki", "pages", "update", "77", "--content", "# U", "--title", "New"],
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 77 and out["title"] == "New"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"content": "# U", "title": "New"}


@responses.activate
def test_pages_get_by_id_dumps_model_json():
    responses.add(
        responses.GET,
        f"{BASE}/pages/12345",
        json={"id": 12345, "slug": "data/x", "title": "T", "content": "# B"},
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "pages", "get-by-id", "12345", "--fields", "content"]
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["id"] == 12345 and out["content"] == "# B"


@responses.activate
def test_pages_descendants_by_id_dumps_flat_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/12345/descendants",
        json={"results": [{"id": 2, "slug": "data/x/child"}], "next_cursor": None},
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "pages", "descendants-by-id", "12345"]
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out[0]["slug"] == "data/x/child"


@responses.activate
def test_pages_grids_dumps_flat_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/grids",
        json={"results": [{"id": "g1", "title": "Roadmap"}], "next_cursor": None},
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "pages", "grids", "42", "--order-by", "title"]
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out[0]["title"] == "Roadmap"
    assert responses.calls[-1].request.params["order_by"] == "title"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_pages_delete_emits_recovery_token():
    responses.add(
        responses.DELETE, f"{BASE}/pages/42", json={"recovery_token": "tok-uuid"}, status=200
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "pages", "delete", "42"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["recovery_token"] == "tok-uuid"
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_pages_append_posts_typed_body():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/append-content",
        json={"id": 42, "slug": "data/x", "title": "T"},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "pages",
            "append",
            "42",
            "--content",
            "## More",
            "--location",
            "bottom",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["id"] == 42
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"content": "## More", "body": {"location": "bottom"}}


@responses.activate
def test_pages_append_default_sends_bottom_body_selector():
    """Bare ``append`` (no --location) must send the ``body: bottom`` selector — the live API
    requires exactly one of body/section/anchor and 400s on a content-only payload."""
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/append-content",
        json={"id": 42, "slug": "data/x", "title": "T"},
        status=200,
    )
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "pages", "append", "42", "--content", "## More"]
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"content": "## More", "body": {"location": "bottom"}}


@responses.activate
def test_pages_append_location_top():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/append-content",
        json={"id": 42, "slug": "data/x", "title": "T"},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "pages",
            "append",
            "42",
            "--content",
            "## More",
            "--location",
            "top",
        ],
    )
    assert result.exit_code == 0
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"content": "## More", "body": {"location": "top"}}


def test_pages_subcommand_help_needs_no_creds(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    result = runner.invoke(cli.app, ["wiki", "pages", "get", "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "usage" in result.stdout.lower()


@responses.activate
def test_pages_clone_no_wait_prints_operation():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/clone",
        json={"operation": {"type": "clone", "id": "task-1"}, "status_url": "u"},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        ["--format", "json", "wiki", "pages", "clone", "42", "--target", "data/y", "--no-wait"],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["operation"]["id"] == "task-1"
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent == {"target": "data/y", "subscribe_me": False}


@responses.activate
def test_pages_clone_wait_polls_operations_to_terminal():
    """NOTE wiring-dependent: --wait reaches ``wiki.operations`` (mounted by the integrator)."""
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/clone",
        json={"operation": {"type": "clone", "id": "task-1"}, "status_url": "u"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/operations/clone/task-1",
        json={"status": "success", "result": {"page": {"id": 99, "slug": "data/y"}}},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "pages",
            "clone",
            "42",
            "--target",
            "data/y",
            "--subscribe-me",
        ],
    )
    assert result.exit_code == 0
    out = json.loads(result.stdout)
    assert out["status"] == "success"
    assert out["result"]["page"]["slug"] == "data/y"
