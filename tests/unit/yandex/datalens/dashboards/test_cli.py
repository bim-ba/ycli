"""`datalens dashboards`: a body that comes from a file."""

import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.unit.yandex.datalens.dashboards.cases import CHANGE, NEW
from ycli.cli.errors import format_cli_error

DRY = ["-o", "json", "--dry-run", "datalens", "dashboards"]


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def _planned(*argv: str) -> dict:
    result = CliRunner().invoke(cli.app, [*DRY, *argv])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)["body"]


def test_a_dashboard_is_created_and_saved_from_a_file(api, tmp_path):
    """What a dashboard holds is far too large for a command line."""
    new = tmp_path / "new.json"
    new.write_text(json.dumps({"entry": NEW}), encoding="utf-8")
    assert _planned("create", "--body-file", str(new)) == {"entry": NEW}
    change = tmp_path / "change.json"
    change.write_text(json.dumps({"entry": CHANGE, "lockToken": "lock-1"}), encoding="utf-8")
    # A field of the request beside `entry` reaches it from the file, and a flag lies over it.
    assert _planned("update", "--mode", "save", "--body-file", str(change)) == {
        "entry": CHANGE,
        "mode": "save",
        "lockToken": "lock-1",
    }
    over = _planned("update", "--mode", "save", "--body-file", str(change), "--lock-token", "l2")
    assert over["lockToken"] == "l2"


@pytest.mark.parametrize("argv", [["create"], ["update", "--mode", "save"]])
def test_a_request_with_no_entry_says_so(api, argv):
    result = CliRunner().invoke(cli.app, ["datalens", "dashboards", *argv])
    assert isinstance(result.exception, ValidationError) and api.calls == []
    assert "entry: is required" in format_cli_error(result.exception)
