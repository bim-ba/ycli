"""`ycli auth status` — validate credentials against Tracker /myself and report."""
from __future__ import annotations

import os

import typer
from pydantic import BaseModel

from ycli.output import render
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.tracker.client import TrackerClient

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)


class AuthStatus(BaseModel):
    """The result of an auth probe — rendered like any other ycli result."""

    configured: bool
    org_id: str = ""
    valid: bool = False
    login: str | None = None
    display: str | None = None
    detail: str = ""


@app.command()
def status() -> None:
    """Report whether the env credentials are set and actually work."""
    token = os.environ.get("YANDEX_ID_OAUTH_TOKEN", "")
    org = os.environ.get("YANDEX_ID_ORGANIZATION_ID", "")
    if not token or not org:
        missing = ", ".join(
            name
            for name, value in (
                ("YANDEX_ID_OAUTH_TOKEN", token),
                ("YANDEX_ID_ORGANIZATION_ID", org),
            )
            if not value
        )
        render(AuthStatus(configured=False, org_id=org, detail=f"not configured — missing {missing}"))
        raise typer.Exit(1)

    try:
        me = TrackerClient.from_env().me.get()
    except YandexAuthError:
        render(AuthStatus(configured=True, org_id=org, valid=False, detail="token invalid or expired"))
        raise typer.Exit(1) from None
    except YandexError as exc:
        render(AuthStatus(configured=True, org_id=org, valid=False, detail=str(exc)))
        raise typer.Exit(1) from None

    render(AuthStatus(configured=True, org_id=org, valid=True, login=me.login, display=me.display))
