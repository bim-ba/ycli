"""TDD for `forms files` CLI — upload/verify/download/delete (needs the resource mounted)."""

import json

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


@responses.activate
def test_upload(tmp_path):
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/files",
        json={"name": "cv.pdf", "path": "a/b/cv.pdf", "check_status": "check"},
        status=201,
    )
    local = tmp_path / "cv.pdf"
    local.write_bytes(b"%PDF123")
    res = runner.invoke(cli.app, ["--format", "json", "forms", "files", "upload", SID, str(local)])
    assert res.exit_code == 0
    assert json.loads(res.stdout)["path"] == "a/b/cv.pdf"


@responses.activate
def test_verify():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/files/verify",
        json=[{"name": "cv.pdf", "check_status": "ready"}],
        status=200,
    )
    res = runner.invoke(
        cli.app, ["--format", "json", "forms", "files", "verify", SID, "--path", "a/b/cv.pdf"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["check_status"] == "ready"


@responses.activate
def test_download_writes_output_file(tmp_path):
    responses.add(responses.GET, f"{BASE}/files", body=b"\x89PNGdata", status=200)
    out = tmp_path / "got.bin"
    res = runner.invoke(
        cli.app, ["forms", "files", "download", "--path", "a/b/cv.pdf", "--output", str(out)]
    )
    assert res.exit_code == 0
    assert out.read_bytes() == b"\x89PNGdata"


@responses.activate
def test_delete():
    responses.add(responses.DELETE, f"{BASE}/files", json={}, status=200)
    res = runner.invoke(
        cli.app, ["--format", "json", "forms", "files", "delete", "--path", "a/b/cv.pdf"]
    )
    assert res.exit_code == 0
    assert json.loads(res.stdout)["ok"] is True


def test_verify_requires_path_or_url():
    res = runner.invoke(cli.app, ["forms", "files", "verify", SID])
    assert res.exit_code != 0


def test_verify_url_count_must_match_path_count():
    res = runner.invoke(cli.app, ["forms", "files", "verify", SID, "--url", "https://x"])
    assert res.exit_code != 0


def test_delete_requires_path_or_url():
    res = runner.invoke(cli.app, ["forms", "files", "delete"])
    assert res.exit_code != 0
