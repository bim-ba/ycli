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
    """A sub-app the root can list without importing it: ``app`` is ``"module:attribute"``."""

    name: str
    help: str
    app: str


class LazyGroup(TyperGroup):
    """Stands in for one sub-app: ``--help`` lists it from :class:`SubApp`, use loads it."""

    def __init__(self, sub_app: SubApp) -> None:
        super().__init__(name=sub_app.name, help=sub_app.help)
        self._sub_app = sub_app
        self._group: TyperGroup | None = None

    def load(self) -> TyperGroup:
        """The real Click group, built once, with its commands' dependencies injectable."""
        if self._group is None:
            from ycli.cli.inject import inject_dependencies

            app: typer.Typer = resolve_name(self._sub_app.app)
            inject_dependencies(app)
            self._group = typer.main.get_group(app)
            self._group.help = self._sub_app.help
        return self._group

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: _click.Context | None = None,
        **extra: Any,
    ) -> _click.Context:
        return self.load().make_context(info_name, args, parent=parent, **extra)

    def list_commands(self, ctx: _click.Context) -> list[str]:
        return self.load().list_commands(ctx)

    def get_command(self, ctx: _click.Context, cmd_name: str) -> _click.Command | None:
        return self.load().get_command(ctx, cmd_name)


class RootGroup(TyperGroup):
    """The ``ycli`` group: every :class:`SubApp` in ``sub_apps``, each loaded on first use.

    The stand-ins are ordinary entries of ``commands``, so listing, dispatch and Typer's
    "did you mean" suggestions work unchanged.
    """

    sub_apps: tuple[SubApp, ...] = ()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.commands.update({sub_app.name: LazyGroup(sub_app) for sub_app in self.sub_apps})
