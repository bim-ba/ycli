"""`tracker attachments download` / `thumbnail` write the raw bytes to --output."""

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE


@pytest.mark.parametrize(
    ("argv", "path"),
    [
        (
            ["download", "JUNE-2", "4159", "attachment.txt"],
            "issues/JUNE-2/attachments/4159/attachment.txt",
        ),
        (["thumbnail", "JUNE-2", "4159"], "issues/JUNE-2/thumbnails/4159"),
    ],
)
def test_download_writes_the_bytes_to_output(api, tmp_path, argv, path):
    api.add("GET", f"{BASE}/{path}", content=b"\x89PNGbytes")
    out = tmp_path / "file.bin"
    res = CliRunner().invoke(cli.app, ["tracker", "attachments", *argv, "--output", str(out)])
    assert res.exit_code == 0, res.output
    assert out.read_bytes() == b"\x89PNGbytes"
