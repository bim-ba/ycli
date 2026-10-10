"""inject_dependencies skips registrations that have nothing to wrap."""

import pytest
import typer
from typer.models import CommandInfo, TyperInfo
from typer.testing import CliRunner

from ycli.cli.app import app as root
from ycli.cli.inject import NO_NAME, inject_dependencies


def test_registrations_without_a_callback_or_an_app_are_left_alone():
    app = typer.Typer()
    app.registered_commands.append(CommandInfo(name="empty", callback=None))
    app.registered_groups.append(TyperInfo(typer_instance=None, name="hollow"))
    inject_dependencies(app)
    assert app.registered_commands[0].callback is None
    assert app.registered_groups[0].typer_instance is None


@pytest.mark.parametrize(
    "argv",
    [
        # Typer holds the choice as the text given until the command's own callback runs.
        ["--format", "name", "forms", "access", "list", "s1"],
        ["forms", "access", "list", "s1", "-o", "name"],
    ],
)
def test_name_is_refused_before_the_command_runs_where_the_result_has_no_identifier(api, argv):
    result = CliRunner().invoke(root, argv)
    assert result.exit_code == 2
    assert NO_NAME in " ".join(result.output.replace("│", " ").split())
    assert api.calls == []
