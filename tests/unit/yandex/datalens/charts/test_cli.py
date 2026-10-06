"""`datalens charts data-get`: what a chart that gives no data answers with."""

import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from ycli.cli.errors import format_cli_error
from ycli.yandex.errors import YandexClientError

DATA = "https://api.datalens.tech/rpc/getChartData"
# Two refusals measured live (2026-10-06): a source that cannot be reached, and a pivot table.
UNREACHABLE = {"code": "ERR.CHARTS.DATA_FETCHING_ERROR", "message": "Failed to retrieve chart data"}
PIVOT = {
    "code": "UNSUPPORTED_CHART_DATA_VISUALIZATION",
    "message": "Data retrieval is not supported for this visualization type. "
    "Pivot tables are not supported.",
}


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


@pytest.mark.parametrize(("status", "body"), [(427, UNREACHABLE), (422, PIVOT)])
def test_a_chart_that_gives_no_data_says_why(api, status, body):
    """427 is a status of DataLens's own: it is an error of the request like any other 4xx."""
    api.add("POST", DATA, json=body, status=status)
    result = CliRunner().invoke(cli.app, ["datalens", "charts", "data-get", "ch1"])
    assert result.exit_code == 1
    assert isinstance(result.exception, YandexClientError) and result.exception.status == status
    assert f"{body['code']}: {body['message']}" in format_cli_error(result.exception)


def test_an_error_that_is_only_the_word_error_reaches_the_user(api):
    """Measured on ``createQLChart``: the body is ``{"error": "..."}`` and nothing else."""
    said = "Cannot read properties of undefined (reading 'entryId')"
    api.add("POST", "https://api.datalens.tech/rpc/createQLChart", json={"error": said}, status=400)
    argv = ["charts", "ql", "create", "--template", "ql", "--data", "{}"]
    result = CliRunner().invoke(cli.app, ["datalens", *argv])
    assert isinstance(result.exception, YandexClientError)
    assert format_cli_error(result.exception).endswith(said)


def test_the_content_of_a_chart_comes_from_a_file_or_from_field_flags(api, tmp_path):
    """What a chart holds is too large for a command line."""
    body = tmp_path / "chart.json"
    body.write_text('{"data": {"sources": {"datasetsIds": ["ds1"]}}}', encoding="utf-8")
    dry = ["-o", "json", "--dry-run", "datalens", "charts"]
    planned = CliRunner().invoke(
        cli.app,
        [*dry, "wizard", "update", "ch1", "--mode", "save", "--body-file", str(body)],
    )
    assert planned.exit_code == 0, planned.output
    assert json.loads(planned.stdout)["body"]["data"] == {"sources": {"datasetsIds": ["ds1"]}}
    entry = CliRunner().invoke(
        cli.app,
        [*dry, "editor", "create", "-F", "entry[type]=table_node", "-F", "entry[name]=Top"],
    )
    assert entry.exit_code == 0, entry.output
    assert json.loads(entry.stdout)["body"] == {"entry": {"type": "table_node", "name": "Top"}}


def _planned(*argv: str) -> dict:
    dry = ["-o", "json", "--dry-run", "datalens", "charts"]
    result = CliRunner().invoke(cli.app, [*dry, *argv])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)["body"]


def test_a_field_of_the_request_given_in_a_file_or_by_a_field_flag_reaches_it(api, tmp_path):
    """Measured defect: `workbookId` and `name` from --body-file and -F were dropped silently."""
    data = {"sources": {"datasetsIds": ["ds1"]}}
    body = tmp_path / "chart.json"
    body.write_text(json.dumps({"data": data, "workbookId": "wb1", "name": "File"}), "utf-8")
    assert _planned("wizard", "create", "--body-file", str(body)) == {
        "data": data,
        "workbookId": "wb1",
        "name": "File",
    }
    # A flag lies over the file, and -F gives a field like the file does.
    over = _planned("wizard", "create", "--body-file", str(body), "--name", "Flag")
    assert over["name"] == "Flag" and over["workbookId"] == "wb1"
    by_field = ["-F", "workbookId=wb2", "-F", "name=Field", "--data", json.dumps(data)]
    assert _planned("wizard", "create", *by_field) == {
        "data": data,
        "workbookId": "wb2",
        "name": "Field",
    }
    ql = _planned("ql", "create", "--template", "ql", "--body-file", str(body))
    assert (ql["workbookId"], ql["name"]) == ("wb1", "File")


@pytest.mark.parametrize(
    "argv",
    [
        ["wizard", "update", "ch1", "--mode", "save"],
        ["wizard", "create", "--name", "Top"],
        ["ql", "update", "ch1", "--template", "ql", "--mode", "save"],
        ["editor", "create"],
    ],
)
def test_a_request_with_nothing_to_hold_says_which_field_it_lacks(api, argv):
    """Not `body: Input should be a valid dictionary`: the field that is missing is named."""
    result = CliRunner().invoke(cli.app, ["datalens", "charts", *argv])
    assert isinstance(result.exception, ValidationError) and api.calls == []
    said = format_cli_error(result.exception)
    assert "data: is required" in said or "entry: is required" in said
