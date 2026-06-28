"""`forms answers` commands."""
from __future__ import annotations

import typer

from ycli.context import AppContext
from ycli.output import Serializer
from ycli.yandex.forms._args import SurveyIdArg

app = typer.Typer(name="answers", help="Forms answers.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """List ALL of a form's responses (drains every page via the next cursor)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.answers.list_all(survey_id), app_ctx.strategy, app_ctx.console)
