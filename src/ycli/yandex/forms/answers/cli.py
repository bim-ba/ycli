"""`forms answers` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms._types import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="answers", help="Forms answers.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    limit: Annotated[int, typer.Option(help="Max responses (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every response (no cap).")] = False,
) -> None:
    """List a form's responses (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.forms.answers.list_all(survey_id, limit=cap), app_ctx.strategy, app_ctx.console
    )
