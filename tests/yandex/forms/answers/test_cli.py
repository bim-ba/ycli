"""`forms answers export --wait`: poll the export to a terminal status, then download the file."""

import json
import time

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import FORMS_BASE as BASE

SID = "686d0a1b2c3d4e5f00000030"
ANSWERS = f"{BASE}/surveys/{SID}/answers"
runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda *_: None)


def test_export_waits_then_downloads(api, tmp_path):
    api.add("POST", f"{ANSWERS}/export", json={"id": "op-1", "status": "wait"}, status=202)
    api.add("GET", f"{ANSWERS}/export-results", json={"id": "op-1", "status": "wait"})
    api.add("GET", f"{ANSWERS}/export-results", json={"id": "op-1", "status": "ok"})
    api.add("GET", f"{ANSWERS}/export-results", content=b"xlsxbytes")
    target = tmp_path / "answers.xlsx"
    res = runner.invoke(cli.app, ["forms", "answers", "export", SID, "--output", str(target)])
    assert res.exit_code == 0, res.output
    assert target.read_bytes() == b"xlsxbytes"
    assert len(api.calls) == 4  # export, two status polls, the download


def test_export_finishes_on_a_redirect_to_the_file(api, tmp_path):
    file_url = "https://forms.s3.test/uploads/answers.csv"
    api.add("POST", f"{ANSWERS}/export", json={"id": "op-1", "status": "wait"}, status=202)
    api.add("GET", f"{ANSWERS}/export-results", status=302, headers={"Location": file_url})
    api.add("GET", file_url, content=b"Name\nAnn\n")
    target = tmp_path / "answers.csv"
    res = runner.invoke(cli.app, ["forms", "answers", "export", SID, "--output", str(target)])
    assert res.exit_code == 0, res.output
    assert target.read_bytes() == b"Name\nAnn\n"
    # The status read sees the redirect without following it; only the download fetches the file.
    assert [call.url.host for call in api.calls].count("forms.s3.test") == 1


def test_export_prints_a_failed_status(api):
    api.add("POST", f"{ANSWERS}/export", json={"id": "op-2", "status": "wait"}, status=202)
    api.add(
        "GET", f"{ANSWERS}/export-results", json={"id": "op-2", "status": "fail", "message": "boom"}
    )
    res = runner.invoke(cli.app, ["--format", "json", "forms", "answers", "export", SID])
    assert res.exit_code == 0, res.output
    assert json.loads(res.stdout)["message"] == "boom"
