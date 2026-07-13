"""`forms questions` commands (reads + writes; writes also ship as MCP tools)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.questions.models import (
    BooleanQuestion,
    DateQuestion,
    EnumQuestion,
    IntegerQuestion,
    QuestionCreate,
    QuestionCreateAdapter,
    QuestionEnumItem,
    QuestionMove,
    QuestionValidator,
    StringQuestion,
)
from ycli.yandex.forms.typedefs import (
    QuestionIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="questions", help="Forms questions.", no_args_is_help=True)


def _build_from_flags(
    type_: str,
    *,
    label: str,
    slug: str,
    comment: str,
    placeholder: str,
    required: bool,
    hidden: bool,
    multiline: bool,
    widget: str,
    options: list[str] | None,
) -> QuestionCreate:
    """Build a typed question from the common ``--type`` flags (string/boolean/integer/date/enum).

    Raises ``typer.BadParameter`` for the richer types (matrix/series/suggest/payment/…), which
    are reachable only via ``--body-file``.

    Example:
        >>> _build_from_flags(
        ...     "string",
        ...     label="Name",
        ...     slug="",
        ...     comment="",
        ...     placeholder="",
        ...     required=True,
        ...     hidden=False,
        ...     multiline=True,
        ...     widget="",
        ...     options=None,
        ... ).multiline
        True
    """
    common: dict[str, Any] = {
        "label": label or None,
        "slug": slug or None,
        "comment": comment or None,
        "placeholder": placeholder or None,
        "hidden": hidden or None,
    }
    validators = [QuestionValidator(type="required")] if required else None
    if type_ == "string":
        return StringQuestion(**common, multiline=multiline or None, validators=validators)
    if type_ == "boolean":
        return BooleanQuestion(**common, validators=validators)
    if type_ == "integer":
        return IntegerQuestion(**common, validators=validators)
    if type_ == "date":
        return DateQuestion(**common, validators=validators)
    if type_ == "enum":
        items = [QuestionEnumItem(label=text) for text in options or []]
        return EnumQuestion(
            **common,
            widget=widget or None,  # ty: ignore[invalid-argument-type]  # pydantic validates the widget literal
            items=items or None,
            validators=validators,
        )
    raise typer.BadParameter(
        f"--type {type_!r} has no typed flags; pass --body-file with a full JSON body"
    )


def _resolve_body(
    type_: str,
    label: str,
    slug: str,
    comment: str,
    placeholder: str,
    required: bool,
    hidden: bool,
    multiline: bool,
    widget: str,
    options: list[str] | None,
    body_file: Path | None,
) -> QuestionCreate:
    """Pick the write body: a ``--body-file`` JSON validated through the union, else typed flags."""
    if body_file is not None:
        data = json.loads(body_file.read_text(encoding="utf-8"))
        return QuestionCreateAdapter.validate_python(data)
    if not type_:
        raise typer.BadParameter("pass --type (with flags) or --body-file")
    return _build_from_flags(
        type_,
        label=label,
        slug=slug,
        comment=comment,
        placeholder=placeholder,
        required=required,
        hidden=hidden,
        multiline=multiline,
        widget=widget,
        options=options,
    )


TypeOpt = Annotated[
    str, typer.Option("--type", help="Question type: string/boolean/integer/date/enum.")
]
LabelOpt = Annotated[str, typer.Option(help="Question label / title.")]
SlugOpt = Annotated[str, typer.Option(help="Stable machine slug.")]
CommentOpt = Annotated[str, typer.Option(help="Question hint / helper text.")]
PlaceholderOpt = Annotated[str, typer.Option(help="Placeholder text.")]
RequiredOpt = Annotated[bool, typer.Option("--required", help="Mark the answer as required.")]
HiddenOpt = Annotated[bool, typer.Option("--hidden", help="Hide until conditions match.")]
MultilineOpt = Annotated[bool, typer.Option("--multiline", help="Multiline text (string type).")]
WidgetOpt = Annotated[str, typer.Option(help="Enum widget: radio/checkbox/dropdown/stars/onerow.")]
OptionOpt = Annotated[
    list[str] | None, typer.Option("--option", help="Enum option label (repeatable).")
]
BodyFileOpt = Annotated[
    Path | None,
    typer.Option(
        "--body-file",
        help="JSON file with the full question body (validated through the typed union); "
        "use for matrix/series/suggest/payment/daterange.",
    ),
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(ctx: typer.Context, survey_id: SurveyIdArg) -> None:
    """List a form's questions (the {pages} envelope)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(app_ctx.forms.questions.list(survey_id), app_ctx.strategy, app_ctx.console)


