"""`ycli auth status` — validate credentials against each service's identity endpoint.

Cross-cutting: sits above the three domains and imports their clients. CLI-only — the MCP
server stays read-only domain tools (no auth tool).
"""
from __future__ import annotations

import typer
from pydantic import BaseModel, ValidationError

from ycli.output import render
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.settings import Credentials
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)


class ServiceAuthStatus(BaseModel):
    """Per-service probe result. ``identity`` is the service's own user handle —
    Tracker ``login``, Wiki ``username``, Forms ``email``."""

    service: str
    valid: bool = False
    identity: str | None = None
    detail: str = ""


class AuthReport(BaseModel):
    """The full auth probe — rendered like any other ycli result."""

    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = []


def _probe_tracker() -> ServiceAuthStatus:
    try:
        me = TrackerClient.from_env().me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service="tracker", valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service="tracker", valid=False, detail=str(exc))
    return ServiceAuthStatus(service="tracker", valid=True, identity=me.login)


def _probe_forms() -> ServiceAuthStatus:
    try:
        me = FormsClient.from_env().me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service="forms", valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service="forms", valid=False, detail=str(exc))
    return ServiceAuthStatus(service="forms", valid=True, identity=me.email)


def _probe_wiki() -> ServiceAuthStatus:
    try:
        me = WikiClient.from_env().me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service="wiki", valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service="wiki", valid=False, detail=str(exc))
    return ServiceAuthStatus(service="wiki", valid=True, identity=me.username)


@app.command()
def status() -> None:
    """Report whether the env credentials are set and actually work, per service."""
    env_names = {
        "oauth_token": "YANDEX_ID_OAUTH_TOKEN",
        "organization_id": "YANDEX_ID_ORGANIZATION_ID",
    }
    try:
        credentials = Credentials()
    except ValidationError as exc:
        missing = ", ".join(
            env_names.get(str(error["loc"][0]), str(error["loc"][0])) for error in exc.errors()
        )
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        render(AuthReport(configured=False, services=[]))
        raise typer.Exit(1) from None

    services = [_probe_tracker(), _probe_wiki(), _probe_forms()]
    report = AuthReport(
        configured=True,
        organization_id=credentials.organization_id,
        services=services,
    )
    render(report)
    if not all(service.valid for service in services):
        raise typer.Exit(1)
