"""`ycli auth status` — validate credentials against each service's identity endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from collections.abc import Callable
from pydantic import Field, ValidationError

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.settings import Credentials
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.models import APIModel
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)


class ServiceAuthStatus(APIModel):
    service: str
    valid: bool = False
    identity: str | None = None
    detail: str = ""


class AuthReport(APIModel):
    configured: bool
    organization_id: str = ""
    services: list[ServiceAuthStatus] = Field(default_factory=list)


_PROBES: list[tuple[str, type, Callable[[object], str]]] = [
    ("tracker", TrackerClient, lambda me: me.login),  # ty: ignore[unresolved-attribute]
    ("wiki", WikiClient, lambda me: me.username),  # ty: ignore[unresolved-attribute]
    ("forms", FormsClient, lambda me: me.email),  # ty: ignore[unresolved-attribute]
]


def _probe(
    name: str, client_cls: type, identity_of: Callable[[object], str], credentials: Credentials
) -> ServiceAuthStatus:
    client = client_cls(
        oauth_token=credentials.oauth_token, organization_id=credentials.organization_id
    )
    try:
        me = client.me.get()
    except YandexAuthError:
        return ServiceAuthStatus(service=name, valid=False, detail="token invalid or expired")
    except YandexError as exc:
        return ServiceAuthStatus(service=name, valid=False, detail=str(exc))
    return ServiceAuthStatus(service=name, valid=True, identity=identity_of(me))


@app.command()
def status(ctx: typer.Context) -> None:
    """Report whether the env credentials are set and actually work, per service."""
    app_ctx = AppContext.from_typer_context(ctx)
    env_names = {
        "oauth_token": "YANDEX_ID_OAUTH_TOKEN",
        "organization_id": "YANDEX_ID_ORGANIZATION_ID",
    }
    try:
        credentials = Credentials()  # ty: ignore[missing-argument]
    except ValidationError as exc:
        missing = ", ".join(env_names.get(str(e["loc"][0]), str(e["loc"][0])) for e in exc.errors())
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        Serializer.serialize(
            AuthReport(configured=False, services=[]), app_ctx.strategy, app_ctx.console
        )
        raise typer.Exit(1) from None

    services = [_probe(name, cls, ident, credentials) for name, cls, ident in _PROBES]
    report = AuthReport(
        configured=True, organization_id=credentials.organization_id, services=services
    )
    Serializer.serialize(report, app_ctx.strategy, app_ctx.console)
    if not all(s.valid for s in services):
        raise typer.Exit(1)
