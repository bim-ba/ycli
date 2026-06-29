"""`ycli auth status` — validate credentials against each service's identity endpoint."""

from __future__ import annotations

import typer
from pydantic import ValidationError

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.settings import Credentials
from ycli.yandex.status.models import AuthReport
from ycli.yandex.status.reporter import StatusReporter

app = typer.Typer(name="auth", help="Inspect Yandex 360 credentials.", no_args_is_help=True)

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
