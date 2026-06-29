"""TDD for `forms answers` CLI — dumps the {columns, answers, next} envelope."""

import json
from urllib.parse import parse_qs, urlparse

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


def _two_page_callback(request):
    """Page 1 hands a next_url with ``id=100``; page 2 drains it."""
    if "id" not in parse_qs(urlparse(request.url).query):
        body = {
            "columns": [],
            "answers": [{"id": 1, "created": "x", "data": []}],
            "next": {"next_url": f"{BASE}/surveys/{SID}/answers?id=100"},
        }
    else:
        body = {"columns": [], "answers": [{"id": 2, "created": "x", "data": []}], "next": None}
    return (200, {}, json.dumps(body))


@responses.activate
def test_list_dumps_envelope():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
            "answers": [{"id": 99, "created": "2026-01-01", "data": [{"value": "x"}]}],
            "next": None,
        },
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "answers", "list", SID])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["answers"][0]["id"] == 99 and out["next"] is None


@responses.activate
def test_list_drains_all_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        callback=_two_page_callback,
        content_type="application/json",
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "answers", "list", SID])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert [a["id"] for a in out["answers"]] == [1, 2]
    assert out["next"] is None


@responses.activate
def test_list_with_limit_caps_results():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        json={
            "columns": [],
            "answers": [
                {"id": 1, "created": "x", "data": []},
                {"id": 2, "created": "x", "data": []},
            ],
            "next": {"next_url": f"{BASE}/surveys/{SID}/answers?id=2"},
        },
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "forms", "answers", "list", SID, "--limit", "1"]
    )
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert len(out["answers"]) == 1
    assert out["next"] is None


@responses.activate
def test_list_with_all_flag_drains_all_pages():
    responses.add_callback(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers",
        callback=_two_page_callback,
        content_type="application/json",
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "answers", "list", SID, "--all"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert [a["id"] for a in out["answers"]] == [1, 2]
    assert out["next"] is None
