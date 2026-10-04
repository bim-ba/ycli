"""`tracker entities` CLI: arguments refused before any request, and the download to a file."""

import re

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.hosts import TRACKER_BASE as BASE


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["checklists", "update", "project", "655f", "--item", "no-separator"], "must be id=text"),
    ],
)
def test_bad_arguments_fail_before_sending(argv, message):
    res = CliRunner().invoke(cli.app, ["tracker", "entities", *argv])
    assert res.exit_code == 2
    # CI forces colour: drop the escape codes and the panel border before matching the words.
    plain = re.sub(r"[│╭╮╰╯─]", " ", re.sub(r"\x1b\[[0-9;]*m", "", res.output))
    assert message in " ".join(plain.split())


def test_order_asc_without_order_by_is_sent_as_given(api):
    api.add("POST", f"{BASE}/entities/project/_search", json={"hits": 0, "values": []})
    res = CliRunner().invoke(cli.app, ["tracker", "entities", "search", "project", "--order-asc"])
    assert res.exit_code == 0
    assert api.body() == {"orderAsc": True}


def test_set_direct_permissions_with_nothing_to_change_sends_an_empty_body(api):
    api.add("PATCH", f"{BASE}/entities/project/655f/permissions", json={})
    res = CliRunner().invoke(
        cli.app, ["tracker", "entities", "set-direct-permissions", "project", "655f"]
    )
    assert res.exit_code == 0
    assert api.body() == {}


def test_attachment_download_writes_the_bytes_to_output(api, tmp_path):
    api.add("GET", f"{BASE}/attachments/5/flowers.jpg", content=b"\xff\xd8jpg")
    out = tmp_path / "flowers.jpg"
    res = CliRunner().invoke(
        cli.app,
        ["tracker", "entities", "attachments", "download", "5", "flowers.jpg", "-O", str(out)],
    )
    assert res.exit_code == 0, res.output
    assert out.read_bytes() == b"\xff\xd8jpg"
