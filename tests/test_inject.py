"""inject_dependencies skips registrations that have nothing to wrap."""

import typer
from typer.models import CommandInfo, TyperInfo

from ycli.cli.inject import inject_dependencies


def test_registrations_without_a_callback_or_an_app_are_left_alone():
    app = typer.Typer()
    app.registered_commands.append(CommandInfo(name="empty", callback=None))
    app.registered_groups.append(TyperInfo(typer_instance=None, name="hollow"))
    inject_dependencies(app)
    assert app.registered_commands[0].callback is None
    assert app.registered_groups[0].typer_instance is None
