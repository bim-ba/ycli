"""TDD for `tracker import` CLI (wiring-dependent — run by the integrator after mount)."""

import json

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.tracker.yandex.net/v3"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_task():
    responses.add(responses.POST, f"{BASE}/issues/_import", json={"key": "TEST-1"}, status=200)
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "import",
            "task",
            "--queue",
            "TEST",
            "--summary",
            "Test",
            "--created-at",
            "2017-08-29T12:34:41.740+0000",
            "--created-by",
            "11",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "queue": "TEST",
        "summary": "Test",
        "createdAt": "2017-08-29T12:34:41.740+0000",
        "createdBy": "11",
    }


@responses.activate
def test_comment():
    responses.add(
        responses.POST,
        f"{BASE}/issues/TEST-1/comments/_import",
        json={"id": 1, "text": "T"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "import",
            "comment",
            "TEST-1",
            "--text",
            "T",
            "--created-at",
            "t",
            "--created-by",
            "11",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body)["createdBy"] == "11"  # ty: ignore[invalid-argument-type]


@responses.activate
def test_link():
    responses.add(
        responses.POST,
        f"{BASE}/issues/TEST-1/links/_import",
        json={"id": 51, "type": {"id": "relates"}},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "import",
            "link",
            "TEST-1",
            "--relationship",
            "relates",
            "--issue",
            "TEST-2",
            "--created-at",
            "t",
            "--created-by",
            "11",
        ],
    )
    assert res.exit_code == 0
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "relationship": "relates",
        "issue": "TEST-2",
        "createdAt": "t",
        "createdBy": "11",
    }


@responses.activate
def test_worklog_plural_path():
    responses.add(
        responses.POST,
        f"{BASE}/issues/TEST-1/worklogs/_import",
        json={"id": 37, "duration": "PT1H"},
        status=200,
    )
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "import",
            "worklog",
            "TEST-1",
            "--duration",
            "PT1H",
            "--created-at",
            "t",
            "--created-by",
            "u",
            "--start",
            "s",
        ],
    )
    assert res.exit_code == 0
    assert responses.calls[0].request.url.endswith("/worklogs/_import")  # ty: ignore[unresolved-attribute]


@responses.activate
def test_file(tmp_path):
    responses.add(
        responses.POST,
        f"{BASE}/issues/JUNE-2/attachments/_import",
        json={"id": "123", "name": "pic.png"},
        status=200,
    )
    upload = tmp_path / "pic.png"
    upload.write_bytes(b"PNGDATA")
    res = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "tracker",
            "import",
            "file",
            "JUNE-2",
            str(upload),
            "--created-at",
            "2020-01-01",
            "--created-by",
            "user",
        ],
    )
    assert res.exit_code == 0
    request = responses.calls[0].request
    assert "filename=pic.png" in request.url  # ty: ignore[unsupported-operator]
    body = request.body
    body = body.read() if hasattr(body, "read") else body  # ty: ignore[call-non-callable]
    assert b"PNGDATA" in body  # ty: ignore[unsupported-operator]
