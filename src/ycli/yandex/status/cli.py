"""`ycli auth` — inspect (`status`) and obtain (`login`) Yandex 360 credentials."""

from __future__ import annotations

import time
import webbrowser
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.settings import AppConfig, Credentials, OAuthAppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.status.client import OAuthClient, TokenPollResult
from ycli.yandex.status.env_file import EnvFile
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter
from ycli.yandex.tracker.client import TrackerClient
from ycli.yandex.wiki.client import WikiClient

app = typer.Typer(
    name="auth", help="Inspect and obtain Yandex 360 credentials.", no_args_is_help=True
)

_ENV_NAMES = {
    "oauth_token": "YANDEX_ID_OAUTH_TOKEN",
    "organization_id": "YANDEX_ID_ORGANIZATION_ID",
}


@app.command()
def status(ctx: typer.Context) -> None:
    """Report whether the env credentials are set and actually work, per service."""
    app_ctx = AppContext.from_typer_context(ctx)
    try:
        credentials = Credentials()  # ty: ignore[missing-argument]
    except ValidationError as exc:
        missing = ", ".join(
            _ENV_NAMES.get(str(e["loc"][0]), str(e["loc"][0])) for e in exc.errors()
        )
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        Serializer.serialize(
            AuthReport(configured=False, services=[]), app_ctx.strategy, app_ctx.console
        )
        raise typer.Exit(1) from None

    me_clients = {
        "tracker": app_ctx.tracker.me,
        "wiki": app_ctx.wiki.me,
        "forms": app_ctx.forms.me,
    }
    report = StatusReporter(me_clients).report(
        configured=True, organization_id=credentials.organization_id
    )
    Serializer.serialize(report, app_ctx.strategy, app_ctx.console)
    if not all(s.valid for s in report.services):
        raise typer.Exit(1)


@app.command()
def login(
    ctx: typer.Context,
    implicit: Annotated[
        bool,
        typer.Option(
            "--implicit", help="Use the browser paste flow even if a client secret is set."
        ),
    ] = False,
    assume_yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Write .env without asking to confirm."),
    ] = False,
    device_name: Annotated[
        str | None,
        typer.Option("--device-name", help="Label shown for this device during OAuth approval."),
    ] = None,
) -> None:
    """Obtain a Yandex OAuth token + organization id and save them to .env.

    Uses your own OAuth app (YANDEX_OAUTH_CLIENT_ID / YANDEX_OAUTH_CLIENT_SECRET): the
    headless device flow when both are set, otherwise the browser paste (implicit) flow.
    The token is validated against Tracker, Wiki, and Forms before it is written.
    """
    app_ctx = AppContext.from_typer_context(ctx)
    oauth_config = OAuthAppConfig()
    if not oauth_config.client_id:
        typer.secho(
            "No OAuth app configured. Register one at https://oauth.yandex.ru, grant it "
            "Tracker/Wiki/Forms permissions, then set YANDEX_OAUTH_CLIENT_ID (and "
            "YANDEX_OAUTH_CLIENT_SECRET for the headless device flow) and re-run.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    config = app_ctx.config
    oauth_client = OAuthClient(
        client_id=oauth_config.client_id,
        client_secret=oauth_config.client_secret,
        timeout_seconds=int(config.timeout_seconds),
        retries=config.retries,
    )

    if implicit or oauth_config.client_secret is None:
        token = _implicit_flow(oauth_client)
    else:
        token = _device_flow(oauth_client, device_name)

    organization_id = _resolve_organization_id(oauth_client, token)
    report = _build_report(token, organization_id, config)
    Serializer.serialize(report, app_ctx.strategy, app_ctx.console)
    _write_env_file(token, organization_id, assume_yes=assume_yes)


def _implicit_flow(oauth_client: OAuthClient) -> str:
    """Open the authorize URL, then read the token the user pastes from the verify page."""
    url = oauth_client.authorize_url()
    typer.echo(f"Opening {url}")
    typer.echo("If it does not open, paste that URL into a browser, log in, and approve.")
    webbrowser.open(url)
    return typer.prompt("Paste the token shown on the Yandex verification page").strip()


def _device_flow(oauth_client: OAuthClient, device_name: str | None) -> str:
    """Request a device code, show it, then poll until the user approves (or it fails)."""
    device = oauth_client.request_device_code(device_name=device_name)
    typer.echo(f"Visit {device.verification_url} and enter code: {device.user_code}")
    while True:
        result: TokenPollResult = oauth_client.poll_token(device.device_code)
        if result.token is not None:
            return result.token.access_token
        if result.pending:
            time.sleep(device.interval)
            continue
        typer.secho(f"Authorization failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


def _resolve_organization_id(oauth_client: OAuthClient, token: str) -> str:
    """Auto-detect the org via api360; prompt when it is ambiguous or the scope is missing."""
    organizations = oauth_client.fetch_organizations(token)
    if len(organizations) == 1:
        organization = organizations[0]
        typer.echo(f"Using organization {organization.name} ({organization.id}).")
        return str(organization.id)
    if len(organizations) > 1:
        typer.echo("Multiple organizations found:")
        for index, organization in enumerate(organizations, start=1):
            typer.echo(f"  {index}. {organization.name} ({organization.id})")
        selected = typer.prompt("Choose an organization number", type=int)
        return str(organizations[selected - 1].id)
    typer.echo("Could not detect an organization (the token lacks directory scope).")
    typer.echo("Find your organization id at https://tracker.yandex.ru/admin/orgs")
    return typer.prompt("Enter your organization id").strip()


def _build_report(token: str, organization_id: str, config: AppConfig) -> AuthReport:
    """Probe Tracker/Wiki/Forms with the new token+org and assemble an AuthReport."""
    timeout_seconds = int(config.timeout_seconds)
    tracker = TrackerClient(
        oauth_token=token,
        organization_id=organization_id,
        timeout_seconds=timeout_seconds,
        retries=config.retries,
    )
    wiki = WikiClient(
        oauth_token=token,
        organization_id=organization_id,
        timeout_seconds=timeout_seconds,
        retries=config.retries,
    )
    forms = FormsClient(
        oauth_token=token,
        organization_id=organization_id,
        timeout_seconds=timeout_seconds,
        retries=config.retries,
    )
    me_clients = {"tracker": tracker.me, "wiki": wiki.me, "forms": forms.me}
    return StatusReporter(me_clients).report(configured=True, organization_id=organization_id)


def _write_env_file(token: str, organization_id: str, *, assume_yes: bool) -> None:
    """Confirm (unless ``--yes``), back up any existing .env, and upsert the two keys."""
    if not assume_yes and not typer.confirm("Save these credentials to .env?"):
        typer.echo("Skipped; nothing written.")
        return
    values = {
        _ENV_NAMES["oauth_token"]: token,
        _ENV_NAMES["organization_id"]: organization_id,
    }
    backup = EnvFile.upsert(Path(".env"), values)
    if backup is not None:
        typer.echo(f"Backed up existing .env to {backup}")
    typer.secho(f"Saved credentials to .env (token {_mask(token)}).", fg=typer.colors.GREEN)


def _mask(token: str) -> str:
    """A safe-to-print token fingerprint — never the full secret."""
    return f"...{token[-4:]}"
