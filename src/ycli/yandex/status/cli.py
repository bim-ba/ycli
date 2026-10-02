"""`ycli auth` — inspect (`status`) and obtain (`login`) Yandex 360 credentials."""

from __future__ import annotations

# PEP 810: on Python 3.15+ these load on first use (only `auth login` needs them);
# older versions ignore the name.
__lazy_modules__ = {"webbrowser", "rich.panel"}

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

from ycli.cli.exit_codes import ExitCode
from ycli.cli.global_options import refuse_dry_run
from ycli.cli.output import ExitWith
from ycli.settings import (
    OAUTH_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    AppConfig,
    Credentials,
    OAuthAppConfig,
    missing_credentials,
)
from ycli.yandex.errors import YandexAuthError
from ycli.yandex.status.client import OAuthClient, TokenPollResult
from ycli.yandex.status.env_file import EnvFile
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import build_report
from ycli.yandex.status.service_cli import failure_code
from ycli.yandex.status.token_client import TokenClient

if TYPE_CHECKING:
    from collections.abc import Iterator

    from ycli.yandex.status.oauth_models import Organization

# Help text lives with the root sub-app list (ycli.cli.app).
app = typer.Typer(name="auth", no_args_is_help=True)

_ENV_NAMES = {
    "oauth_token": OAUTH_TOKEN_ENV,
    "organization_id": ORGANIZATION_ID_ENV,
}


@app.command()
def status(*, config: AppConfig) -> AuthReport | ExitWith:
    """Report whether the env credentials are set, whose they are, and which services accept them.

    The owner comes from Yandex ID, the organization name from API 360, and each service is
    probed with its own call. `ycli <service> auth status` probes just one service.
    """
    try:
        credentials = Credentials()  # ty: ignore[missing-argument]
    except ValidationError as exc:
        missing = ", ".join(missing_credentials(exc))
        typer.secho(f"not configured — missing {missing}", fg=typer.colors.RED, err=True)
        return ExitWith(AuthReport(configured=False), exit_code=ExitCode.AUTH)

    report = build_report(credentials, config)
    return (
        report
        if all(s.valid for s in report.services)
        else ExitWith(report, exit_code=failure_code(report.services))
    )


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
    context: typer.Context,
    config: AppConfig,
) -> AuthReport:
    """Obtain a Yandex OAuth token + organization id and save them to .env.

    Uses your own OAuth app (YANDEX_OAUTH_CLIENT_ID / YANDEX_OAUTH_CLIENT_SECRET): the
    headless device flow when both are set, otherwise the browser paste (implicit) flow.
    The token is validated against every service before it is written.
    """
    refuse_dry_run(context, "auth login signs in and writes .env; there is nothing to plan.")
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

    organization_id = _resolve_organization_id(_visible_organizations(token, config))
    credentials = Credentials(oauth_token=SecretStr(token), organization_id=organization_id)
    report = build_report(credentials, config)
    _write_env_file(token, organization_id, report, assume_yes=assume_yes)
    return report


@contextlib.contextmanager
def _suppressed_stderr() -> Iterator[None]:
    """Silence fd-level stderr for the duration of the block.

    The OS browser launcher (``xdg-open`` and friends) prints chatter straight to fd 2 that would
    otherwise smear the login prompt.
    """
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
    token = typer.prompt(
        "Paste the token shown on the Yandex verification page", hide_input=True, err=True
    ).strip()
    if not token:
        typer.secho(
            "No token was pasted. Re-run `ycli auth login` and paste the token from the page.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    return token


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
    # A static line, not a spinner: a live redraw drops the selection while the user copies
    # the code above.
    console.print("Waiting for you to confirm in the browser… (Ctrl+C to cancel)")
    while True:
        result: TokenPollResult = oauth_client.poll_token(device.device_code)
        if result.token is not None:
            return result.token.access_token
        if result.pending:
            time.sleep(device.interval)
            continue
        typer.secho(f"Authorization failed: {result.error}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


def _visible_organizations(token: str, config: AppConfig) -> list[Organization]:
    """The token's organizations from API 360, or ``[]`` when it lacks the directory scope."""
    with TokenClient(oauth_token=token, http=config.http) as token_client:
        try:
            return token_client.organizations()
        except YandexAuthError:
            return []


def _resolve_organization_id(organizations: list[Organization]) -> str:
    """Pick the org from API 360's list; prompt when it is ambiguous or the scope is missing."""
    if len(organizations) == 1:
        organization = organizations[0]
        typer.echo(f"Using organization {organization.name} ({organization.id}).", err=True)
        return str(organization.id)
    if len(organizations) > 1:
        typer.echo("Multiple organizations found:", err=True)
        for index, organization in enumerate(organizations, start=1):
            typer.echo(f"  {index}. {organization.name} ({organization.id})", err=True)
        selected = typer.prompt("Choose an organization number", type=int, err=True)
        while not 1 <= selected <= len(organizations):
            typer.echo(f"Enter a number from 1 to {len(organizations)}.", err=True)
            selected = typer.prompt("Choose an organization number", type=int, err=True)
        return str(organizations[selected - 1].id)
    typer.echo(
        "Could not detect an organization: the token lacks the directory:read_organization "
        "permission. Add it to your OAuth app at https://oauth.yandex.ru and sign in again to "
        "skip this step, or copy the id from Tracker → Administration → Organizations "
        "(https://tracker.yandex.ru/admin/orgs).",
        err=True,
    )
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
