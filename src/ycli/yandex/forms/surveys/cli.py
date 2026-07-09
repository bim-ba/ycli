"""`forms surveys` commands."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="surveys", help="Forms surveys.", no_args_is_help=True)


@app.command("list")
def list_(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option(help="Max forms (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every form (no cap).")] = False,
) -> None:
    """List all forms (auto-paginated over offset pages; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(app_ctx.forms.surveys.list(limit=cap), app_ctx.strategy, app_ctx.console)


@app.command()
def get(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Print one form's settings for SURVEY_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.surveys.get(survey_id), app_ctx.strategy, app_ctx.console)
