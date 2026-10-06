"""`datalens connections`: a body from a file, and a secret that is not printed."""

import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.unit.yandex.datalens.connections.cases import NEW, NEW_FILE
from ycli.cli.errors import format_cli_error

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


@pytest.mark.parametrize(
    "argv",
    [
        ["update", "con1", "--data", '{"host": "db2", "password": "typed"}'],
        ["update", "con1", "-F", "data[host]=db2", "-F", "data[password]=typed"],
    ],
)
def test_the_fields_to_change_come_from_data_or_from_field_flags(api, argv):
    assert _planned(*argv) == {"connectionId": "con1", "data": {"host": "db2", "password": "***"}}


def test_a_connection_with_no_body_is_refused_before_anything_is_sent(api):
    """The body is a union by ``type``: without one there is nothing to build."""
    result = CliRunner().invoke(cli.app, ["datalens", "connections", "create"])
    assert isinstance(result.exception, ValidationError)
    assert "needs `type` to tell which kind it is" in format_cli_error(result.exception)
    assert api.calls == []


def test_a_kind_that_does_not_exist_is_refused_without_quoting_the_body(api):
    result = CliRunner().invoke(
        cli.app, ["datalens", "connections", "create", "--body-file", NEW_FILE, "-F", "type=nope"]
    )
    assert isinstance(result.exception, ValidationError)
    said = format_cli_error(result.exception) + str(result.exception)
    assert "nope" in said and NEW["password"] not in said
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
