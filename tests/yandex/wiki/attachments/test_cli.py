"""TDD for `wiki attachments` CLI."""

import pytest
import responses
from typer.testing import CliRunner

import ycli.cli.app as cli

BASE = "https://api.wiki.yandex.net/v1"
runner = CliRunner()


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


@responses.activate
def test_attachments_list():
    responses.add(
        responses.GET,
        f"{BASE}/pages/42/attachments",
        json={"results": [{"name": "f.pdf", "size": 0, "mime_type": "application/pdf"}]},
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
