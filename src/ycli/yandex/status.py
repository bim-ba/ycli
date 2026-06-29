"""`ycli auth status` — validate credentials against each service's identity endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer

if TYPE_CHECKING:
    from collections.abc import Callable
from pydantic import Field, ValidationError

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.settings import AppConfig, Credentials
from ycli.yandex.errors import YandexAuthError, YandexError
from ycli.yandex.factory import ClientFactory
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


class ServiceProbe:
    """One service's identity check — name, client class, and identity extractor together."""

    def __init__(
        self, name: str, client_cls: type, identity_of: Callable[[Any], str | None]
    ) -> None:
        self._name, self._client_cls, self._identity_of = name, client_cls, identity_of

    def run(self, credentials: Credentials) -> ServiceAuthStatus:
        client = ClientFactory.build(self._client_cls, credentials, AppConfig())
        try:
            me = client.me.get()  # ty: ignore[unresolved-attribute]
        except YandexAuthError:
            return ServiceAuthStatus(
                service=self._name, valid=False, detail="token invalid or expired"
            )
        except YandexError as exc:
            return ServiceAuthStatus(service=self._name, valid=False, detail=str(exc))
        return ServiceAuthStatus(service=self._name, valid=True, identity=self._identity_of(me))


PROBES: list[ServiceProbe] = [
    ServiceProbe("tracker", TrackerClient, lambda me: me.login),
    ServiceProbe("wiki", WikiClient, lambda me: me.username),
    ServiceProbe("forms", FormsClient, lambda me: me.email),
]


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

    services = [p.run(credentials) for p in PROBES]
    report = AuthReport(
        configured=True, organization_id=credentials.organization_id, services=services
    )
    Serializer.serialize(report, app_ctx.strategy, app_ctx.console)
    if not all(s.valid for s in services):
        raise typer.Exit(1)
