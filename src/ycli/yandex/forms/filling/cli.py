"""`forms filling` commands (get-settings read + submit write + suggest read).

``submit`` is a write (CLI/SDK only); ``suggest`` is a read but its verb is not an MCP read verb,
so it too stays off MCP. Only ``get`` also reaches MCP (``filling_get``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.filling.models import SubmitBody
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="filling", help="Forms form filling.", no_args_is_help=True)

_KEY = typer.Option("--key", help="Personal-link fill key, when the form uses one.")
# Module-level Annotated alias so ``Path`` is referenced at runtime (typer resolves annotations
# via get_type_hints), keeping the import out of a TYPE_CHECKING block.
BodyFileArg = Annotated[
    Path,
    typer.Option(
        "--body-file",
        help="JSON file: an answer map keyed by question slug (see `filling get` values).",
    ),
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(
    ctx: typer.Context,
    survey: SurveyIdArg,
    key: Annotated[str, _KEY] = "",
) -> None:
    """Print the fillable-form settings for SURVEY (GET …/form) — pages, conditions, values."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.filling.get(survey, key=key or None), app_ctx.strategy, app_ctx.console
    )


@app.command()
def submit(
    ctx: typer.Context,
    survey: SurveyIdArg,
    body_file: BodyFileArg,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Validate only — save nothing, fire no integrations.")
    ] = False,
    key: Annotated[str, _KEY] = "",
) -> None:
    """Submit a form response from --body-file (POST …/form); --dry-run validates only."""
    payload = SubmitBody.model_validate(json.loads(body_file.read_text(encoding="utf-8")))
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.filling.submit(survey, payload, dry_run=dry_run, key=key or None),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def suggest(
    ctx: typer.Context,
    survey: SurveyIdArg,
    question: Annotated[str, typer.Option(help="Question slug the suggestion is for.")] = "",
    text: Annotated[str, typer.Option(help="Text to search suggestions for.")] = "",
    suggest_id: Annotated[
        str, typer.Option("--id", help="Comma-separated suggestion-object ids to resolve.")
    ] = "",
    parent_id: Annotated[
        str, typer.Option("--parent-id", help="Parent ids for a Master/Detail lookup.")
    ] = "",
) -> None:
    """Get fill suggestions for a question (GET …/suggest)."""
    app_ctx = AppContext.from_typer_context(ctx)
    result = app_ctx.forms.filling.suggest(
        survey,
        question=question or None,
        text=text or None,
        suggest_id=suggest_id or None,
        parent_id=parent_id or None,
    )
    Serializer.serialize(result, app_ctx.strategy, app_ctx.console)