@app.command()
def get(ctx: typer.Context, survey_id: SurveyIdArg, question_id: QuestionIdArg) -> None:
    """Print one question's settings (SURVEY_ID / QUESTION_ID)."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.questions.get(survey_id, question_id), app_ctx.strategy, app_ctx.console
    )


@app.command()
def create(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    type_: TypeOpt = "",
    label: LabelOpt = "",
    slug: SlugOpt = "",
    comment: CommentOpt = "",
    placeholder: PlaceholderOpt = "",
    required: RequiredOpt = False,
    hidden: HiddenOpt = False,
    multiline: MultilineOpt = False,
    widget: WidgetOpt = "",
    option: OptionOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Create a question (POST …/questions). Use --type + flags, or --body-file for full JSON."""
    payload = _resolve_body(
        type_,
        label,
        slug,
        comment,
        placeholder,
        required,
        hidden,
        multiline,
        widget,
        option,
        body_file,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.questions.create(survey_id, payload), app_ctx.strategy, app_ctx.console
    )


@app.command()
def modify(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    type_: TypeOpt = "",
    label: LabelOpt = "",
    slug: SlugOpt = "",
    comment: CommentOpt = "",
    placeholder: PlaceholderOpt = "",
    required: RequiredOpt = False,
    hidden: HiddenOpt = False,
    multiline: MultilineOpt = False,
    widget: WidgetOpt = "",
    option: OptionOpt = None,
    body_file: BodyFileOpt = None,
) -> None:
    """Modify a question (PATCH …/questions/{id}) — --type + flags, or --body-file for full JSON."""
    payload = _resolve_body(
        type_,
        label,
        slug,
        comment,
        placeholder,
        required,
        hidden,
        multiline,
        widget,
        option,
        body_file,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.questions.modify(survey_id, question_id, payload),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def delete(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    force: Annotated[
        bool, typer.Option("--force", help="Skip the condition-usage check before deleting.")
    ] = False,
) -> None:
    """Delete a question (DELETE …/questions/{id}); --force skips the condition-usage check."""
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.questions.delete(survey_id, question_id, force=force),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command()
def move(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    page: Annotated[
        int,
        typer.Option(
            help="Target page number, 1-based (0 = unset; defaults to 1 when only "
            "--position is given — the API silently ignores a bare position)."
        ),
    ] = 0,
    page_id: Annotated[int, typer.Option("--page-id", help="Target page id (0 = unset).")] = 0,
    position: Annotated[
        int, typer.Option(help="New position on the page, 1-based (0 = unset).")
    ] = 0,
    create_page: Annotated[
        bool, typer.Option("--create-page", help="Create a new page for the question.")
    ] = False,
    question: Annotated[
        str, typer.Option(help="Question id/slug to move into a question series.")
    ] = "",
) -> None:
    """Move a question (POST …/questions/{id}/move) to another page / position.

    ``--position`` without a page target would be silently ignored by the API (200, nothing
    moves), so ``--page`` defaults to 1 in that case.
    """
    payload = QuestionMove(
        question=question or None,
        page=page or None,
        page_id=page_id or None,
        position=position or None,
        create_page=create_page or None,
    )
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.questions.move(survey_id, question_id, payload),
        app_ctx.strategy,
        app_ctx.console,
    )
