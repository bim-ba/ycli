"""The CLI's gate on writes: ``AppContext`` hands :class:`SendGuard` to every client it builds.

The core calls it once per endpoint, before the first HTTP attempt, with the endpoint's effect
and the request about to go out (``ycli.yandex.core.session.BeforeSend``), so no command needs
its own confirmation code. An operation that destroys data asks first, unless ``--yes`` was
given: on a terminal it prompts on stderr, and a declined prompt aborts (exit 1); with no
terminal to ask it fails as a usage error (exit 2) that says to pass ``--yes``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import typer
from typer._click.exceptions import UsageError

from ycli.yandex.core.session import shown

if TYPE_CHECKING:
    from collections.abc import Mapping

    import httpx2

    from ycli.yandex.core.endpoint import Effect


def attended() -> bool:
    """Whether a person can be asked: stdin and stdout are both terminals (not a pipe or a CI)."""
    return sys.stdin.isatty() and sys.stdout.isatty()


@dataclass(frozen=True)
class SendGuard:
    """The ``before_send`` hook of the CLI; ``options`` is the root's parsed global options.

    ``options`` is read at call time, so a ``--yes`` given after the subcommand (written into
    the root state by the leaf) counts.
    """

    options: Mapping[str, Any]

    def __call__(self, effect: Effect, request: httpx2.Request) -> None:
        if effect == "destructive" and not self.options.get("yes"):
            self._confirm(f"{request.method} {shown(request.url)} — this deletes data.")

    def _confirm(self, what: str) -> None:
        if not attended():
            raise UsageError(f"{what} Pass --yes to confirm; there is no terminal to ask on.")
        typer.confirm(f"{what} Continue?", abort=True, err=True)
