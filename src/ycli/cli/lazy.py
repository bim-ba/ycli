"""Lazy sub-apps: the root CLI imports a service's commands only when that service runs.

``ycli --version`` or ``ycli wiki pages get`` used to import every service's clients, models
and commands first (~1.3 s). The root group now lists each sub-app by name and help text and
loads its Typer app on first use, so a command pays only for the service it calls.

Kill-criterion: replace with PEP 810 ``lazy import`` once Python 3.15 is the floor (#113).
"""

from __future__ import annotations

from dataclasses import dataclass
from pkgutil import resolve_name
from typing import TYPE_CHECKING, Any

import typer.main
from typer.core import TyperGroup

if TYPE_CHECKING:
    # Typer vendors Click and exposes no public alias for these types.
    from typer import _click


@dataclass(frozen=True, slots=True)
class SubApp:
    """A sub-app the root can list without importing it: ``app`` is ``"module:attribute"``.

    ``command`` says the sub-app is one command (``ycli api PATH``), not a group of them.
    """

    name: str
    help: str
    app: str
    command: bool = False


class LazyGroup(TyperGroup):
    """Stands in for one sub-app: ``--help`` lists it from :class:`SubApp`, use loads it.

    The sub-app is a group, or a single command when its :class:`SubApp` says so.
    """

    def __init__(self, sub_app: SubApp) -> None:
        super().__init__(name=sub_app.name, help=sub_app.help)
        self._sub_app = sub_app
        self._loaded: _click.Command | None = None

    def load(self) -> _click.Command:
        """The real Click group or command, built once, with its dependencies injectable."""
        if self._loaded is None:
            from ycli.cli.inject import inject_dependencies

            app: typer.Typer = resolve_name(self._sub_app.app)
            inject_dependencies(app)
            if self._sub_app.command:  # a command keeps its docstring as its help
                self._loaded = typer.main.get_command(app)
            else:
                self._loaded = typer.main.get_group(app)
                self._loaded.help = self._sub_app.help
        return self._loaded

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: _click.Context | None = None,
        **extra: Any,
    ) -> _click.Context:
        """Build the context from the loaded group or command."""
        return self.load().make_context(info_name, args, parent=parent, **extra)

    def list_commands(self, ctx: _click.Context) -> list[str]:
        """The loaded group's command names; a single command has none."""
        loaded = self.load()
        return loaded.list_commands(ctx) if isinstance(loaded, TyperGroup) else []

    def get_command(self, ctx: _click.Context, cmd_name: str) -> _click.Command | None:
        """The named command of the loaded group; a single command has none."""
        loaded = self.load()
        return loaded.get_command(ctx, cmd_name) if isinstance(loaded, TyperGroup) else None


class RootGroup(TyperGroup):
    """The ``ycli`` group: every :class:`SubApp` in ``sub_apps``, each loaded on first use.

    The stand-ins are ordinary entries of ``commands``, so listing, dispatch and Typer's
    "did you mean" suggestions work unchanged.
    """

    sub_apps: tuple[SubApp, ...] = ()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.commands.update({sub_app.name: LazyGroup(sub_app) for sub_app in self.sub_apps})
