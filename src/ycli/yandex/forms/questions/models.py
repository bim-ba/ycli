"""Pydantic models for Forms questions.

Two families live here:

* **Read** — the lenient ``Question`` / ``Page`` / ``QuestionsResponse`` envelope returned by
  ``GET …/questions`` and ``GET …/questions/{id}`` (type-specific detail lenient-ignored).
* **Write** — a **fully-typed discriminated union** (:data:`QuestionCreate`) over the 12 API
  question schemas, tagged by ``type``. The same body serves ``POST …/questions`` (create) and
  ``PATCH …/questions/{id}`` (modify); ``QuestionMove`` types the ``/move`` body. Every field
  carries a ``Field(description=…)`` so the shape is self-documenting.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import Field, TypeAdapter, model_validator

from ycli.yandex.models import APIModel


class Question(APIModel):
    """A single question / form field.

    Serves both ``GET …/questions`` (``pages[].items[]``) and ``GET …/questions/{id}``
    (a single question's settings). ``id`` is an **int**. Type-specific detail
    (``data_source``, ``items``, ``validators``, ``conditions``, ``image``,
    ``quiz_items``, …) is lenient-ignored — the common fields below cover every type.

    Example:
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


class Page(APIModel):
    """A page grouping questions (``…/questions`` → ``pages[]``).

    Example:
        >>> Page.model_validate({"id": 7, "items": [{"id": 1}]}).items[0].id
        1
    """

    id: int | None = Field(default=None, description="Page ID (integer).")
    items: list[Question] = Field(
        default_factory=list, description="Questions grouped on this page, in display order."
    )


class QuestionsResponse(APIModel):
    """Envelope for ``GET …/questions`` — ``{pages:[Page]}``.

    Example:
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

WidgetType = Literal["radio", "checkbox", "dropdown", "stars", "onerow"]
ModifyChoicesType = Literal["", "natural", "sort", "shuffle"]
ValidatorType = Literal[
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
ConditionOperatorType = Literal["and", "or"]
ConditionItemKind = Literal["question", "language", "origin", "quiz"]
ConditionComparison = Literal["eq", "neq", "lt", "gt"]


class QuestionValidator(APIModel):
    """One answer-validation rule (an item of a question's ``validators`` list).

    ``type`` selects the rule; ``value`` carries its argument where the rule needs one —
    an int (``min``/``max`` length or number, ``size``/``count``), a float, or a string
    (a ``min``/``max`` date ``YYYY-MM-DD``, a ``regexp`` pattern). Rules like ``required``,
    ``email``, ``url``, ``phone``, ``inn``, ``single`` take no ``value``.

    Example:
        >>> QuestionValidator(type="min", value=3).value
        3
    """

    type: ValidatorType = Field(description="Validation rule kind, e.g. required, min, max, email.")
    value: int | float | str | None = Field(
        default=None, description="Rule argument (length/number, date string, or regexp pattern)."
    )


class ConditionItem(APIModel):
    """One clause inside a display-condition group.

    Example:
        >>> ConditionItem(type="question", condition="eq", question="q1", value="yes").value
        'yes'
    """

    condition: ConditionComparison | None = Field(
        default=None, description="Comparison operator: eq, neq, lt, gt."
    )
    operator: ConditionOperatorType | None = Field(
        default=None, description="Boolean operator joining this clause to the next: and / or."
    )
    type: ConditionItemKind | None = Field(
        default=None, description="Clause subject: question, language, origin or quiz."
    )
    question: str | None = Field(
        default=None, description="Slug of the question this clause tests (for type=question)."
    )
    value: str | None = Field(default=None, description="Value the clause compares against.")


class Condition(APIModel):
    """A display-condition group (the question shows only when the group matches).

    Example:
        >>> Condition(operator="and", items=[ConditionItem(question="q1")]).operator
        'and'
    """

    id: int | None = Field(default=None, description="Condition group ID.")
    operator: str | None = Field(default=None, description="Operator combining the group's items.")
    items: list[ConditionItem] | None = Field(
        default=None, description="Clauses evaluated within this group."
    )


class QuestionImage(APIModel):
    """An image attached to a question (or an enum option).

    Example:
        >>> QuestionImage(id=5, name="cover.png").id
        5
    """

    id: int | None = Field(default=None, description="Image ID (from an image upload).")
    name: str | None = Field(default=None, description="Original image file name.")
    links: dict[str, Any] | None = Field(
        default=None, description="Map of links to the rendered image sizes."
    )
    check_status: str | None = Field(
        default=None, description="Upload/scan status: check, ready, infected, error, deleted."
    )


class DataSourceParam(APIModel):
    """One parameter of a hint- or suggest-data-source descriptor.

    Example:
        >>> DataSourceParam(type="org", value="42").value
        '42'
    """

    type: str | None = Field(default=None, description="Parameter name/type.")
    value: str | None = Field(default=None, description="Parameter value.")


class QuestionHintSource(APIModel):
    """A named source that supplies a string question's hint/autocomplete.

    Example:
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

    Example:
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

    Example:
        >>> QuestionQuizItem(label="A", correct=True, scores=1.0).correct
        True
    """

    label: str | None = Field(default=None, description="Answer option text.")
    correct: bool | None = Field(default=None, description="Whether this option is correct.")
    scores: float | None = Field(default=None, description="Points awarded for this option.")


class QuestionEnumItem(APIModel):
    """One selectable option of an ``enum`` (radio/checkbox/dropdown/stars) question.

    Example:
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


class QuestionMatrixRow(APIModel):
    """One row (or column) of a ``matrix`` question's grid.

    Example:
        >>> QuestionMatrixRow(slug="r1", label="Row 1").label
        'Row 1'
    """

    id: int | None = Field(default=None, description="Row/column ID (integer).")
    slug: str | None = Field(default=None, description="Stable machine slug of the row/column.")
    label: str | None = Field(default=None, description="Row/column text.")


class _QuestionBase(APIModel):
    """Fields shared by every question type (the discriminated-union member base).

    Concrete members add a ``Literal`` ``type`` tag (the union discriminator) plus their own
    type-specific fields. Unset (``None``) fields are dropped before the request is sent.
    Display conditions are NOT part of the write body — the live API silently ignores a
    ``conditions`` key here; manage them via the ``conditions`` resource
    (``forms conditions …`` / ``forms_conditions_*``).
    """

    id: int | None = Field(
        default=None, description="Question ID — set only when modifying an existing question."
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

    Example:
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
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min/max length, email, url, …)."
    )


class BooleanQuestion(_QuestionBase):
    """Yes/no (single checkbox) answer.

    Example:
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

    Example:
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

    Example:
        >>> FileQuestion(label="Attach").type
        'file'
    """

    type: Literal["file"] = Field(default="file", description="Discriminator: file.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, size, count, external)."
    )


class CommentQuestion(_QuestionBase):
    """A static text / header block (no answer collected).

    Example:
        >>> CommentQuestion(label="Section A", header=True).header
        True
    """

    type: Literal["comment"] = Field(default="comment", description="Discriminator: comment.")
    header: bool | None = Field(
        default=None, description="Render the text as a section header rather than body copy."
    )


class DateQuestion(_QuestionBase):
    """Single-date answer, optionally bounded by min/max date validators.

    Example:
        >>> DateQuestion(label="Born").type
        'date'
    """

    type: Literal["date"] = Field(default="date", description="Discriminator: date.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min/max date, external)."
    )


class DateRangeQuestion(_QuestionBase):
    """Date-range (from/to) answer, optionally bounded by min/max date validators.

    Example:
        >>> DateRangeQuestion(label="Period").type
        'daterange'
    """

    type: Literal["daterange"] = Field(default="daterange", description="Discriminator: daterange.")
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, min/max date, external)."
    )


