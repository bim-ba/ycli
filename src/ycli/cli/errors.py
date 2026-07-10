"""Human-facing formatting for errors that reach the CLI entry point.

Kept as a pure function so the message/hint logic is unit-testable; the console
entry point (``ycli.cli.app.main``) is a thin, coverage-excluded wrapper that
prints the result and exits. A missing/expired credential is the most common
fatal error, so an auth failure appends a concrete next step.
"""

from __future__ import annotations

from ycli.yandex.errors import YandexAuthError

_AUTH_HINT = (
    "\nHint: run `ycli auth login` to (re)authenticate, or check that "
    "YANDEX_ID_OAUTH_TOKEN and YANDEX_ID_ORGANIZATION_ID are set."
)


def format_cli_error(exc: Exception) -> str:
    """A single human-readable message for a fatal CLI error (plus a hint on auth failures)."""
    message = f"Error: {exc}"
    if isinstance(exc, YandexAuthError):
        return message + _AUTH_HINT
    return message
