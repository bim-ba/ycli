"""TDD for the `yandex` CLI — tracker group smoke test + forms group smoke test."""

import pytest
from typer.testing import CliRunner

import ycli.cli as cli

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
