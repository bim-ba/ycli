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
    "\nHint: run `ycli auth login` to (re)authenticate with OAuth, or check your "
    "YANDEX_ID_OAUTH_TOKEN / YANDEX_CLOUD_IAM_TOKEN credential variables."
)

def format_cli_error(exc: Exception) -> str:
    """A single human-readable message for a fatal CLI error, with a next step where it helps."""
    if isinstance(exc, ValidationError) and exc.title == "Credentials":
        details = "; ".join(
            str(error.get("ctx", {}).get("error", error["msg"])) for error in exc.errors()
        )
        return (
            f"Not signed in — invalid credential configuration: {details}.\n\n"
            "Run `ycli auth login` to authenticate with OAuth, or configure IAM credentials. "
            "Check status any time with `ycli auth status`."
        )
    message = f"Error: {exc}"
    if isinstance(exc, YandexAuthError):
        return message + _AUTH_HINT
    return message
