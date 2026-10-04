"""`forms questions` commands (reads + writes; writes also ship as MCP tools)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer

from ycli.cli.typedefs import values_option
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.questions.models import (
    FORCE_IGNORED,
    Question,
    QuestionCreate,
    QuestionCreateAdapter,
    QuestionMove,
    QuestionMoveResult,
    QuestionsResponse,
    QuestionValidator,
    WidgetType,
)
from ycli.yandex.forms.typedefs import (
    QuestionIdArg,
    SurveyIdArg,
)
from ycli.yandex.models import IGNORED_BY_API, Ack

app = typer.Typer(name="questions", help="Forms questions.", no_args_is_help=True)


# The question types the flags can build; the richer ones take ``--body-file``.
FlagQuestionType = Literal["string", "boolean", "integer", "date", "enum"]


def _build_from_flags(
    type_: str | None,
    *,
    label: str | None,
    slug: str | None,
    comment: str | None,
    placeholder: str | None,
    required: bool | None,
    hidden: bool | None,
    multiline: bool | None,
    widget: str | None,
    options: list[str] | None,
) -> QuestionCreate:
    """Build a typed question from the common ``--type`` flags (string/boolean/integer/date/enum).

    Raises ``typer.BadParameter`` for the richer types (matrix/series/suggest/payment/…), which
    are reachable only via ``--body-file``.

    Examples:
        >>> _build_from_flags(
        ...     "string",
        ...     label="Name",
        ...     slug=None,
        ...     comment=None,
        ...     placeholder=None,
        ...     required=True,
        ...     hidden=False,
        ...     multiline=True,
        ...     widget=None,
        ...     options=None,
        ... ).multiline
        True
    """
    # The flags carry only the ``required`` rule, so they set the whole validators list:
    # --required sends [required], --no-required sends [] (clearing every rule), unset sends none.
    validators: list[QuestionValidator] | None = None
    if required is not None:
        validators = [QuestionValidator(type="required")] if required else []
    given = {
        "type": type_,
        "label": label,
        "slug": slug,
        "comment": comment,
        "placeholder": placeholder,
        "hidden": hidden,
        "multiline": multiline,
        "widget": widget,
        "items": [{"label": text} for text in options] if options else None,
        "validators": validators,
    }
    # The union picks the class by ``type`` and refuses a flag that type does not take.
    return QuestionCreateAdapter.validate_python(
        {name: value for name, value in given.items() if value is not None}
    )


def _resolve_body(
    type_: str | None,
    label: str | None,
    slug: str | None,
    comment: str | None,
    placeholder: str | None,
    required: bool | None,
    hidden: bool | None,
    multiline: bool | None,
    widget: str | None,
    options: list[str] | None,
    body_file: Path | None,
) -> QuestionCreate:
    """Pick the write body: a ``--body-file`` JSON validated through the union, else typed flags."""
    if body_file is not None:
        return QuestionCreateAdapter.validate_json(body_file.read_bytes())
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
    FlagQuestionType | None,
    typer.Option("--type", help="Question type the flags can build; others take --body-file."),
]
LabelOpt = Annotated[str | None, typer.Option(help="Question label / title.")]
SlugOpt = Annotated[str | None, typer.Option(help="Stable machine slug.")]
CommentOpt = Annotated[str | None, typer.Option(help="Question hint / helper text.")]
PlaceholderOpt = Annotated[str | None, typer.Option(help="Placeholder text.")]
RequiredOpt = Annotated[
    bool | None,
    typer.Option(
        "--required/--no-required",
        help="Answer required or not (sets the whole validators list: [required] or []).",
    ),
]
HiddenOpt = Annotated[
    bool | None, typer.Option("--hidden/--no-hidden", help="Hide until conditions match.")
]
MultilineOpt = Annotated[
    bool | None, typer.Option("--multiline/--no-multiline", help="Multiline text (string type).")
]
WidgetOpt = Annotated[
    str | None, values_option(WidgetType, help="How an enum question shows its options.")
]
OptionOpt = Annotated[
    list[str] | None, typer.Option("--option", help="Enum option label (repeatable).")
]
BodyFileOpt = Annotated[
    Path | None,
    typer.Option(
        "--body-file",
        exists=True,
        dir_okay=False,
        readable=True,
        help="JSON file with the full question body (validated through the typed union); "
        "use for matrix/series/suggest/payment/daterange.",
    ),
]


@app.command("list")
def list_(survey_id: SurveyIdArg, *, forms: FormsClient) -> QuestionsResponse:
    """List a form's questions (the {pages} envelope)."""
    return forms.questions.list(survey_id)


