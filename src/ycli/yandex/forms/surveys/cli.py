"""`forms surveys` commands (reads + writes; writes are CLI/SDK only, never MCP)."""

from __future__ import annotations

import json
from typing import Annotated, Any

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.forms.surveys.models import SurveyCreate, SurveyUpdate
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)
from ycli.yandex.pagination import resolve_cap

app = typer.Typer(name="surveys", help="Forms surveys.", no_args_is_help=True)

FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Advanced key=value (JSON-coerced; repeatable)."),
]


def _parse_fields(items: list[str] | None) -> dict[str, Any]:
    """Parse repeated ``--field key=value`` strings into a dict (gh ``-F`` model).

    Each value is JSON-coerced (``123`` → int, ``true`` → bool, ``{"submit":"Go"}`` → object),
    falling back to the raw string when it is not valid JSON. Raises ``typer.BadParameter`` when
    an item has no ``=``. These merge onto the typed body for advanced form keys the modelled
    options do not cover (``styles``, ``quiz``, ``texts``, ``auto_publication``, …).

    Example:
        >>> _parse_fields(["max_count=10", "language=ru"])
        {'max_count': 10, 'language': 'ru'}
    """
    out: dict[str, Any] = {}
    for item in items or []:
        key, sep, raw = item.partition("=")
        if not sep:
            raise typer.BadParameter(f"--field must be key=value, got {item!r}")
        try:
            out[key] = json.loads(raw)
        except json.JSONDecodeError:
            out[key] = raw
    return out


@app.command("list")
def list_(
    ctx: typer.Context,
    limit: LimitOption = 0,
    all_: AllOption = False,
) -> None:
    """List all forms (auto-paginated over offset pages; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(app_ctx.forms.surveys.list(limit=cap), app_ctx.strategy, app_ctx.console)


@app.command()
def get(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Print one form's settings for SURVEY_ID."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.surveys.get(survey_id), app_ctx.strategy, app_ctx.console)


@app.command()
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Form name (title).")],
    language: Annotated[str, typer.Option(help="Interface language, e.g. ru or en.")] = "",
    published: Annotated[
        bool | None, typer.Option("--published/--no-published", help="Publish on creation.")
    ] = None,
    public: Annotated[
        bool | None, typer.Option("--public/--no-public", help="Fillable without an invite.")
    ] = None,
    need_auth: Annotated[
        bool | None, typer.Option("--need-auth/--no-need-auth", help="Require sign-in to fill.")
    ] = None,
    max_count: Annotated[int, typer.Option(help="Maximum number of responses (0 = unset).")] = 0,
    field: FieldOpt = None,
) -> None:
    """Create a form (POST /surveys). Advanced keys via --field; returns the created form."""
    payload = SurveyCreate(
        name=name,
        language=language or None,
        is_published=published,
        is_public=public,
        need_auth=need_auth,
        max_count=max_count or None,
    )
    body = payload.model_dump(exclude_none=True) | _parse_fields(field)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.surveys.create(body=body), app_ctx.strategy, app_ctx.console)


@app.command()
def modify(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    name: Annotated[str, typer.Option(help="New form name.")] = "",
    language: Annotated[str, typer.Option(help="New interface language.")] = "",
    published: Annotated[
        bool | None, typer.Option("--published/--no-published", help="Publish / unpublish.")
    ] = None,
    public: Annotated[
        bool | None, typer.Option("--public/--no-public", help="Toggle public fill.")
    ] = None,
    need_auth: Annotated[
        bool | None, typer.Option("--need-auth/--no-need-auth", help="Toggle sign-in requirement.")
    ] = None,
    max_count: Annotated[int, typer.Option(help="New response cap (0 = leave unchanged).")] = 0,
    field: FieldOpt = None,
) -> None:
    """Modify form SURVEY_ID (PATCH /surveys/{id}) — only supplied fields are sent."""
    payload = SurveyUpdate(
        name=name or None,
        language=language or None,
        is_published=published,
        is_public=public,
        need_auth=need_auth,
        max_count=max_count or None,
    )
    body = payload.model_dump(exclude_none=True) | _parse_fields(field)
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.surveys.modify(survey_id, body=body), app_ctx.strategy, app_ctx.console
    )


@app.command()
def delete(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Delete form SURVEY_ID (DELETE /surveys/{id})."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.surveys.delete(survey_id), app_ctx.strategy, app_ctx.console)


@app.command()
def publish(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Publish form SURVEY_ID (POST /surveys/{id}/publish)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.surveys.publish(survey_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def unpublish(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """Unpublish form SURVEY_ID (POST /surveys/{id}/unpublish)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.surveys.unpublish(survey_id), app_ctx.strategy, app_ctx.console
    )
