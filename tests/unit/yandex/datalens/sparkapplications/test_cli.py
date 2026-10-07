"""`datalens sparkapplications create`: the kind comes from a flag, a field or the file."""

import json

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from pydantic import RootModel, ValidationError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from ycli.cli.errors import format_cli_error
from ycli.yandex.datalens.schemas.spark_applications import (
    CreateSparkApplicationArgsVariant1 as Variant1,
)
from ycli.yandex.datalens.schemas.spark_applications import (
    CreateSparkApplicationArgsVariant2 as Variant2,
)
from ycli.yandex.datalens.schemas.spark_applications import (
    CreateSparkApplicationArgsVariant3 as Variant3,
)
from ycli.yandex.datalens.sparkapplications.models import SparkApplicationCreate

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


ONE_KIND = (
    "The request cannot be built:\n"
    "  body: give exactly one of: sparkApplication, pysparkApplication, sparkConnectApplication"
)
BODIES = {
    "no kind": {"clusterId": "sc1"},
    "two kinds": {"clusterId": "sc1", "sparkApplication": {}, "pysparkApplication": {}},
    "a mistyped key": {"clusterId": "sc1", "pysparkApplication": {}, "nmae": "x"},
}


@pytest.mark.parametrize(
    "kinds",
    [[], ["--spark-application", "{}", "--pyspark-application", "{}"]],
    ids=["no kind", "two kinds"],
)
def test_an_application_of_no_kind_or_of_two_is_refused_once_before_sending(api, kinds):
    """#459: one line that names the three fields, not one per generated class."""
    result = CliRunner().invoke(cli.app, [*DRY, *kinds])
    assert isinstance(result.exception, ValidationError)
    assert format_cli_error(result.exception) == ONE_KIND
    assert api.calls == []


def test_a_mistyped_key_is_named_once_under_the_kind_given(api):
    result = CliRunner().invoke(cli.app, [*DRY, "--pyspark-application", "{}", "-F", "nmae=x"])
    assert isinstance(result.exception, ValidationError)
    assert format_cli_error(result.exception) == (
        "The request cannot be built:\n  pysparkApplication.nmae: Extra inputs are not permitted"
    )


@pytest.mark.parametrize(
    ("case", "lines"), [("no kind", 3), ("two kinds", 5), ("a mistyped key", 7)]
)
def test_without_the_mark_every_member_of_the_union_answers(case, lines):
    """The defect, on the same generated members: 3 to 7 lines, each under ``…VariantN``."""
    with pytest.raises(ValidationError) as refused:
        RootModel[Variant1 | Variant2 | Variant3].model_validate(BODIES[case])
    said = format_cli_error(refused.value).splitlines()[1:]
    assert len(said) == lines
    assert all(line.strip().startswith("CreateSparkApplicationArgsVariant") for line in said)
    with pytest.raises(ValidationError) as marked:
        SparkApplicationCreate.model_validate(BODIES[case])
    assert len(marked.value.errors()) == 1


async def test_the_tool_refuses_an_application_of_no_kind_once():
    async with Client(mcp) as client:
        with pytest.raises(ToolError) as refused:
            await client.call_tool("datalens_sparkapplications_create", {"body": BODIES["no kind"]})
    assert str(refused.value) == (
        "The arguments do not fit the tool:\n"
        "  body: give exactly one of: sparkApplication, pysparkApplication, sparkConnectApplication"
    )
