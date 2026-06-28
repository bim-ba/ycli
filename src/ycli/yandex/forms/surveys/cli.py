"""`forms surveys` commands."""

from __future__ import annotations

import typer

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.yandex.forms._args import SurveyIdArg

app = typer.Typer(name="surveys", help="Forms surveys.", no_args_is_help=True)


@app.command("list")
def list_(ctx: typer.Context) -> None:
    """List all forms (the {links, result} envelope)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.surveys.list(), app_ctx.strategy, app_ctx.console)


@app.command()
def get(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Print one form's settings for SURVEY_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.surveys.get(survey_id), app_ctx.strategy, app_ctx.console)
