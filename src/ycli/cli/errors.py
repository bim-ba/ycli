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

from typing import TypeGuard

from pydantic import ValidationError

from ycli.cli.exit_codes import ExitCode
from ycli.settings import (
    AppConfig,
    Credentials,
    ProfileError,
    missing_credentials,
)
from ycli.yandex.errors import (
    YandexAuthError,
    YandexConnectionError,
    YandexInvalidRequestError,
    YandexNotConfiguredError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
    YandexStaleContinuationError,
    YandexTimeoutError,
    next_step,
)
from ycli.yandex.models import field_error

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
    if isinstance(exc, ProfileError):
        return f"Invalid configuration:\n  {exc}"
    if isinstance(exc, ValidationError):
        return "The request cannot be built:\n" + "\n".join(map(field_error, exc.errors()))
    hint = next_step(exc)
    return f"Error: {exc}" + (f"\nHint: {hint}" if hint else "")


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
    # A bad setting, or a request the arguments given cannot build: nothing was sent.
    if isinstance(
        exc,
        (ValidationError, ProfileError, YandexInvalidRequestError, YandexNotConfiguredError),
    ):
        return ExitCode.USAGE
    if isinstance(exc, YandexStaleContinuationError):
        return ExitCode.STALE
    if isinstance(exc, YandexNotFoundError):
        return ExitCode.NOT_FOUND
    if isinstance(exc, YandexRateLimitError):
        return ExitCode.RATE_LIMITED
    if isinstance(exc, YandexServerError | YandexTimeoutError | YandexConnectionError):
        return ExitCode.TRANSIENT
    return ExitCode.FAILURE


def _is_invalid_configuration(exc: Exception) -> TypeGuard[ValidationError]:
    """Whether ``exc`` is the ``ValidationError`` of a bad setting, or of two tokens at once.

    Missing credentials are not a configuration error: :func:`missing_credentials` names them.
    """
    return isinstance(exc, ValidationError) and exc.title in _SETTINGS_TITLES
