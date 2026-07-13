"""TDD for `tracker attachments` CLI — list renders, download/thumbnail write bytes to --output.

NOTE: these invoke the ROOT app (``cli.app``), so they pass only after the integrator MOUNTS
the resource (``app.add_typer(attachments_app)`` in tracker/cli.py). The producer self-validates
test_client / test_models / test_mcp only.
"""

import json

import responses
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE

runner = CliRunner()


@responses.activate
def test_list_renders_json():
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/attachments",
        json=[{"id": "123", "name": "picture.jpg"}],
        status=200,
    )
    res = runner.invoke(cli.app, ["--format", "json", "tracker", "attachments", "list", "JUNE-2"])
    assert res.exit_code == 0
    assert json.loads(res.stdout)[0]["name"] == "picture.jpg"


@responses.activate
def test_download_writes_bytes_to_output(tmp_path):
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/attachments/4159/attachment.txt",
        body=b"\x89PNGbytes",
        status=200,
    )
    out = tmp_path / "attachment.txt"
    res = runner.invoke(
        cli.app,
        [
            "tracker",
            "attachments",
            "download",
            "JUNE-2",
            "4159",
            "attachment.txt",
            "--output",
            str(out),
        ],
    )
    assert res.exit_code == 0
    assert out.read_bytes() == b"\x89PNGbytes"


@responses.activate
def test_thumbnail_writes_bytes_to_output(tmp_path):
    responses.add(
        responses.GET,
        f"{BASE}/issues/JUNE-2/thumbnails/4159",
        body=b"\x89PNGthumb",
        status=200,
    )
    out = tmp_path / "thumb.png"
    res = runner.invoke(
        cli.app,
        ["tracker", "attachments", "thumbnail", "JUNE-2", "4159", "--output", str(out)],
    )
    assert res.exit_code == 0
    assert out.read_bytes() == b"\x89PNGthumb"
