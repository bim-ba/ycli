"""Deprecated CLI aliases: Typer 0.26 has no alias feature, so a renamed command registers twice.

Put :func:`deprecated_alias` above the command's own decorator; the old name keeps working, is
hidden from ``--help`` and prints Click's deprecation warning on stderr::

    @deprecated_alias(app, "edit")
    @app.command()
    def update(...): ...

Both registrations share one callback, so dependency injection and the global options
(:mod:`ycli.cli.inject`) apply to the alias like to any command.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import typer
    from typer.models import CommandFunctionType


def deprecated_alias(
    app: typer.Typer, name: str
) -> Callable[[CommandFunctionType], CommandFunctionType]:
    """Register the decorated command under ``name`` as well, hidden and deprecated.

    Example:
        >>> import typer
        >>> app = typer.Typer()
        >>> @deprecated_alias(app, "edit")
        ... @app.command()
        ... def update() -> None: ...
        >>> [
        ...     (command.name, command.hidden, command.deprecated)
        ...     for command in app.registered_commands
        ... ]
        [(None, False, False), ('edit', True, True)]
    """
    return app.command(name, hidden=True, deprecated=True)
