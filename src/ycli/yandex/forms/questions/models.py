"""Pydantic models for Forms questions.

Two families live here:

* **Read** — the lenient ``Question`` / ``Page`` / ``QuestionsResponse`` envelope returned by
  ``GET …/questions`` and ``GET …/questions/{id}``: one class for all twelve types.
* **Write** — a **fully-typed discriminated union** (:data:`QuestionCreate`) over the 12 API
  question schemas, tagged by ``type``. The same body serves ``POST …/questions`` (create) and
  ``PATCH …/questions/{id}`` (modify); ``QuestionMove`` types the ``/move`` body. Every field
  carries a ``Field(description=…)`` so the shape is self-documenting.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field, TypeAdapter

from ycli.yandex.forms.images.models import Image
from ycli.yandex.forms.models import ConditionsResponse, FileCheckStatus
from ycli.yandex.models import IGNORED_BY_API, APIModel, RequestBody, WarnsOnIgnored

#: What happens to ``force`` of a question delete: the API takes the parameter and ignores it.
FORCE_IGNORED = "a question that a display condition refers to is refused all the same."


class Question(APIModel):
    """A single question / form field.

    Serves both ``GET …/questions`` (``pages[].items[]``) and ``GET …/questions/{id}``
    (a single question's settings). ``id`` is an **int**. One class reads all twelve
    question types: the fields a type does not have stay ``None``. ``items`` holds the options
    of an ``enum`` question and the sub-questions of a ``series``.

    Examples:
        >>> Question.model_validate({"id": 1, "slug": "s", "type": "string", "label": "L"}).slug
        's'
    """

    id: int | None = Field(default=None, description="Question ID (integer).")
    label: str | None = Field(default=None, description="Question label / title.")
    slug: str | None = Field(
        default=None, description="Stable machine slug (also the answers-table column key)."
    )
    type: str | None = Field(
        default=None,
        description="Question type — string, boolean, integer, date, daterange, file, enum, "
        "suggest, matrix, comment, payment, series, ….",
    )
    hidden: bool | None = Field(
        default=None,
        description="Whether the question is hidden (shown only when its conditions match).",
    )
    comment: str | None = Field(default=None, description="Question hint / helper text.")
    placeholder: str | None = Field(
        default=None, description="Placeholder text shown in the empty input."
    )
    initial: Any = Field(
        default=None,
        description="Default / initial value; type varies by question type (string, int, bool, "
        "or a list of enum items).",
    )
    multiline: bool | None = Field(
        default=None, description="Whether a text answer spans multiple lines (string questions)."
    )
    has_quiz: bool | None = Field(
        default=None, description="Whether the question is graded as part of a quiz / test."
    )
    conditions: ConditionsResponse | None = Field(
        default=None, description="Conditions under which the question is shown."
    )
    image: Image | None = Field(default=None, description="Image shown with the question.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules of the answer."
    )
    hint_source: QuestionHintSource | None = Field(
        default=None, description="Source of the input hints (string questions)."
    )
    quiz_items: list[QuestionQuizItem] | None = Field(
        default=None, description="Graded answers of a text quiz question."
    )
    quiz_comment: QuestionQuizComment | None = Field(
        default=None, description="Comments shown for a right and a wrong quiz answer."
    )
    header: bool | None = Field(
        default=None, description="Whether a comment block is shown as a heading."
    )
    fixed: bool | None = Field(
        default=None, description="Whether the payment amount is fixed (payment questions)."
    )
    account_id: str | None = Field(
        default=None, description="Wallet that receives the payment (payment questions)."
    )
    widget: WidgetType | None = Field(
        default=None,
        description="How the options are shown: radio, checkbox, dropdown, stars or onerow.",
    )
    items: list[QuestionItem] | None = Field(
        default=None,
        description="Options of an enum question, or the sub-questions of a series.",
    )
    modify_choices: ModifyChoicesType | None = Field(
        default=None, description="Order of the options: natural, sort or shuffle."
    )
    show_first: bool | None = Field(
        default=None, description="Whether the first option is shown preselected."
    )
    data_source: QuestionDataSource | None = Field(
        default=None, description="Where a suggest question takes its values."
    )
    multichoice: bool | None = Field(
        default=None, description="Whether several values may be chosen (suggest questions)."
    )
    rows: list[QuestionMatrixRow] | None = Field(default=None, description="Rows of a matrix.")
    columns: list[QuestionMatrixRow] | None = Field(
        default=None, description="Columns of a matrix."
    )


class QuestionItem(Question):
    """An item of a question: an option of an ``enum``, or a sub-question of a ``series``.

    An option has ``id``, ``slug``, ``label``, ``hidden``, ``image`` and, in a quiz, ``correct``
    and ``scores``; a sub-question is a whole question, with its ``type``.

    Examples:
        >>> QuestionItem.model_validate({"id": 5, "label": "Yes", "correct": True}).correct
        True
    """

    correct: bool | None = Field(
        default=None, description="Whether the option is the right answer of a quiz."
    )
    scores: float | None = Field(default=None, description="Points the option gives in a quiz.")


class Page(APIModel):
    """A page grouping questions (``…/questions`` → ``pages[]``).

    Examples:
        >>> Page.model_validate({"id": 7, "items": [{"id": 1}]}).items[0].id
        1
    """

    id: int | None = Field(default=None, description="Page ID (integer).")
    items: list[Question] = Field(
        default_factory=list, description="Questions grouped on this page, in display order."
    )


class QuestionsResponse(APIModel):
    """Envelope for ``GET …/questions`` — ``{pages:[Page]}``.

    Examples:
        >>> QuestionsResponse.model_validate({"pages": [{"items": [{"id": 1}]}]}).pages[0].items[
        ...     0
        ... ].id
        1
    """

    pages: list[Page] = Field(
        default_factory=list, description="Form pages, each grouping a set of questions."
    )


# --------------------------------------------------------------------------------------------
# Write bodies — the fully-typed discriminated union over the 12 question schemas.
# --------------------------------------------------------------------------------------------

WidgetType = Literal["radio", "checkbox", "dropdown", "stars", "onerow"] | str
ModifyChoicesType = Literal["", "natural", "sort", "shuffle"] | str
ValidatorType = (
    Literal[
        "required",
        "min",
        "max",
        "email",
        "url",
        "phone",
        "inn",
        "decimal",
        "russian",
        "regexp",
        "external",
        "size",
        "count",
        "single",
    ]
    | str
)


class QuestionValidator(APIModel):
    """One answer-validation rule (an item of a question's ``validators`` list).

    ``type`` selects the rule; ``value`` carries its argument where the rule needs one —
    an int (``min``/``max`` length or number, ``size``/``count``), a float, or a string
    (a ``min``/``max`` date ``YYYY-MM-DD``, a ``regexp`` pattern). Rules like ``required``,
    ``email``, ``url``, ``phone``, ``inn``, ``single`` take no ``value``.

    Examples:
        >>> QuestionValidator(type="min", value=3).value
        3
    """

    type: ValidatorType = Field(description="Validation rule kind, e.g. required, min, max, email.")
    value: int | float | str | None = Field(
        default=None, description="Rule argument (length/number, date string, or regexp pattern)."
    )


class QuestionImage(RequestBody):
    """An image attached to a question (or an enum option).

    Examples:
        >>> QuestionImage(id=5, name="cover.png").id
        5
    """

    id: int | None = Field(default=None, description="Image ID (from an image upload).")
    name: str | None = Field(default=None, description="Original image file name.")
    links: dict[str, Any] | None = Field(
        default=None, description="Map of links to the rendered image sizes."
    )
    check_status: FileCheckStatus | None = Field(
        default=None, description="Upload/scan status: check, ready, infected, error, deleted."
    )


class DataSourceParam(APIModel):
    """One parameter of a hint- or suggest-data-source descriptor.

    Examples:
        >>> DataSourceParam(type="org", value="42").value
        '42'
    """

    type: str | None = Field(default=None, description="Parameter name/type.")
    value: str | None = Field(default=None, description="Parameter value.")


class QuestionHintSource(APIModel):
    """A named source that supplies a string question's hint/autocomplete.

    Examples:
        >>> QuestionHintSource(name="src", params=[DataSourceParam(value="x")]).name
        'src'
    """

    name: str | None = Field(default=None, description="Hint-source name.")
    params: list[DataSourceParam] | None = Field(
        default=None, description="Hint-source parameters."
    )


class QuestionDataSource(APIModel):
    """The external data source backing a ``suggest`` question's options.

    Live-verified source names: ``city`` and ``country`` (the API rejects other names with
    400 "incorrect data source").

    Examples:
        >>> QuestionDataSource(name="city").name
        'city'
    """

    name: str | None = Field(
        default=None, description="Data-source name — ``city`` or ``country``."
    )
    params: list[DataSourceParam] | None = Field(
        default=None, description="Data-source parameters."
    )


class QuestionQuizItem(APIModel):
    """One graded answer option (string/enum quiz mode).

    Examples:
        >>> QuestionQuizItem(label="A", correct=True, scores=1.0).correct
        True
    """

    label: str | None = Field(default=None, description="Answer option text.")
    correct: bool | None = Field(default=None, description="Whether this option is correct.")
    scores: float | None = Field(default=None, description="Points awarded for this option.")


class QuestionEnumItem(RequestBody):
    """One selectable option of an ``enum`` (radio/checkbox/dropdown/stars) question.

    Examples:
        >>> QuestionEnumItem(slug="opt1", label="Option 1").slug
        'opt1'
    """

    id: int | None = Field(default=None, description="Option ID (integer).")
    slug: str | None = Field(default=None, description="Stable machine slug of the option.")
    label: str | None = Field(default=None, description="Option text shown to the respondent.")
    hidden: bool | None = Field(default=None, description="Whether the option is hidden.")
    image: QuestionImage | None = Field(default=None, description="Image shown for the option.")
    correct: bool | None = Field(
        default=None, description="Whether the option is a correct answer (quiz mode)."
    )
    scores: float | None = Field(
        default=None, description="Points awarded for the option (quiz mode)."
    )


class QuestionQuizComment(APIModel):
    """What a quiz question says after a right and after a wrong answer (``quiz_comment``).

    Examples:
        >>> QuestionQuizComment(correct="Right!").correct
        'Right!'
    """

    correct: str | None = Field(default=None, description="Comment for a right answer.")
    incorrect: str | None = Field(default=None, description="Comment for a wrong answer.")


class QuestionMatrixRow(APIModel):
    """One row (or column) of a ``matrix`` question's grid.

    Examples:
        >>> QuestionMatrixRow(slug="r1", label="Row 1").label
        'Row 1'
    """

    id: int | None = Field(default=None, description="Row/column ID (integer).")
    slug: str | None = Field(default=None, description="Stable machine slug of the row/column.")
    label: str | None = Field(default=None, description="Row/column text.")


class _QuestionBase(WarnsOnIgnored):
    """Fields shared by every question type (the discriminated-union member base).

    Concrete members add a ``Literal`` ``type`` tag (the union discriminator) plus their own
    type-specific fields. Unset (``None``) fields are dropped before the request is sent.
    Display conditions are not part of the write body (no ``Question*In`` schema has them);
    manage them through the ``conditions`` resource (``forms conditions …``).
    """

    id: int | None = Field(
        default=None,
        description=IGNORED_BY_API + "a new question gets its own id, and an existing one is "
        "named in the path.",
    )
    label: str | None = Field(default=None, description="Question label / title.")
    slug: str | None = Field(default=None, description="Stable machine slug.")
    comment: str | None = Field(default=None, description="Question hint / helper text.")
    placeholder: str | None = Field(
        default=None, description="Placeholder text shown in the empty input."
    )
    hidden: bool | None = Field(
        default=None, description="Hide the question until its display conditions match."
    )
    image: QuestionImage | None = Field(
        default=None, description="Image shown alongside the question."
    )


class StringQuestion(_QuestionBase):
    """Free-text answer (single- or multi-line). Validators add email/url/phone/inn/… masks.

    Examples:
        >>> StringQuestion(label="Name", multiline=False).type
        'string'
    """

    type: Literal["string"] = Field(default="string", description="Discriminator: string.")
    initial: str | None = Field(default=None, description="Default text value.")
    multiline: bool | None = Field(default=None, description="Allow a multi-line answer.")
    hint_source: QuestionHintSource | None = Field(
        default=None, description="Source supplying autocomplete hints."
    )
    has_quiz: bool | None = Field(default=None, description="Grade the answer as a quiz item.")
    quiz_items: list[QuestionQuizItem] | None = Field(
        default=None, description="Accepted correct answers (quiz mode)."
    )
    quiz_comment: QuestionQuizComment | None = Field(
        default=None, description="Comments shown for a right and a wrong quiz answer."
    )
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min/max length, email, url, …)."
    )


class BooleanQuestion(_QuestionBase):
    """Yes/no (single checkbox) answer.

    Examples:
        >>> BooleanQuestion(label="Agree", initial=False).type
        'boolean'
    """

    type: Literal["boolean"] = Field(default="boolean", description="Discriminator: boolean.")
    initial: bool | None = Field(default=None, description="Default boolean value.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, external)."
    )


class IntegerQuestion(_QuestionBase):
    """Whole-number answer, optionally bounded by min/max validators.

    Examples:
        >>> IntegerQuestion(label="Age", initial=18).type
        'integer'
    """

    type: Literal["integer"] = Field(default="integer", description="Discriminator: integer.")
    initial: int | None = Field(default=None, description="Default integer value.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min, max, external)."
    )


class FileQuestion(_QuestionBase):
    """File-upload answer, optionally bounded by size/count validators.

    Examples:
        >>> FileQuestion(label="Attach").type
        'file'
    """

    type: Literal["file"] = Field(default="file", description="Discriminator: file.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, size, count, external)."
    )


class CommentQuestion(_QuestionBase):
    """A static text / header block (no answer collected).

    Examples:
        >>> CommentQuestion(label="Section A", header=True).header
        True
    """

    type: Literal["comment"] = Field(default="comment", description="Discriminator: comment.")
    header: bool | None = Field(
        default=None, description="Render the text as a section header rather than body copy."
    )


class DateQuestion(_QuestionBase):
    """Single-date answer, optionally bounded by min/max date validators.

    Examples:
        >>> DateQuestion(label="Born").type
        'date'
    """

    type: Literal["date"] = Field(default="date", description="Discriminator: date.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min/max date, external)."
    )


class DateRangeQuestion(_QuestionBase):
    """Date-range (from/to) answer, optionally bounded by min/max date validators.

    Examples:
        >>> DateRangeQuestion(label="Period").type
        'daterange'
    """

    type: Literal["daterange"] = Field(default="daterange", description="Discriminator: daterange.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min/max date, external)."
    )


class PaymentQuestion(_QuestionBase):
    """A payment field (amount to a wallet), optionally fixed or bounded by min/max.

    Examples:
        >>> PaymentQuestion(label="Donate", account_id="410011", fixed=False).account_id
        '410011'
    """

    type: Literal["payment"] = Field(default="payment", description="Discriminator: payment.")
    account_id: str | None = Field(default=None, description="Wallet number receiving the payment.")
    fixed: bool | None = Field(
        default=None, description="Whether the respondent may change the amount."
    )
    initial: int | None = Field(default=None, description="Default payment amount.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min, max)."
    )


class EnumQuestion(_QuestionBase):
    """Choice from a fixed option list (radio/checkbox/dropdown/stars/onerow).

    Examples:
        >>> EnumQuestion(label="Pick", widget="radio", items=[QuestionEnumItem(label="A")]).widget
        'radio'
    """

    type: Literal["enum"] = Field(default="enum", description="Discriminator: enum.")
    widget: WidgetType | None = Field(
        default=None, description="Display style: radio, checkbox, dropdown, stars, onerow."
    )
    items: list[QuestionEnumItem] | None = Field(
        default=None, description="The selectable options."
    )
    initial: list[QuestionEnumItem] | None = Field(
        default=None, description="Pre-selected options."
    )
    modify_choices: ModifyChoicesType | None = Field(
        default=None, description="Option ordering: '' (as given), natural, sort, shuffle."
    )
    show_first: bool | None = Field(
        default=None, description="Show the first value (dropdown widget)."
    )
    has_quiz: bool | None = Field(default=None, description="Grade the choice as a quiz item.")
    quiz_comment: QuestionQuizComment | None = Field(
        default=None, description="Comments shown for a right and a wrong quiz answer."
    )
    show_suggest: bool | None = Field(
        default=None, description="Offer the options as suggestions while the respondent types."
    )
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, single, external)."
    )


class SuggestQuestion(_QuestionBase):
    """Autocomplete/suggest answer backed by an external data source.

    Examples:
        >>> SuggestQuestion(label="Dept", data_source=QuestionDataSource(name="departments")).type
        'suggest'
    """

    type: Literal["suggest"] = Field(default="suggest", description="Discriminator: suggest.")
    multichoice: bool | None = Field(default=None, description="Allow selecting several values.")
    data_source: QuestionDataSource | None = Field(
        default=None, description="External source of suggestions."
    )
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, external)."
    )


class MatrixQuestion(_QuestionBase):
    """A grid of rows scored against a shared set of columns.

    Examples:
        >>> MatrixQuestion(label="Grid", rows=[QuestionMatrixRow(label="R")]).type
        'matrix'
    """

    type: Literal["matrix"] = Field(default="matrix", description="Discriminator: matrix.")
    rows: list[QuestionMatrixRow] | None = Field(default=None, description="Grid rows.")
    columns: list[QuestionMatrixRow] | None = Field(default=None, description="Grid columns.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, external)."
    )


class SeriesQuestion(_QuestionBase):
    """A repeatable group nesting other questions (each item is itself a typed question).

    The API accepts ``items`` and ignores them (checked live on 2026-10-04): the series comes
    back empty.

    Examples:
        >>> SeriesQuestion(label="People").type
        'series'
    """

    type: Literal["series"] = Field(default="series", description="Discriminator: series.")
    items: list[QuestionCreate] | None = Field(
        default=None,
        description=IGNORED_BY_API + "a series is created with no questions in it.",
    )


QuestionCreate = Annotated[
    StringQuestion
    | BooleanQuestion
    | IntegerQuestion
    | FileQuestion
    | CommentQuestion
    | DateQuestion
    | DateRangeQuestion
    | PaymentQuestion
    | EnumQuestion
    | SuggestQuestion
    | MatrixQuestion
    | SeriesQuestion,
    Field(discriminator="type"),
]
"""Discriminated union over the 12 question schemas, tagged by ``type`` — the write body for
``POST …/questions`` (create) and ``PATCH …/questions/{id}`` (modify)."""

# ``SeriesQuestion.items`` forward-references the union defined just above — resolve it now that
# every name is in the module namespace.
SeriesQuestion.model_rebuild()
# The read models name classes defined below them, and the ones that hold a ``Question`` wait
# with it. Pydantic would finish each at its first validation, but an MCP tool serializes with
# a serializer it took when the tool was registered, before any reply was read.
Question.model_rebuild()
QuestionItem.model_rebuild()
Page.model_rebuild()
QuestionsResponse.model_rebuild()

#: Runtime validator that routes a raw dict to the right member by its ``type`` tag.
QuestionCreateAdapter: TypeAdapter[Any] = TypeAdapter(QuestionCreate)


class QuestionMove(RequestBody):
    """Typed body for ``POST …/questions/{id}/move`` — where to reposition the question.

    A bare ``position`` with no page target is a **silent no-op** live: the API answers 200
    but moves nothing. The body is sent as it is given; give a target (``page`` / ``page_id`` /
    ``create_page`` / ``question``) with the position. The CLI ``move`` command defaults
    ``page`` to 1 for a bare ``--position``.

    Examples:
        >>> QuestionMove(page=2, position=1).position
        1
        >>> QuestionMove(position=1).page is None
        True
    """

    question: int | str | None = Field(
        default=None, description="Question id or slug to move into a question series."
    )
    page: int | None = Field(
        default=None,
        description="Target page number (1-based). Required (or another target) when "
        "``position`` is set — the API silently ignores a bare position.",
    )
    page_id: int | None = Field(default=None, description="Target page ID.")
    create_page: bool | None = Field(
        default=None, description="Create a new page for the question (used with ``page``)."
    )
    position: int | None = Field(
        default=None, description="New position of the question on the page (1-based)."
    )


class QuestionMoveResult(APIModel):
    """Result of ``POST …/questions/{id}/move`` — the moved question's id.

    Examples:
        >>> QuestionMoveResult(id=17).id
        17
    """

    id: int | None = Field(default=None, description="ID of the moved question.")
