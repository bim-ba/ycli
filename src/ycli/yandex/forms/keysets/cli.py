"""`forms keysets` commands (reads + writes; writes/download are CLI/SDK only, never MCP)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.binary import write_output
from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.keysets.models import KeysetCreate, KeysetUpdate
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="keysets", help="Forms personal-link key sets.", no_args_is_help=True)

KeysetIdArg = Annotated[int, typer.Argument(metavar="KEYSET_ID", help="Key set id (integer).")]
OutputOption = Annotated[
    str | None,
    typer.Option("--output", help="Write bytes to this path; omit / '-' streams to stdout."),
]


@app.command("list")
def list_(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """List key sets on form SURVEY_ID (GET /surveys/{id}/keysets)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.keysets.list(survey_id), app_ctx.strategy, app_ctx.console)


@app.command()
def get(ctx: typer.Context, survey_id: SurveyIdArg, keyset_id: KeysetIdArg) -> None:
    """Print one key set (SURVEY_ID KEYSET_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.keysets.get(survey_id, keyset_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    name: Annotated[str, typer.Option(help="Key set name.")],
    total: Annotated[int, typer.Option(help="Number of keys to generate.")],
    enabled: Annotated[
        bool | None, typer.Option("--enabled/--disabled", help="Create the set active.")
    ] = None,
) -> None:
    """Create a key set on form SURVEY_ID (POST /surveys/{id}/keysets)."""
    body = KeysetCreate(name=name, total=total, is_enabled=enabled).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.keysets.create(survey_id, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def modify(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    keyset_id: KeysetIdArg,
    name: Annotated[str, typer.Option(help="Key set name (required — replaces the record).")],
    total: Annotated[int, typer.Option(help="Number of keys (required — replaces the record).")],
    enabled: Annotated[bool, typer.Option("--enabled/--disabled", help="Active flag (required).")],
) -> None:
    """Modify key set KEYSET_ID on SURVEY_ID (PATCH) — the API replaces the whole record, so
    every field (name, total, enabled) is required and sent together."""
    body = KeysetUpdate(name=name, total=total, is_enabled=enabled).model_dump()
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.keysets.modify(survey_id, keyset_id, body=body),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(ctx: typer.Context, survey_id: SurveyIdArg, keyset_id: KeysetIdArg) -> None:
    """Delete key set KEYSET_ID on SURVEY_ID (DELETE /surveys/{id}/keysets/{keyset_id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    app_ctx.forms.keysets.delete(survey_id, keyset_id)
    print(f"deleted keyset {keyset_id} on survey {survey_id}")


@app.command()
def download(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    keyset_id: KeysetIdArg,
    output: OutputOption = None,
) -> None:
    """Download key set KEYSET_ID to --output (or stdout) as raw bytes."""
    app_ctx = AppContext.from_typer_context(ctx)
    write_output(app_ctx.forms.keysets.download(survey_id, keyset_id), output)
