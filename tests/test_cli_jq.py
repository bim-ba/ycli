"""``--jq`` — a jq filter over a command's JSON result, printed like ``jq -r``."""

import sys

import pytest
import typer
from pydantic import BaseModel
from typer.testing import CliRunner

from tests.hosts import TRACKER_BASE
from ycli.cli.app import app
from ycli.cli.output import BinaryResult, ExitWith, OutputFormat, check_jq, render

runner = CliRunner()


class _Issue(BaseModel):
    key: str
    votes: int
    tags: list[str]
    note: str | None = None


ISSUE = _Issue(key="DE-1", votes=3, tags=["a", "ü"])


@pytest.mark.parametrize(
    ("expression", "printed"),
    [
        (".key", "DE-1\n"),  # a string prints raw: the "value mode"
        (".votes", "3\n"),
        (".tags", '["a", "ü"]\n'),  # anything else is compact JSON, non-ASCII kept
        (".note", "null\n"),
        (".key, .votes", "DE-1\n3\n"),  # one result per line
        (".tags[]", "a\nü\n"),
        ("empty", ""),
    ],
)
def test_the_filter_runs_over_the_json_form(capsys, expression, printed):
    render(ISSUE, OutputFormat.json, expression)
    assert capsys.readouterr().out == printed


def test_auto_format_is_json_so_it_accepts_a_filter(capsys):
    render(ISSUE, OutputFormat.auto, ".key")
    assert capsys.readouterr().out == "DE-1\n"


@pytest.mark.parametrize("output_format", [OutputFormat.yaml, OutputFormat.pretty])
def test_a_filter_with_a_non_json_format_is_a_usage_error(output_format):
    with pytest.raises(typer.BadParameter, match="cannot be combined"):
        render(ISSUE, output_format, ".key")


def test_a_program_that_does_not_compile_is_a_usage_error():
    with pytest.raises(typer.BadParameter, match="not a valid jq program"):
        render(ISSUE, OutputFormat.json, ".key |")


def test_a_runtime_jq_error_exits_1_and_prints_nothing(capsys):
    with pytest.raises(typer.Exit) as caught:
        render(ISSUE, OutputFormat.json, '.key, error("boom")')
    assert caught.value.exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "boom" in captured.err


@pytest.mark.parametrize("result", ["# page", 7, BinaryResult(b"x")])
def test_a_result_that_is_not_a_model_has_nothing_to_filter(result):
    with pytest.raises(typer.BadParameter, match="nothing to filter"):
        render(result, OutputFormat.json, ".x")


def test_a_command_that_returns_nothing_prints_nothing_even_with_a_filter(capsys):
    render(None, OutputFormat.json, ".x")
    assert capsys.readouterr().out == ""


def test_an_exit_with_result_is_filtered_before_exiting(capsys):
    with pytest.raises(typer.Exit) as caught:
        render(ExitWith(ISSUE, exit_code=3), OutputFormat.json, ".key")
    assert caught.value.exit_code == 3
    assert capsys.readouterr().out == "DE-1\n"


def test_a_missing_jq_package_is_a_usage_error_that_says_how_to_install(monkeypatch):
    monkeypatch.setitem(sys.modules, "jq", None)  # `import jq` now raises ImportError
    with pytest.raises(typer.BadParameter, match=r"pip install jq"):
        check_jq(".key", OutputFormat.json)


def test_the_root_option_filters_a_real_command(api):
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice", "uid": 7})
    result = runner.invoke(app, ["--jq", ".login", "tracker", "me", "get"])
    assert result.exit_code == 0, result.output
    assert result.stdout == "alice\n"


@pytest.mark.parametrize(
    ("args", "code"),
    [
        (["--jq", ".login |", "tracker", "me", "get"], 2),
        (["-o", "yaml", "--jq", ".login", "tracker", "me", "get"], 2),
    ],
)
def test_a_bad_filter_is_a_usage_error_from_the_command_line(api, args, code):
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice"})
    result = runner.invoke(app, args)
    assert result.exit_code == code
