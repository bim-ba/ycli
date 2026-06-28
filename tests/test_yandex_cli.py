"""TDD for the `yandex` CLI — tracker group smoke test + forms group smoke test."""

from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

import ycli.cli as cli
from ycli.context import AppContext
from ycli.output import OutputFormat, PrettyStrategy

pytestmark = pytest.mark.integration

runner = CliRunner()


# ---------------------------------------------------------------------------
# Tracker CLI smoke tests
# ---------------------------------------------------------------------------


def test_app_has_tracker_issues_group():
    res = runner.invoke(cli.app, ["tracker", "issues", "--help"])
    assert res.exit_code == 0
    assert "get" in res.stdout and "create" in res.stdout


def test_app_has_forms_surveys_group():
    res = runner.invoke(cli.app, ["forms", "surveys", "--help"])
    assert res.exit_code == 0
    assert "list" in res.stdout and "get" in res.stdout


def test_mcp_subcommand_launches_server(monkeypatch):
    """`ycli mcp` resolves the optional MCP server and runs it."""
    calls: list[str] = []
    monkeypatch.setattr("ycli.mcp.main", lambda: calls.append("ran"))
    res = runner.invoke(cli.app, ["mcp"])
    assert res.exit_code == 0
    assert calls == ["ran"]


def test_mcp_command_registered_from_launcher():
    from typer.main import get_command

    names = get_command(cli.app).commands  # click Group.commands maps name -> Command
    assert "mcp" in names


def test_appcontext_strategy_and_retrieval():
    app = AppContext(output_format=OutputFormat.pretty)
    assert app.output_format is OutputFormat.pretty
    assert isinstance(app.strategy, PrettyStrategy)
    # from_typer_context just returns ctx.obj (set by the root callback)
    assert AppContext.from_typer_context(SimpleNamespace(obj=app)) is app


def test_completion_is_enabled():
    """Shell completion is enabled: the completion options are registered on the root app.

    Checked via the resolved Click command's params (width-independent) rather than the
    rendered --help text, which rich truncates the option name on a narrow terminal.
    """
    from typer.main import get_command

    params = {p.name for p in get_command(cli.app).params}
    assert "install_completion" in params
    assert "show_completion" in params
