"""Human-facing formatting for errors that reach the CLI entry point.

Kept as a pure function so the message/hint logic is unit-testable; the console
entry point (``ycli.cli.app.main``) is a thin, coverage-excluded wrapper that
prints the result and exits. Fatal cases get a concrete next step: an expired/rejected
credential (:class:`YandexAuthError`), a *missing* credential — the first-run case, where
pydantic raises a ``ValidationError`` for the unset env vars and we route the user to
``ycli auth login`` instead of dumping a validation dump — a 404 and a 429. :func:`exit_code_for`
is the one mapping from an error to the process exit status (see :class:`ExitCode`).
"""

from __future__ import annotations

from http import HTTPStatus
from typing import TypeGuard

from pydantic import ValidationError

from ycli.cli.exit_codes import ExitCode
from ycli.settings import (
    OAUTH_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    AppConfig,
    Credentials,
    missing_credentials,
)
from ycli.yandex.errors import (
    YandexAuthError,
    YandexConnectionError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
    YandexTimeoutError,
)

_AUTH_HINT = (
    "\nHint: run `ycli auth login` to (re)authenticate, or check that "
    f"{OAUTH_TOKEN_ENV} and {ORGANIZATION_ID_ENV} are set."
)
# A 403 comes with a valid token: signing in again does not help, a permission or scope does.
_PERMISSION_HINT = (
    "\nHint: the token is valid but lacks access here — ask an administrator for permission "
    "on this resource, or check that the token's OAuth scopes cover this service."
)
_NOT_FOUND_HINT = (
    "\nHint: check the id or key, and that the token's organization and user can see it "
    "(Yandex answers 404 for an object the caller may not read)."
)


_SETTINGS_TITLES = frozenset({AppConfig.__name__, Credentials.__name__})


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
    if _is_invalid_configuration(exc):
        return "Invalid configuration:\n" + "\n".join(
            # A setting is named by its variable; the credentials' own error names them itself.
            f"  YCLI__{'__'.join(str(part) for part in error['loc']).upper()}: {error['msg']}"
            if exc.title == AppConfig.__name__
            else f"  {error['msg']}"
            for error in exc.errors()
        )
    message = f"Error: {exc}"
    if isinstance(exc, YandexAuthError):
        return message + (_PERMISSION_HINT if exc.status == HTTPStatus.FORBIDDEN else _AUTH_HINT)
    if isinstance(exc, YandexNotFoundError):
        return message + _NOT_FOUND_HINT
    if isinstance(exc, YandexRateLimitError):
        return message + _rate_limit_hint(exc.retry_after)
    return message


def exit_code_for(exc: Exception) -> ExitCode:
    """The process exit status for a fatal error — the one mapping, documented in the README.

    Args:
        exc: The fatal error.

    Returns:
        The exit status for ``exc``.

    Examples:
        >>> exit_code_for(YandexNotFoundError("gone", status=404))
        <ExitCode.NOT_FOUND: 3>
        >>> exit_code_for(RuntimeError("boom"))
        <ExitCode.FAILURE: 1>
    """
    if missing_credentials(exc) or isinstance(exc, YandexAuthError):
        return ExitCode.AUTH
    if _is_invalid_configuration(exc):
        return ExitCode.USAGE
    if isinstance(exc, YandexNotFoundError):
        return ExitCode.NOT_FOUND
    if isinstance(exc, YandexRateLimitError):
        return ExitCode.RATE_LIMITED
    if isinstance(exc, YandexServerError | YandexTimeoutError | YandexConnectionError):
        return ExitCode.TRANSIENT
    return ExitCode.FAILURE


def _rate_limit_hint(retry_after: float | None) -> str:
    """``Hint: … wait 30 s`` when the server sent ``Retry-After``, a generic wait otherwise."""
    wait = "wait a little" if retry_after is None else f"wait {retry_after:g} s (Retry-After)"
    return f"\nHint: the API is rate limiting this token — {wait}, then run the command again."


def _is_invalid_configuration(exc: Exception) -> TypeGuard[ValidationError]:
    """Whether ``exc`` is the ``ValidationError`` of a bad setting, or of two tokens at once.

    Missing credentials are not a configuration error: :func:`missing_credentials` names them.
    """
    return isinstance(exc, ValidationError) and exc.title in _SETTINGS_TITLES
