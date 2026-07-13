"""TDD for `wiki attachments` CLI."""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


@responses.activate
def test_attachments_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "f.pdf", "size": "0.00", "mimetype": "application/pdf"}]},
        status=200,
    )
    result = runner.invoke(cli.app, ["wiki", "attachments", "list", "42"])
    assert result.exit_code == 0 and "f.pdf" in result.stdout


@responses.activate
def test_attachments_download_writes_bytes_to_output(tmp_path):
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments/7/download",
        body=b"\x00\x01BLOB",
        status=200,
    )
    target = tmp_path / "out.bin"
    result = runner.invoke(
        cli.app, ["wiki", "attachments", "download", "42", "7", "--output", str(target)]
    )
    assert result.exit_code == 0
    assert target.read_bytes() == b"\x00\x01BLOB"


@responses.activate
def test_attachments_download_by_url_writes_bytes_to_output(tmp_path):
    responses.add(
        responses.GET,
        f"{BASE}/pages/attachments/download_by_url",
        body=b"%PDF blob",
        status=200,
    )
    target = tmp_path / "report.pdf"
    result = runner.invoke(
        cli.app,
        [
            "wiki",
            "attachments",
            "download-by-url",
            "data/x/.files/report.pdf",
            "--output",
            str(target),
        ],
    )
    assert result.exit_code == 0
    assert target.read_bytes() == b"%PDF blob"


@responses.activate
def test_attachments_delete_confirms():
    responses.add(responses.DELETE, f"{BASE}/pages/42/attachments/7", body="", status=204)
    result = runner.invoke(
        cli.app, ["--format", "json", "wiki", "attachments", "delete", "42", "7"]
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"ok": True, "detail": "deleted attachment 7 from page 42"}
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_attachments_attach():
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"id": 7, "name": "d.png"}]},
        status=200,
    )
    result = runner.invoke(
        cli.app,
        ["wiki", "attachments", "attach", "42", "--session", "s-1", "--session", "s-2"],
    )
    assert result.exit_code == 0 and "d.png" in result.stdout
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "upload_sessions": ["s-1", "s-2"]
    }


@responses.activate
def test_attachments_upload_runs_pipeline(tmp_path):
    """WIRING-DEPENDENT: needs UploadSessionsClient wired into WikiClient (integrator runs)."""
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions",
        json={"session_id": "s-1", "status": "not_started"},
        status=200,
    )
    responses.add(
        responses.PUT,
        f"{BASE}/upload_sessions/s-1/upload_part",
        json={"session_id": "s-1", "status": "in_progress"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/s-1/finish",
        json={"session_id": "s-1", "status": "finished"},
        status=200,
    )
    responses.add(
        responses.POST,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"id": 9, "name": "d.png"}]},
        status=200,
    )
    local = tmp_path / "d.png"
    local.write_bytes(b"\x89PNGraw")
    result = runner.invoke(cli.app, ["wiki", "attachments", "upload", "42", str(local)])
    assert result.exit_code == 0 and "d.png" in result.stdout
    assert [c.request.method for c in responses.calls] == ["POST", "PUT", "POST", "POST"]
