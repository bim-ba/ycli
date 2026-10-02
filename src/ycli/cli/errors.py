"""Human-facing formatting for errors that reach the CLI entry point.

Kept as a pure function so the message/hint logic is unit-testable; the console
entry point (``ycli.cli.app.main``) is a thin, coverage-excluded wrapper that
prints the result and exits. Two fatal cases get a concrete next step: an expired/
rejected credential (:class:`YandexAuthError`) and a *missing* credential — the
first-run case, where pydantic raises a ``ValidationError`` for the unset env vars
and we route the user to ``ycli auth login`` instead of dumping a validation dump.
"""

from __future__ import annotations

from pydantic import ValidationError

from ycli.settings import OAUTH_TOKEN_ENV, ORGANIZATION_ID_ENV, AppConfig, missing_credentials
from ycli.yandex.errors import YandexAuthError

_AUTH_HINT = (
    "\nHint: run `ycli auth login` to (re)authenticate, or check that "
    f"{OAUTH_TOKEN_ENV} and {ORGANIZATION_ID_ENV} are set."
)
# A 403 comes with a valid token: signing in again does not help, a permission or scope does.
_PERMISSION_HINT = (
    "\nHint: the token is valid but lacks access here — ask an administrator for permission "
    "on this resource, or check that the token's OAuth scopes cover this service."
)


def format_cli_error(exc: Exception) -> str:
    """A single human-readable message for a fatal CLI error, with a next step where it helps."""
    missing = missing_credentials(exc)
    if missing:
        return (
            f"Not signed in — {', '.join(missing)} "
            f"{'are' if len(missing) > 1 else 'is'} not set.\n\n"
            "Run `ycli auth login` to authenticate interactively, or export those environment "
            "variables yourself. Check status any time with `ycli auth status`."
        )
    if isinstance(exc, ValidationError) and exc.title == AppConfig.__name__:
        return "Invalid configuration:\n" + "\n".join(
            f"  YCLI__{'__'.join(str(part) for part in error['loc']).upper()}: {error['msg']}"
            for error in exc.errors()
        )
    message = f"Error: {exc}"
    if isinstance(exc, YandexAuthError):
        return message + (_PERMISSION_HINT if exc.status == 403 else _AUTH_HINT)
    return message