class PaymentQuestion(_QuestionBase):
    """A payment field (amount to a wallet), optionally fixed or bounded by min/max.

    Example:
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

    Example:
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
    validators: list[QuestionValidator] | None = Field(
        default=None, description="Validation rules (required, single, external)."
    )


class SuggestQuestion(_QuestionBase):
    """Autocomplete/suggest answer backed by an external data source.

    Example:
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

    Example:
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

    Example:
        >>> SeriesQuestion(label="People", items=[StringQuestion(label="Name")]).items[0].type
        'string'
    """

    type: Literal["series"] = Field(default="series", description="Discriminator: series.")
    items: list[QuestionCreate] | None = Field(
        default=None, description="Nested questions repeated as a group."
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

#: Runtime validator that routes a raw dict to the right member by its ``type`` tag.
QuestionCreateAdapter: TypeAdapter[Any] = TypeAdapter(QuestionCreate)


class QuestionMove(APIModel):
    """Typed body for ``POST …/questions/{id}/move`` — where to reposition the question.

    A bare ``position`` with no page target is a **silent no-op** live: the API answers 200
    but moves nothing. Rather than paper over that with a hidden default, this model RAISES
    when ``position`` is set and no target (``page`` / ``page_id`` / ``create_page`` /
    ``question``) is given — the caller must pick a target. The CLI ``move`` command defaults
    ``page`` to 1 for a bare ``--position`` *visibly*, before constructing this model; an MCP
    caller passing position-only gets this validation error instead of a silent re-page.

    Example:
        >>> QuestionMove(page=2, position=1).position
        1
        >>> QuestionMove(position=1)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for QuestionMove
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

    @model_validator(mode="after")
    def _require_target_for_position(self) -> QuestionMove:
        """Reject a bare ``position`` — the API 200s-but-silently-ignores it otherwise."""
        no_target = (
            self.page is None
            and self.page_id is None
            and self.question is None
            and not self.create_page
        )
        if self.position is not None and no_target:
            raise ValueError(
                "question move needs a target: pass page / page_id / question / create_page "
                "(a bare position is a silent no-op live)"
            )
        return self


class QuestionMoveResult(APIModel):
    """Result of ``POST …/questions/{id}/move`` — the moved question's id.

    Example:
        >>> QuestionMoveResult(id=17).id
        17
    """

    id: int | None = Field(default=None, description="ID of the moved question.")
