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

from ycli.yandex.errors import YandexAuthError

_AUTH_HINT = (
    "\nHint: run `ycli auth login` to (re)authenticate, or check that "
    "YANDEX_ID_OAUTH_TOKEN and YANDEX_ID_ORGANIZATION_ID are set."
)

# The credential env vars. pydantic-settings reports a missing field under its validation
# alias (the env var name), so a ``ValidationError`` loc is already one of these strings.
_CREDENTIAL_ENV_NAMES = frozenset({"YANDEX_ID_OAUTH_TOKEN", "YANDEX_ID_ORGANIZATION_ID"})


def format_cli_error(exc: Exception) -> str:
    """A single human-readable message for a fatal CLI error, with a next step where it helps."""
    missing = _missing_credentials(exc)
    if missing:
        return (
            f"Not signed in — {', '.join(missing)} "
            f"{'are' if len(missing) > 1 else 'is'} not set.\n\n"
            "Run `ycli auth login` to authenticate interactively, or export those environment "
            "variables yourself. Check status any time with `ycli auth status`."
        )
    message = f"Error: {exc}"
    if isinstance(exc, YandexAuthError):
        return message + _AUTH_HINT
    return message


def _missing_credentials(exc: Exception) -> list[str]:
    """The credential env vars a pydantic ``ValidationError`` reports as missing (else ``[]``)."""
    if not isinstance(exc, ValidationError):
        return []
    return [
        name
        for error in exc.errors()
        if error.get("type") == "missing"
        and error["loc"]
        and (name := str(error["loc"][0])) in _CREDENTIAL_ENV_NAMES
    ]
