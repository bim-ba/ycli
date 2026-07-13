"""`wiki uploadsessions` CLI tests (invoke the ROOT app → wiring-dependent).

These invoke ``cli.app`` and reach ``app_ctx.wiki.uploadsessions``; they pass only AFTER the
integrator mounts the sub-app on the wiki CLI and wires ``UploadSessionsClient`` into
``WikiClient``. Producer self-validation covers test_client / test_models / test_mcp.
"""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import WIKI_BASE as BASE

runner = CliRunner()

_SESSION_JSON = {"session_id": "s-1", "file_name": "d.png", "file_size": 4, "status": "not_started"}


@responses.activate
def test_uploadsessions_create():
    responses.add(responses.POST, f"{BASE}/upload_sessions", json=_SESSION_JSON, status=200)
    result = runner.invoke(
        cli.app,
        [
            "--format",
            "json",
            "wiki",
            "uploadsessions",
            "create",
            "--file-name",
            "d.png",
            "--file-size",
            "4",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["session_id"] == "s-1"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "file_name": "d.png",
        "file_size": 4,
    }


@responses.activate
def test_uploadsessions_get():
    responses.add(responses.GET, f"{BASE}/upload_sessions/s-1", json=_SESSION_JSON, status=200)
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "uploadsessions", "get", "s-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["session_id"] == "s-1"


@responses.activate
def test_uploadsessions_upload_part_reads_file_bytes(tmp_path):
    responses.add(
        responses.PUT,
        f"{BASE}/upload_sessions/s-1/upload_part",
        json={**_SESSION_JSON, "status": "in_progress"},
        status=200,
    )
    part = tmp_path / "part.bin"
    part.write_bytes(b"\x00\x01RAW")
    result = runner.invoke(
        cli.app,
        ["wiki", "uploadsessions", "upload-part", "s-1", str(part), "--part-number", "2"],
    )
    assert result.exit_code == 0
    request = responses.calls[0].request
    assert request.body == b"\x00\x01RAW"
    assert request.headers["Content-Type"] == "application/octet-stream"
    assert request.params["part_number"] == "2"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_uploadsessions_finish():
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/s-1/finish",
        json={**_SESSION_JSON, "status": "finished"},
        status=200,
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "uploadsessions", "finish", "s-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["status"] == "finished"


@responses.activate
def test_uploadsessions_abort():
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/s-1/abort",
        json={**_SESSION_JSON, "status": "aborted"},
        status=200,
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "uploadsessions", "abort", "s-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["status"] == "aborted"


@responses.activate
def test_uploadsessions_abort_all():
    responses.add(
        responses.POST,
        f"{BASE}/upload_sessions/abort_active_uploads",
        json={"status": "ok"},
        status=200,
    )
    result = runner.invoke(cli.app, ["--format", "json", "wiki", "uploadsessions", "abort-all"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["status"] == "ok"
