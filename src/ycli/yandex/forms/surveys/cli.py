"""`forms surveys` commands (reads + writes; writes also ship as MCP tools)."""

from __future__ import annotations

from typing import Annotated, Any

import typer

from ycli.cli.fields import parse_fields
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.surveys.models import Survey, SurveyCreate, SurveyUpdate
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,
)
from ycli.yandex.models import Ack, ItemList

app = typer.Typer(name="surveys", help="Forms surveys.", no_args_is_help=True)

FieldOpt = Annotated[
    list[str] | None,
    typer.Option("--field", "-F", help="Advanced key=value (JSON-coerced; repeatable)."),
]


def _given(named: dict[str, Any], field: list[str] | None) -> dict[str, Any]:
    """The options that were given, then whatever ``--field`` adds or overrides."""
    return {name: value for name, value in named.items() if value is not None} | parse_fields(field)


def _body_help(field: str) -> str:
    """The description of a ``SurveyCreate`` field, so an option says what the model says."""
    return SurveyCreate.model_fields[field].description or ""


# Options the API accepts and ignores: kept, and each says so (docs/conventions/resources.md).
LanguageOpt = Annotated[str | None, typer.Option(help=_body_help("language"))]
PublishedOpt = Annotated[
    bool | None, typer.Option("--published/--no-published", help=_body_help("is_published"))
]
PublicOpt = Annotated[
    bool | None, typer.Option("--public/--no-public", help=_body_help("is_public"))
]


@app.command("list")
def list_(
    limit: LimitOption = None,
    all_: AllOption = False,
    name: Annotated[str | None, typer.Option(help="Only forms whose name matches.")] = None,
    published: Annotated[
        bool | None,
        typer.Option("--published/--no-published", help="Only published (or only unpublished)."),
    ] = None,
    ownership: Annotated[
        str | None, typer.Option(help="mine (created by you) or shared (open to you).")
    ] = None,
    group: Annotated[str | None, typer.Option(help="Only forms of this group.")] = None,
    favourite: Annotated[
        bool | None,
        typer.Option("--favourite/--no-favourite", help="Only favourites (or only the others)."),
    ] = None,
    show_all: Annotated[
        bool,
        typer.Option("--show-all", help="As an administrator, every form of the organization."),
    ] = False,
    orderby: Annotated[
        str | None, typer.Option("--orderby", help="Sort, e.g. name,-modified,-count.")
    ] = None,
    *,
    config: AppConfig,
    forms: FormsClient,
) -> ItemList[Survey]:
    """List forms, filtered (auto-paginated over offset pages; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return forms.surveys.list(
        limit=cap,
        name=name,
        published=published,
        ownership=ownership,
        group=group,
        favourite=favourite,
        show_all=show_all,
        orderby=orderby,
    )


@app.command()
def get(survey_id: SurveyIdArg, *, forms: FormsClient) -> Survey:
    """Print one form's settings for SURVEY_ID."""
    return forms.surveys.get(survey_id)


@app.command()
def create(
    name: Annotated[str, typer.Option(help="Form name (title).")],
    language: LanguageOpt = None,
    published: PublishedOpt = None,
    public: PublicOpt = None,
    need_auth: Annotated[
        bool | None, typer.Option("--need-auth/--no-need-auth", help="Require sign-in to fill.")
    ] = None,
    max_count: Annotated[
        int | None, typer.Option(help="Maximum number of responses (0: no cap).")
    ] = None,
    field: FieldOpt = None,
    *,
    forms: FormsClient,
) -> Survey:
    """Create a form (POST /surveys). Advanced keys via --field; returns the created form."""
    named = {
        "name": name,
        "language": language,
        "is_published": published,
        "is_public": public,
        "need_auth": need_auth,
        "max_count": max_count,
    }
    return forms.surveys.create(body=SurveyCreate.model_validate(_given(named, field)))


@app.command()
def update(
    survey_id: SurveyIdArg,
    name: Annotated[str | None, typer.Option(help="New form name.")] = None,
    language: LanguageOpt = None,
    published: PublishedOpt = None,
    public: PublicOpt = None,
    need_auth: Annotated[
        bool | None, typer.Option("--need-auth/--no-need-auth", help="Toggle sign-in requirement.")
    ] = None,
    max_count: Annotated[
        int | None, typer.Option(help="New response cap (0 removes the cap).")
    ] = None,
    field: FieldOpt = None,
    *,
    forms: FormsClient,
) -> Survey:
    """Modify form SURVEY_ID (PATCH /surveys/{id}) — only supplied fields are sent."""
    named = {
        "name": name,
        "language": language,
        "is_published": published,
        "is_public": public,
        "need_auth": need_auth,
        "max_count": max_count,
    }
    return forms.surveys.update(survey_id, body=SurveyUpdate.model_validate(_given(named, field)))


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
