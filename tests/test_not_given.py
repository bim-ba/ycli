"""An option or tool parameter that is not given is ``None``; an explicit value is sent."""

import ast
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from typer.testing import CliRunner

import ycli.cli.app as cli
from tests.full_server import mcp
from tests.hosts import FORMS_BASE, TRACKER_BASE

SRC = Path(__file__).resolve().parents[1] / "src" / "ycli"


def _sentinel_defaults(source: str) -> list[str]:
    """Parameters of ``source`` whose default is ``""`` or ``0``, as ``function.parameter``."""
    found = []
    for function in ast.walk(ast.parse(source)):
        if not isinstance(function, ast.FunctionDef):
            continue
        arguments = function.args
        positional = arguments.args[len(arguments.args) - len(arguments.defaults) :]
        pairs = [
            *zip(positional, arguments.defaults, strict=True),
            *zip(arguments.kwonlyargs, arguments.kw_defaults, strict=True),
        ]
        found += [
            f"{function.name}.{argument.arg}"
            for argument, default in pairs
            if isinstance(default, ast.Constant)
            and not isinstance(default.value, bool)
            and default.value in ("", 0)
        ]
    return found


def test_no_command_or_tool_spells_not_given_as_an_empty_string_or_zero():
    """A default of ``""`` or ``0`` makes the explicit value unsendable; ``None`` says not given."""
    modules = [*SRC.rglob("cli.py"), *SRC.rglob("mcp.py"), SRC / "cli" / "api.py"]
    offenders = {
        str(module.relative_to(SRC)): found
        for module in modules
        if (found := _sentinel_defaults(module.read_text(encoding="utf-8")))
    }
    assert offenders == {}


def test_the_default_check_bites():
    source = 'def update(key, name="", count=0, flag=False, *, text="", limit=None): ...'
    assert _sentinel_defaults(source) == ["update.name", "update.count", "update.text"]


def test_an_empty_string_is_sent_and_an_absent_option_is_not(api):
    api.add("PATCH", f"{FORMS_BASE}/surveys/s1", json={"id": "s1"})
    runner = CliRunner()
    res = runner.invoke(cli.app, ["forms", "surveys", "update", "s1", "--name", ""])
    assert res.exit_code == 0, res.output
    assert api.body() == {"name": ""}
    res = runner.invoke(cli.app, ["forms", "surveys", "update", "s1", "--language", "en"])
    assert res.exit_code == 0, res.output
    assert api.body() == {"language": "en"}


def test_a_zero_response_cap_is_sent(api):
    api.add("PATCH", f"{FORMS_BASE}/surveys/s1", json={"id": "s1"})
    res = CliRunner().invoke(cli.app, ["forms", "surveys", "update", "s1", "--max-count", "0"])
    assert res.exit_code == 0, res.output
    assert api.body() == {"max_count": 0}


def test_a_zero_limit_is_a_usage_error(api):
    res = CliRunner().invoke(cli.app, ["tracker", "queues", "list", "--limit", "0"])
    assert res.exit_code == 2
    assert "--limit" in res.output
    assert api.calls == []


async def test_a_tool_sends_an_empty_filter_value_and_leaves_out_an_absent_one(api):
    api.add("POST", f"{TRACKER_BASE}/issues/_search", json=[])
    async with Client(mcp) as client:
        await client.call_tool("tracker_issues_list", {"queue": "", "status": "open"})
    assert api.body() == {"filter": {"queue": "", "status": "open"}}


async def test_a_tool_refuses_a_zero_limit(api):
    async with Client(mcp) as client:
        with pytest.raises(ToolError, match="limit"):
            await client.call_tool("tracker_queues_list", {"limit": 0})
    assert api.calls == []


@pytest.mark.parametrize(
    ("flags", "sent"),
    [(["--no-show-all"], {"show_all": "false"}), (["--show-all"], {"show_all": "true"}), ([], {})],
    ids=["an explicit false", "an explicit true", "not given"],
)
def test_a_boolean_option_is_sent_as_given_and_left_out_when_absent(api, flags, sent):
    """#296: ``--x`` and ``--no-x`` both reach the API; neither does when the option is absent."""
    api.add("GET", f"{FORMS_BASE}/surveys", json={"result": []})
    res = CliRunner().invoke(cli.app, ["forms", "surveys", "list", *flags])
    assert res.exit_code == 0, res.output
    assert {
        key: value for key, value in api.calls[0].url.params.items() if key == "show_all"
    } == sent


def test_an_explicit_false_reaches_the_body_of_a_bulk_change(api):
    api.add("POST", f"{TRACKER_BASE}/bulkchange/_update", json={"status": "FAILED"})
    argv = ["tracker", "issues", "update-bulk", "--issue", "TEST-1", "-F", "priority=minor"]
    res = CliRunner().invoke(cli.app, [*argv, "--no-notify"])
    assert res.exit_code == 0, res.output
    assert api.body()["notify"] is False
    assert api.calls[0].url.params["notify"] == "false"


async def test_a_tool_sends_an_explicit_false(api):
    api.add("GET", f"{FORMS_BASE}/surveys", json={"result": []})
    async with Client(mcp) as client:
        await client.call_tool("forms_surveys_list", {"show_all": False})
    assert api.calls[0].url.params["show_all"] == "false"
