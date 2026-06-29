"""`forms questions` commands."""

from __future__ import annotations

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms._types import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="questions", help="Forms questions.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """List a form's questions (the {pages} envelope)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.questions.list(survey_id), app_ctx.strategy, app_ctx.console)
