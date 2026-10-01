"""`ycli auth` — inspect (`status`) and obtain (`login`) Yandex 360 credentials."""

from __future__ import annotations

import contextlib
import os
import time
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from pydantic import SecretStr, ValidationError
from rich.console import Console
from rich.panel import Panel

from ycli.cli.output import ExitWith
from ycli.cli.progress import spinner
from ycli.settings import AppConfig, Credentials, OAuthAppConfig

if TYPE_CHECKING:
    from collections.abc import Iterator
from ycli.yandex.status.client import OAuthClient, TokenPollResult
from ycli.yandex.status.env_file import EnvFile
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter

app = typer.Typer(
    name="auth", help="Inspect and obtain Yandex 360 credentials.", no_args_is_help=True
)

_ENV_NAMES = {
    "oauth_token": "YANDEX_ID_OAUTH_TOKEN",
    "organization_id": "YANDEX_ID_ORGANIZATION_ID",
}


@app.command()
def status(*, config: AppConfig) -> AuthReport | ExitWith:
    """Report whether the env credentials are set and actually work, per service."""
    try:
        credentials = Credentials()  # ty: ignore[missing-argument]
    except ValidationError as exc:
        missing = ", ".join(
            _ENV_NAMES.get(str(e["loc"][0]), str(e["loc"][0])) for e in exc.errors()
        )
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        return ExitWith(AuthReport(configured=False, services=[]))

    report = StatusReporter.for_credentials(credentials, config).report(
        configured=True, organization_id=credentials.organization_id
    )
    return report if all(s.valid for s in report.services) else ExitWith(report)


@app.command()
def login(
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
    *,
    config: AppConfig,
) -> AuthReport:
    """Obtain a Yandex OAuth token + organization id and save them to .env.

    Uses your own OAuth app (YANDEX_OAUTH_CLIENT_ID / YANDEX_OAUTH_CLIENT_SECRET): the
    headless device flow when both are set, otherwise the browser paste (implicit) flow.
    The token is validated against every service before it is written.
    """
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

    oauth_client = OAuthClient(
        client_id=oauth_config.client_id,
        client_secret=(
            oauth_config.client_secret.get_secret_value() if oauth_config.client_secret else None
        ),
        timeout_seconds=config.http.timeout_seconds,
        retries=config.http.retries,
    )

    if implicit or oauth_config.client_secret is None:
        token = _implicit_flow(oauth_client, Console(stderr=True))
    else:
        token = _device_flow(oauth_client, device_name, Console(stderr=True))

    organization_id = _resolve_organization_id(oauth_client, token)
    credentials = Credentials(oauth_token=SecretStr(token), organization_id=organization_id)
    report = StatusReporter.for_credentials(credentials, config).report(
        configured=True, organization_id=organization_id
    )
    _write_env_file(token, organization_id, report, assume_yes=assume_yes)
    return report


@contextlib.contextmanager
def _suppressed_stderr() -> Iterator[None]:
    """Silence fd-level stderr for the duration — the OS browser launcher (``xdg-open`` and
    friends) prints chatter straight to fd 2 that would otherwise smear the login prompt."""
    saved_stderr_fd = os.dup(2)
    with Path(os.devnull).open("w", encoding="utf-8") as devnull:
        os.dup2(devnull.fileno(), 2)
        try:
            yield
        finally:
            os.dup2(saved_stderr_fd, 2)
            os.close(saved_stderr_fd)


def _implicit_flow(oauth_client: OAuthClient, console: Console) -> str:
    """Open the authorize URL, then read the token the user pastes from the verify page."""
    url = oauth_client.authorize_url()
    console.print(f"Opening {url}")
    console.print("If it does not open, paste that URL into a browser, log in, and approve.")
    with _suppressed_stderr():
        webbrowser.open(url)
    return typer.prompt(
        "Paste the token shown on the Yandex verification page", hide_input=True, err=True
    ).strip()


def _device_flow(oauth_client: OAuthClient, device_name: str | None, console: Console) -> str:
    """Request a device code, show it prominently, then poll until approved (or it fails)."""
    device = oauth_client.request_device_code(device_name=device_name)
    console.print(
        Panel(
            f"Visit [bold]{device.verification_url}[/bold] and enter code:\n\n"
            f"    [bold cyan]{device.user_code}[/bold cyan]",
            title="Authorize ycli",
            expand=False,
        )
    )
    with spinner("Waiting for authorization…", console=console):
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
        typer.echo(f"Using organization {organization.name} ({organization.id}).", err=True)
        return str(organization.id)
    if len(organizations) > 1:
        typer.echo("Multiple organizations found:", err=True)
        for index, organization in enumerate(organizations, start=1):
            typer.echo(f"  {index}. {organization.name} ({organization.id})", err=True)
        selected = typer.prompt("Choose an organization number", type=int, err=True)
        return str(organizations[selected - 1].id)
    typer.echo("Could not detect an organization (the token lacks directory scope).", err=True)
    typer.echo("Find your organization id at https://tracker.yandex.ru/admin/orgs", err=True)
    return typer.prompt("Enter your organization id", err=True).strip()


def _write_env_file(
    token: str, organization_id: str, report: AuthReport, *, assume_yes: bool
) -> None:
    """Confirm (unless ``--yes``), back up any existing .env, and upsert the two keys.

    Messages go to stderr: stdout carries only the report the command returns.
    """
    accepted = [status.service for status in report.services if status.valid]
    rejected = [status.service for status in report.services if not status.valid]
    verdict = f"The token works for: {', '.join(accepted) or 'no service'}."
    if rejected:
        verdict += f" Rejected by: {', '.join(rejected)}."
    prompt = f"{verdict} Save these credentials to .env?"
    if not assume_yes and not typer.confirm(prompt, err=True):
        typer.echo("Skipped; nothing written.", err=True)
        return
    values = {
        _ENV_NAMES["oauth_token"]: token,
        _ENV_NAMES["organization_id"]: organization_id,
    }
    backup = EnvFile.upsert(Path(".env"), values)
    if backup is not None:
        typer.echo(f"Backed up existing .env to {backup}", err=True)
    typer.secho(
        f"Saved credentials to .env (token {_mask(token)}).", fg=typer.colors.GREEN, err=True
    )


def _mask(token: str) -> str:
    """A safe-to-print token fingerprint — never the full secret."""
    return f"...{token[-4:]}"
