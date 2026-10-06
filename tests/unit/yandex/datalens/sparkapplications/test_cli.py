"""`datalens sparkapplications create`: the kind comes from a flag, a field or the file."""

import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli

DRY = ["-o", "json", "--dry-run", "datalens", "sparkapplications", "create", "sc1"]


@pytest.fixture(autouse=True)
def signed_in(monkeypatch):
    """DataLens takes an IAM token and a Yandex Cloud organization."""
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN")
    monkeypatch.setenv("YANDEX_CLOUD_IAM_TOKEN", "t")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "c")


def test_a_flag_lies_over_a_field_and_a_field_over_the_file(api, tmp_path):
    body_file = tmp_path / "application.json"
    held = {"clusterId": "file", "name": "file", "pysparkApplication": {"args": ["file"]}}
    body_file.write_text(json.dumps(held))
    fields = ["-F", "name=field", "-F", "pysparkApplication[mainPythonFileUri]=s3a://b/job.py"]
    result = CliRunner().invoke(cli.app, [*DRY, "--body-file", str(body_file), *fields])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["body"] == {
        "clusterId": "sc1",
        "name": "field",
        "pysparkApplication": {"args": ["file"], "mainPythonFileUri": "s3a://b/job.py"},
    }
    assert api.calls == []


@pytest.mark.parametrize(
    "kinds",
    [[], ["--spark-application", "{}", "--pyspark-application", "{}"]],
    ids=["no kind", "two kinds"],
)
def test_an_application_of_no_kind_or_of_two_is_refused_before_sending(api, kinds):
    result = CliRunner().invoke(cli.app, [*DRY, *kinds])
    assert isinstance(result.exception, ValidationError)
    assert api.calls == []
