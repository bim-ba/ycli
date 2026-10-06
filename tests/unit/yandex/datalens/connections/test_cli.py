"""`datalens connections`: a body from a file, and a secret that is not printed."""

import json

import pytest
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.unit.yandex.datalens.connections.cases import NEW, NEW_FILE

DRY = ["-o", "json", "--dry-run", "datalens", "connections"]


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


def test_a_dry_run_of_a_new_connection_does_not_print_its_password(api):
    """#388: the plan goes to a terminal and a CI log; the password of the file does not."""
    assert _planned("create", "--body-file", NEW_FILE) == {**NEW, "password": "***"}
    assert api.calls == []


def test_a_field_flag_lies_over_the_file_and_its_secret_is_masked_too(api):
    planned = _planned("create", "--body-file", NEW_FILE, "-F", "password=typed", "-F", "port=9440")
    assert planned == {**NEW, "password": "***", "port": 9440}


def test_a_secret_read_from_a_file_is_masked_in_a_dry_run_too(api, tmp_path):
    """#412: ``-F password=@file`` keeps the password off the command line and out of the plan."""
    held = tmp_path / "password.txt"
    held.write_text("from-a-file")
    planned = _planned("create", "--body-file", NEW_FILE, "-F", f"password=@{held}")
    assert planned == {**NEW, "password": "***"}
    assert api.calls == []


@pytest.mark.parametrize(
    "argv",
    [
        ["update", "con1", "--data", '{"host": "db2", "password": "typed"}'],
        ["update", "con1", "-F", "data[host]=db2", "-F", "data[password]=typed"],
    ],
)
def test_the_fields_to_change_come_from_data_or_from_field_flags(api, argv):
    assert _planned(*argv) == {"connectionId": "con1", "data": {"host": "db2", "password": "***"}}


def test_a_connection_with_no_kind_is_for_datalens_to_refuse(api):
    """#444: ycli sends a kind it does not know, so a body with no ``type`` goes out as well."""
    assert _planned("create", "-F", "name=x") == {"name": "x"}
    assert api.calls == []


def test_a_kind_the_document_does_not_know_goes_out_with_its_secret_masked(api):
    """#444: DataLens answers for a kind ycli does not know; a dry run still masks the password.

    Before, such a connection was refused by ycli before anything was sent.
    """
    planned = _planned("create", "--body-file", NEW_FILE, "-F", "type=nope")
    assert planned == {**NEW, "type": "nope", "password": "***"}
    assert api.calls == []


@pytest.mark.parametrize(
    ("argv", "rpc", "said"),
    [
        (["update", "con1", "--data", '{"host": "db2"}'], "updateConnection", "updated"),
        (["delete", "con1", "--yes"], "deleteConnection", "deleted"),
    ],
)
def test_a_write_answered_with_no_body_at_all_succeeds(api, argv, rpc, said):
    """Measured: both answer 200 with an empty body, which is no JSON; the write went through."""
    api.add("POST", f"https://api.datalens.tech/rpc/{rpc}", content=b"")
    result = CliRunner().invoke(cli.app, ["-o", "json", "datalens", "connections", *argv])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"ok": True, "detail": f"{said} connection con1"}
