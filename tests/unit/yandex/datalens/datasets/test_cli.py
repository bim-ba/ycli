"""`datalens datasets`: a body that comes from a file, and the fields under `data`."""

import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.unit.yandex.datalens.datasets.cases import CONTENT, CREATED, DS, WB
from ycli.cli.errors import format_cli_error

RPC = "https://api.datalens.tech/rpc/"


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def _planned(*argv: str) -> dict:
    result = CliRunner().invoke(cli.app, ["-o", "json", "--dry-run", "datalens", "datasets", *argv])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)["body"]


def test_a_dataset_is_created_from_a_file_with_flags_over_it(api, tmp_path):
    """What a dataset holds is too large for a command line: it comes from --body-file."""
    body = tmp_path / "dataset.json"
    body.write_text(json.dumps({"name": "From file", "dataset": CONTENT}), encoding="utf-8")
    api.add("POST", RPC + "createDataset", json=CREATED)
    argv = ["create", "--body-file", str(body), "--name", "Sales", "--workbook-id", WB]
    result = CliRunner().invoke(cli.app, ["-o", "json", "datalens", "datasets", *argv])
    assert result.exit_code == 0, result.output
    assert api.body() == {"name": "Sales", "workbook_id": WB, "dataset": CONTENT}


def test_a_dataset_with_nothing_to_hold_is_refused_before_anything_is_sent(api):
    result = CliRunner().invoke(cli.app, ["datalens", "datasets", "create", "--name", "Sales"])
    assert isinstance(result.exception, ValidationError)
    assert "dataset: is required" in format_cli_error(result.exception)
    assert api.calls == []


def test_the_data_of_a_request_may_come_from_field_flags(api):
    planned = _planned("update", DS, "-F", "data[dataset][description]=Q1")
    assert planned == {"datasetId": DS, "data": {"dataset": {"description": "Q1"}}}


def test_validate_is_a_read_and_runs_under_dry_run(api):
    """It saves nothing, so --dry-run does not stop it."""
    api.add("POST", RPC + "validateDataset", json={"code": "OK"})
    argv = ["validate", DS, "-F", "data[dataset][description]=Q1"]
    result = CliRunner().invoke(cli.app, ["-o", "json", "--dry-run", "datalens", "datasets", *argv])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["code"] == "OK"
    assert api.body() == {"datasetId": DS, "data": {"dataset": {"description": "Q1"}}}


def test_an_update_with_no_data_is_refused_before_anything_is_sent(api):
    result = CliRunner().invoke(cli.app, ["datalens", "datasets", "update", DS])
    assert isinstance(result.exception, ValidationError)
    assert api.calls == []


def test_a_field_of_the_request_given_in_a_file_or_by_a_field_flag_reaches_it(api, tmp_path):
    """Measured defect: `workbookId` from --body-file and -F was dropped by `update`."""
    data = {"dataset": {"description": "Q1"}}
    body = tmp_path / "save.json"
    body.write_text(json.dumps({"data": data, "workbookId": WB}), encoding="utf-8")
    assert _planned("update", DS, "--body-file", str(body)) == {
        "datasetId": DS,
        "data": data,
        "workbookId": WB,
    }
    by_field = ["-F", "workbookId=wb2", "-F", "data[dataset][description]=Q1"]
    assert _planned("update", DS, *by_field)["workbookId"] == "wb2"
    # A flag lies over the file.
    assert _planned("update", DS, "--body-file", str(body), "--workbook-id", "wb3") == {
        "datasetId": DS,
        "data": data,
        "workbookId": "wb3",
    }


def test_validate_takes_the_fields_of_its_request_from_a_file_too(api, tmp_path):
    body = tmp_path / "try.json"
    given = {"data": {"dataset": {"description": "Q1"}}, "workbookId": WB, "bindedDatasetId": "d2"}
    body.write_text(json.dumps(given), encoding="utf-8")
    api.add("POST", RPC + "validateDataset", json={"code": "OK"})
    result = CliRunner().invoke(
        cli.app, ["-o", "json", "datalens", "datasets", "validate", DS, "--body-file", str(body)]
    )
    assert result.exit_code == 0, result.output
    assert api.body() == {"datasetId": DS, **given}


def test_a_field_that_is_not_of_the_request_is_refused_not_dropped(api):
    result = CliRunner().invoke(
        cli.app, ["datalens", "datasets", "update", DS, "-F", "data[x]=1", "-F", "workbok=w"]
    )
    assert isinstance(result.exception, ValidationError)
    assert "workbok" in format_cli_error(result.exception) and api.calls == []
