"""How the CLI asks, and what it adds to a body: its part of the gate on writes.

The rule itself is the core's (:class:`ycli.yandex.core.guard.Guard`): every request of every
surface goes through it. The CLI says how to ask and when not to:

- ``--dry-run`` sends no write: the core stops at the first one, and the command wrapper turns
  the request it would have sent into the command's result;
- an operation that destroys data asks first, unless ``--yes`` was given: on a terminal it
  prompts on stderr, and a declined prompt aborts (exit 1); with no terminal to ask it fails as a
  usage error (exit 2) that says to pass ``--yes``;
- ``--body-file`` and ``-F`` reach the body of any command: :class:`SendGuard`, the client's
  ``before_send`` hook, lays them under what the command built, so a field with no flag of its
  own can still be sent. It runs before the core's rule, so a plan shows the body as it would go.
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
from ycli.yandex.core.guard import Guard, PlannedRequest

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ycli.cli.body_fields import CallerFields
    from ycli.yandex.core.endpoint import Effect


def attended() -> bool:
    """Whether a person can be asked: stdin and stdout are both terminals (not a pipe or a CI)."""
    # violation(arch-4): only asks whether stdout is a terminal; it writes nothing
    return sys.stdin.isatty() and sys.stdout.isatty()


def confirm_on_the_terminal(plan: PlannedRequest) -> bool:
    """Ask the person at the terminal whether ``plan`` may be sent.

    Args:
        plan: The request about to go out.

    Returns:
        ``True``: a declined prompt and a missing terminal both end the command themselves.

    Raises:
        typer.Exit: Nobody can be asked; exits as a usage error that says to pass ``--yes``.
    """
    what = f"{plan.method} {plan.url} — this deletes data."
    if not attended():
        typer.secho(
            f"{what} Pass --yes to confirm; there is no terminal to ask on.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(ExitCode.USAGE)
    typer.confirm(f"{what} Continue?", abort=True, err=True)
    return True


def guard_of(options: Mapping[str, Any]) -> Guard:
    """The core's rule as the global options of this invocation set it.

    Args:
        options: The root's parsed global options (``--dry-run``, ``--yes``).

    Returns:
        The guard every client of the invocation sends through.

    Examples:
        >>> guard_of({"dry_run": True, "yes": True})
        Guard(dry_run=True, confirm=None)
    """
    return Guard(
        dry_run=bool(options.get("dry_run")),
        confirm=None if options.get("yes") else confirm_on_the_terminal,
    )


@dataclass
class SendGuard:
    """The ``before_send`` hook of the CLI: ``--body-file`` and ``-F`` go into a request's body.

    They go into the first request of the command, under what the command built from its flags:
    file, then ``-F``, then the flags, the later the stronger.
    """

    fields: CallerFields

    def __call__(self, effect: Effect, request: httpx2.Request) -> httpx2.Request:
        """``request`` with the caller's fields in its body, when any were given.

        Args:
            effect: What the endpoint does to the server (not looked at).
            request: The request about to go out.

        Returns:
            The request to send.
        """
        return self._with_fields(request)

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
