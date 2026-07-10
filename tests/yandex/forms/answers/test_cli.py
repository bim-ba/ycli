"""TDD for `forms answers` CLI — dumps the {columns, answers, next} envelope + async export.

The ``export --wait`` tests poll ``answers export-results`` to a terminal state; ``time.sleep``
is monkeypatched to a no-op so the wait → ok sequence resolves instantly.
"""

import json
import time
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
    monkeypatch.setattr(time, "sleep", lambda *_: None)  # no real waiting in the --wait poll


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
def test_get_dumps_answer_detail():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/99",
        json={
            "id": 99,
            "created": "2026-01-01",
            "survey": {"id": SID, "name": "F"},
            "data": [{"id": "q1", "label": "Name", "type": "string", "value": "Ann"}],
        },
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "answers", "get", SID, "99"])
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["id"] == 99 and out["data"][0]["value"] == "Ann"


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


@responses.activate
def test_export_no_wait_prints_started_operation():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/answers/export",
        json={"id": "op-1", "status": "wait", "message": "started"},
        status=202,
    )
    res = runner.invoke(
        cli.app,
        ["--format", "json", "forms", "answers", "export", SID, "--format", "xlsx", "--no-wait"],
    )
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["id"] == "op-1" and out["status"] == "wait"
    assert json.loads(responses.calls[0].request.body)["format"] == "xlsx"  # ty: ignore[invalid-argument-type]


@responses.activate
def test_export_wait_polls_then_downloads_file(tmp_path):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/answers/export",
        json={"id": "op-1", "status": "wait"},
        status=202,
    )
    # export-results is polled (wait, then ok), then hit once more to download the file bytes
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/export-results",
        json={"id": "op-1", "status": "wait"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/export-results",
        json={"id": "op-1", "status": "ok"},
        status=200,
    )
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/export-results",
        body=b"xlsxbytes",
        status=200,
    )
    target = tmp_path / "answers.xlsx"
    res = runner.invoke(
        cli.app,
        ["forms", "answers", "export", SID, "--format", "xlsx", "--output", str(target)],
    )
    assert res.exit_code == 0
    assert target.read_bytes() == b"xlsxbytes"
    # POST + two status polls + one download == 4 calls
    assert len(responses.calls) == 4


@responses.activate
def test_export_wait_failed_prints_status():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/answers/export",
        json={"id": "op-2", "status": "wait"},
        status=202,
    )
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/answers/export-results",
        json={"id": "op-2", "status": "fail", "message": "boom"},
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "forms", "answers", "export", SID, "--format", "csv"]
    )
    assert res.exit_code == 0
    out = json.loads(res.stdout)
    assert out["status"] == "fail" and out["message"] == "boom"
