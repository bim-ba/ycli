"""The CLI's gate on writes: ``AppContext`` hands :class:`SendGuard` to every client it builds.

The core calls it once per endpoint, before the first HTTP attempt, with the endpoint's effect
and the request about to go out (``ycli.yandex.core.session.BeforeSend``), so no command needs
its own confirmation or dry-run code:

- with ``--dry-run`` a write is not sent: the guard raises :class:`DryRunPlanned`, which the
  command wrapper turns into the command's result — the request it would have sent;
- an operation that destroys data asks first, unless ``--yes`` was given: on a terminal it
  prompts on stderr, and a declined prompt aborts (exit 1); with no terminal to ask it fails as a
  usage error (exit 2) that says to pass ``--yes``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import typer

from ycli.cli.exit_codes import ExitCode
from ycli.cli.planned_request import PlannedRequest
from ycli.yandex.core.session import shown

if TYPE_CHECKING:
    from collections.abc import Mapping

    import httpx2

    from ycli.yandex.core.endpoint import Effect


def attended() -> bool:
    """Whether a person can be asked: stdin and stdout are both terminals (not a pipe or a CI)."""
    # violation(arch-4): only asks whether stdout is a terminal; it writes nothing
    return sys.stdin.isatty() and sys.stdout.isatty()


class DryRunPlanned(Exception):  # noqa: N818  # a signal that stops the command, not an error
    """Stops a command at its first write under ``--dry-run``; ``plan`` is what it would send."""

    def __init__(self, plan: PlannedRequest) -> None:
        super().__init__(f"{plan.method} {plan.url}")
        self.plan = plan


@dataclass(frozen=True)
class SendGuard:
    """The ``before_send`` hook of the CLI; ``options`` is the root's parsed global options.

    ``options`` is read at call time, so a ``--yes`` or ``--dry-run`` given after the subcommand
    (written into the root state by the leaf) counts. Reads pass untouched.
    """

    options: Mapping[str, Any]

    def __call__(self, effect: Effect, request: httpx2.Request) -> None:
        """Let a read pass, stop a write under ``--dry-run``, confirm a delete without ``--yes``."""
        if effect == "read":
            return
        if self.options.get("dry_run"):
            raise DryRunPlanned(PlannedRequest.of(request))
        if effect == "destructive" and not self.options.get("yes"):
            self._confirm(f"{request.method} {shown(request.url)} — this deletes data.")

    def _confirm(self, what: str) -> None:
        if not attended():
            typer.secho(
                f"{what} Pass --yes to confirm; there is no terminal to ask on.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(ExitCode.USAGE)
        typer.confirm(f"{what} Continue?", abort=True, err=True)
