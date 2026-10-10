"""Pydantic models for Forms answers (Column + Answer + AnswersResponse envelope)."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ycli.yandex.forms.models import IntegrationType, RunStatus
from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.sync.marks import Identity

#: The file an export of answers produces.
ExportFormat = Literal["csv", "xlsx", "json"] | str
#: Where the exported file goes: handed back, or saved to Yandex Disk.
ExportUpload = Literal["default", "disk"] | str
#: How a listing shows an answer: cells aligned to the columns, or its data as stored.
AnswerFormat = Literal["default", "raw"] | str


class Column(APIModel):
    """An answers-table column descriptor (``…/answers`` → ``columns[]``).

    Examples:
        >>> Column.model_validate({"id": 1, "slug": "s", "type": "string", "text": "T"}).text
        'T'
    """

    id: Annotated[int | None, Identity()] = Field(default=None, description="Id of the column.")
    slug: str | None = Field(default=None, description="Slug of the column.")
    type: str | None = Field(default=None, description="Question type of the column.")
    text: str | None = Field(default=None, description="Heading of the column, the question text.")
    has_scores: bool | None = Field(default=None, description="Whether the column has quiz scores.")


class Answer(APIModel):
    """A single form response (``…/answers`` → ``answers[]``).

    ``data`` is **positional**, aligned to ``columns``; each element is a
    ``{"value": …}`` dict or ``null``. Passed through verbatim as ``Any``
    (``value`` is a ``str`` or ``list[str]``). Asked for in the ``raw`` format, the reply has
    no ``columns`` and ``data`` is an object keyed by question.

    Examples:
        >>> Answer.model_validate({"id": 9, "created": "2026-01-01", "data": [{"value": "x"}]}).data
        [{'value': 'x'}]
    """

    id: Annotated[int | None, Identity()] = Field(default=None, description="Id of the answer.")
    created: str | None = Field(
        default=None, description="When the answer was submitted (ISO 8601)."
    )
    uid: str | None = Field(
        default=None, description="Passport uid of the respondent (the ``raw`` format only)."
    )
    data: list[Any] | dict[str, Any] = Field(
        default_factory=list,
        description="Cells aligned to ``columns``; in the ``raw`` format, an object by question.",
    )


class AnswerSurveyRef(APIModel):
    """The form a single answer belongs to (``GET /answers`` → ``survey``).

    Examples:
        >>> AnswerSurveyRef.model_validate({"id": "686d0a1b", "name": "Feedback"}).name
        'Feedback'
    """

    id: str | None = Field(default=None, description="Form id (hex ObjectId).")
    name: str | None = Field(default=None, description="Form name.")


class AnswerDetails(APIModel):
    """One full form response (``GET /v1/answers?answer_id=…`` / ``?answer_key=…``).

    Unlike the positional ``data`` of the listing's :class:`Answer`, here each ``data``
    item is a self-describing question record (``{id, label, type, value, …}``) — passed
    through verbatim, as ``value`` ranges over eight shapes. ``quiz`` (test results) is
    also passed through verbatim when present.

    Examples:
        >>> AnswerDetails.model_validate(
        ...     {"id": 9, "created": "2026-01-01", "survey": {"id": "686d", "name": "F"}}
        ... ).survey.id
        '686d'
    """

    id: Annotated[int | None, Identity()] = Field(default=None, description="Answer id (integer).")
    created: str | None = Field(default=None, description="ISO-8601 submission timestamp.")
    survey: AnswerSurveyRef | None = Field(
        default=None, description="The form this answer belongs to."
    )
    started: str | None = Field(
        default=None, description="ISO-8601 time the respondent began filling the form."
    )
    quiz: Any = Field(default=None, description="Quiz (test) results, when the form is a quiz.")
    data: list[Any] = Field(
        default_factory=list,
        description="Per-question answer records ({id, label, type, value, …}), verbatim.",
    )


class AnswersResponse(APIModel):
    """Envelope for ``GET …/answers`` — ``{columns, answers, next}``.

    ``next`` is ``{"next_url": …}`` or ``null`` (a pagination cursor), passed
    through as ``Any``.

    Examples:
        >>> AnswersResponse.model_validate({"columns": [], "answers": [], "next": None}).answers
        []
    """

    columns: list[Column] = Field(default_factory=list, description="Columns of the table.")
    answers: list[Answer] = Field(
        default_factory=list, description="Answers on this page, cells aligned to `columns`."
    )
    next: Any = Field(
        default=None, description='`{"next_url": …}` for the next page, `null` on the last.'
    )


class AnswerExport(RequestBody):
    """Typed request body for ``POST /v1/surveys/{id}/answers/export`` (start an async export).

    Every field is optional — the API defaults ``format`` to ``xlsx`` and ``upload`` to
    ``default``. Unset (``None``) fields are dropped before the request is sent, so a bare
    ``AnswerExport()`` exports every answer of the form in ``xlsx``.

    Examples:
        >>> AnswerExport(format="csv", limit=100).model_dump(exclude_none=True)
        {'format': 'csv', 'limit': 100}
    """

    format: ExportFormat | None = Field(
        default=None, description="Export format (the API's default is ``xlsx``)."
    )
    upload: ExportUpload | None = Field(
        default=None, description="Where the result goes; ``disk`` is Yandex Disk."
    )
    started_at: str | None = Field(
        default=None, description="ISO-8601 start of the answer date range (inclusive)."
    )
    finished_at: str | None = Field(
        default=None, description="ISO-8601 end of the answer date range (inclusive)."
    )
    pks: list[int] | None = Field(
        default=None, description="Explicit answer ids to export (omit to export all)."
    )
    columns: list[str] | None = Field(
        default=None, description="Question/column slugs to include (omit to export all columns)."
    )
    limit: int | None = Field(default=None, description="Maximum number of answers to export.")
    upload_files: bool | None = Field(
        default=None, description="Also export respondents' uploaded files to Yandex Disk."
    )


class AnswerIntegration(APIModel):
    """One integration run an answer triggered (``GET /answers/integrations`` item).

    Which of the type-specific fields is set depends on ``type``: ``to_address`` (email),
    ``wiki_page`` and ``link`` (wiki), ``issue_key`` and ``link`` (tracker), ``url`` (http,
    jsonrpc) or ``function_id`` (function).

    Examples:
        >>> AnswerIntegration.model_validate(
        ...     {"id": 4, "status": "success", "type": "tracker", "issue_key": "DE-7"}
        ... ).issue_key
        'DE-7'
    """

    id: Annotated[int | None, Identity()] = Field(default=None, description="Integration id.")
    status: RunStatus | None = Field(
        default=None, description="Run state: pending, success, error or canceled."
    )
    message: str | None = Field(default=None, description="Result message of the run.")
    type: IntegrationType | None = Field(
        default=None,
        description="Integration type: email, tracker, wiki, jsonrpc, http, post, put or function.",
    )
    to_address: str | None = Field(default=None, description="Recipient address (email).")
    wiki_page: str | None = Field(default=None, description="Wiki page supertag (wiki).")
    link: str | None = Field(default=None, description="Link to the wiki page or tracker issue.")
    issue_key: str | None = Field(default=None, description="Tracker issue key (tracker).")
    url: str | None = Field(default=None, description="URL that was called (http, jsonrpc).")
    function_id: str | None = Field(default=None, description="Cloud function id (function).")
