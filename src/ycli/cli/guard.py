"""The CLI's gate on writes: ``AppContext`` hands :class:`SendGuard` to every client it builds.

The core calls it once per endpoint, before the first HTTP attempt, with the endpoint's effect
and the request about to go out (``ycli.yandex.core.session.BeforeSend``), so no command needs
its own confirmation or dry-run code:

- with ``--dry-run`` a write is not sent: the guard raises :class:`DryRunPlanned`, which the
  command wrapper turns into the command's result — the request it would have sent;
- an operation that destroys data asks first, unless ``--yes`` was given: on a terminal it
  prompts on stderr, and a declined prompt aborts (exit 1); with no terminal to ask it fails as a
  usage error (exit 2) that says to pass ``--yes``;
- ``--body-file`` and ``-F`` reach the body of any command: the guard lays them under what the
  command built, so a field with no flag of its own can still be sent.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import httpx2
import typer

from ycli.cli.exit_codes import ExitCode
from ycli.cli.global_options import NO_BODY
from ycli.cli.planned_request import PlannedRequest
from ycli.yandex.core.session import shown

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ycli.cli.body_fields import CallerFields
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


@dataclass
class SendGuard:
    """The ``before_send`` hook of the CLI; ``options`` is the root's parsed global options.

    ``options`` is read at call time, so a ``--yes`` or ``--dry-run`` given after the subcommand
    (written into the root state by the leaf) counts. Reads pass untouched.

    ``--body-file`` and ``-F`` go into the first request of the command, under what the command
    built from its flags: file, then ``-F``, then the flags, the later the stronger.
    """

    options: Mapping[str, Any]
    fields: CallerFields

    def __call__(self, effect: Effect, request: httpx2.Request) -> httpx2.Request:
        """Add the caller's fields, then pass a read, plan a write, confirm a delete.

        Args:
            effect: What the endpoint does to the server.
            request: The request about to go out.

        Returns:
            The request to send: with the caller's fields in its body when any were given.

        Raises:
            DryRunPlanned: A write under ``--dry-run``; it carries the request not sent.
        """
        # Imported here: the core is loaded by the time a request is about to go.
        from ycli.yandex.core.endpoint import Effect

        request = self._with_fields(request)
        if effect is Effect.READ:
            return request
        if self.options.get("dry_run"):
            raise DryRunPlanned(PlannedRequest.of(request))
        if effect is Effect.DESTRUCTIVE and not self.options.get("yes"):
            self._confirm(f"{request.method} {shown(request.url)} — this deletes data.")
        return request

    def _with_fields(self, request: httpx2.Request) -> httpx2.Request:
        """``request`` with ``--body-file`` and ``-F`` under its body; the first request only."""
        if self.fields.taken or not self.fields.given:
            return request
        json_sent = request.headers.get("content-type", "").startswith("application/json")
        body = json.loads(request.content) if json_sent and request.content else None
        if not isinstance(body, dict):
            # violation(arch-9): -F and --body-file add fields to a JSON object; a request
            # without one has nothing to add them to
            raise typer.BadParameter(NO_BODY, param_hint="-F / --body-file")
        kept = {
            name: value
            for name, value in request.headers.items()
            if name.lower() not in {"content-length", "content-type"}
        }
        return httpx2.Request(
            request.method,
            request.url,
            headers=kept,
            json=self.fields.over(body),
            extensions=request.extensions,
        )

    def _confirm(self, what: str) -> None:
        if not attended():
            typer.secho(
                f"{what} Pass --yes to confirm; there is no terminal to ask on.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(ExitCode.USAGE)
        typer.confirm(f"{what} Continue?", abort=True, err=True)