@app.command()
def get(
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    with_slugs: Annotated[
        bool, typer.Option("--with-slugs", help="Refer to other questions by slug, not id.")
    ] = False,
    *,
    forms: FormsClient,
) -> Question:
    """Print one question's settings (SURVEY_ID / QUESTION_ID)."""
    return forms.questions.get(survey_id, question_id, with_slugs=with_slugs)


@app.command()
def create(
    survey_id: SurveyIdArg,
    type_: TypeOpt = None,
    label: LabelOpt = None,
    slug: SlugOpt = None,
    comment: CommentOpt = None,
    placeholder: PlaceholderOpt = None,
    required: RequiredOpt = None,
    hidden: HiddenOpt = None,
    multiline: MultilineOpt = None,
    widget: WidgetOpt = None,
    option: OptionOpt = None,
    body_file: BodyFileOpt = None,
    *,
    forms: FormsClient,
) -> Question:
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
    return forms.questions.create(survey_id, payload)


@app.command()
def update(
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    type_: TypeOpt = None,
    label: LabelOpt = None,
    slug: SlugOpt = None,
    comment: CommentOpt = None,
    placeholder: PlaceholderOpt = None,
    required: RequiredOpt = None,
    hidden: HiddenOpt = None,
    multiline: MultilineOpt = None,
    widget: WidgetOpt = None,
    option: OptionOpt = None,
    body_file: BodyFileOpt = None,
    *,
    forms: FormsClient,
) -> Question:
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
    return forms.questions.update(survey_id, question_id, payload)


@app.command()
def delete(
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    force: Annotated[bool, typer.Option("--force", help=IGNORED_BY_API + FORCE_IGNORED)] = False,
    *,
    forms: FormsClient,
) -> Ack:
    """Delete a question (DELETE …/questions/{id}); one a condition refers to is refused."""
    return forms.questions.delete(survey_id, question_id, force=force)


@app.command()
def move(
    survey_id: SurveyIdArg,
    question_id: QuestionIdArg,
    page: Annotated[
        int | None,
        typer.Option(
            help="Target page number, 1-based (visibly defaults to 1 when only "
            "--position is given — the API silently ignores a bare position)."
        ),
    ] = None,
    page_id: Annotated[int | None, typer.Option("--page-id", help="Target page id.")] = None,
    position: Annotated[int | None, typer.Option(help="New position on the page, 1-based.")] = None,
    create_page: Annotated[
        bool, typer.Option("--create-page", help="Create a new page for the question.")
    ] = False,
    question: Annotated[
        str | None, typer.Option(help="Question id/slug to move into a question series.")
    ] = None,
    *,
    forms: FormsClient,
) -> QuestionMoveResult:
    """Move a question (POST …/questions/{id}/move) to another page / position.

    ``--position`` without a page target is silently ignored by the API (200, nothing moves),
    so ``--page`` defaults to 1 here when only ``--position`` is given.
    """
    target_page: int | None = page
    target_page_id = page_id
    target_position = position
    target_question = question
    target_create_page = create_page or None
    no_target = (
        target_page is None
        and target_page_id is None
        and target_question is None
        and not target_create_page
    )
    if target_position is not None and no_target:
        target_page = 1  # visible default: a bare --position would otherwise 200-but-no-op live
    payload = QuestionMove(
        question=target_question,
        page=target_page,
        page_id=target_page_id,
        position=target_position,
        create_page=target_create_page,
    )
    return forms.questions.move(survey_id, question_id, payload)
