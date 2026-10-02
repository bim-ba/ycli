"""`forms surveys` commands (reads + writes; writes also ship as MCP tools)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.fields import parse_fields
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.surveys.models import Survey, SurveyCreate, SurveyList, SurveyUpdate
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,
)
from ycli.yandex.models import Ack

app = typer.Typer(name="surveys", help="Forms surveys.", no_args_is_help=True)

FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Advanced key=value (JSON-coerced; repeatable)."),
]


@app.command("list")
def list_(
    limit: LimitOption = 0, all_: AllOption = False, *, config: AppConfig, forms: FormsClient
) -> SurveyList:
    """List all forms (auto-paginated over offset pages; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return forms.surveys.list(limit=cap)


@app.command()
def get(survey_id: SurveyIdArg, *, forms: FormsClient) -> Survey:
    """Print one form's settings for SURVEY_ID."""
    return forms.surveys.get(survey_id)


@app.command()
def create(
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
    *,
    forms: FormsClient,
) -> Survey:
    """Create a form (POST /surveys). Advanced keys via --field; returns the created form."""
    payload = SurveyCreate(
        name=name,
        language=language or None,
        is_published=published,
        is_public=public,
        need_auth=need_auth,
        max_count=max_count or None,
    )
    body = payload.model_dump(exclude_none=True) | parse_fields(field)
    return forms.surveys.create(body=body)


@app.command()
def modify(
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
    *,
    forms: FormsClient,
) -> Survey:
    """Modify form SURVEY_ID (PATCH /surveys/{id}) — only supplied fields are sent."""
    payload = SurveyUpdate(
        name=name or None,
        language=language or None,
        is_published=published,
        is_public=public,
        need_auth=need_auth,
        max_count=max_count or None,
    )
    body = payload.model_dump(exclude_none=True) | parse_fields(field)
    return forms.surveys.modify(survey_id, body=body)


@app.command()
def delete(survey_id: SurveyIdArg, *, forms: FormsClient) -> Ack:
    """Delete form SURVEY_ID (DELETE /surveys/{id})."""
    return forms.surveys.delete(survey_id)


@app.command()
def publish(survey_id: SurveyIdArg, *, forms: FormsClient) -> Ack:
    """Publish form SURVEY_ID (POST /surveys/{id}/publish)."""
    return forms.surveys.publish(survey_id)


@app.command()
def unpublish(survey_id: SurveyIdArg, *, forms: FormsClient) -> Ack:
    """Unpublish form SURVEY_ID (POST /surveys/{id}/unpublish)."""
    return forms.surveys.unpublish(survey_id)
