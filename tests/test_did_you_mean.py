"""Unknown subcommands suggest the closest valid one."""

from __future__ import annotations

from typer.testing import CliRunner

from ycli.cli import app

_RUNNER = CliRunner()


def test_root_typo_suggests():
    result = _RUNNER.invoke(app, ["trackr"])
    assert result.exit_code != 0
    assert "did you mean 'tracker'" in result.output.lower()


def test_domain_typo_suggests():
    result = _RUNNER.invoke(app, ["wiki", "pagez"])
    assert result.exit_code != 0
    assert "did you mean 'pages'" in result.output.lower()


def test_correct_command_unaffected():
    result = _RUNNER.invoke(app, ["--help"])
    assert result.exit_code == 0
