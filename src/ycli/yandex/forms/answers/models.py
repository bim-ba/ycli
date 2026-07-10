"""Pydantic models for Forms answers (Column + Answer + AnswersResponse envelope)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel


class Column(APIModel):
    """An answers-table column descriptor (``…/answers`` → ``columns[]``).

    Example:
        >>> Column.model_validate({"id": 1, "slug": "s", "type": "string", "text": "T"}).text
        'T'
    """

    id: int | None = None
    slug: str | None = None
    type: str | None = None
    text: str | None = None
    has_scores: bool | None = None


class Answer(APIModel):
    """A single form response (``…/answers`` → ``answers[]``).

    ``data`` is **positional**, aligned to ``columns``; each element is a
    ``{"value": …}`` dict or ``null``. Passed through verbatim as ``Any``
    (``value`` is a ``str`` or ``list[str]``).

    Example:
        >>> Answer.model_validate({"id": 9, "created": "2026-01-01", "data": [{"value": "x"}]}).data
        [{'value': 'x'}]
    """

    id: int | None = None
    created: str | None = None
    data: list[Any] = Field(default_factory=list)


class AnswersResponse(APIModel):
    """Envelope for ``GET …/answers`` — ``{columns, answers, next}``.

    ``next`` is ``{"next_url": …}`` or ``null`` (a pagination cursor), passed
    through as ``Any``.

    Example:
        >>> AnswersResponse.model_validate({"columns": [], "answers": [], "next": None}).answers
        []
    """

    columns: list[Column] = Field(default_factory=list)
    answers: list[Answer] = Field(default_factory=list)
    next: Any = None


class ImageOut(APIModel):
    """An image attached to a quiz result page (``ImageOut``).

    Example:
        >>> ImageOut.model_validate(
        ...     {"id": 1, "name": "r.png", "check_status": "ready"}
        ... ).check_status
        'ready'
    """

    id: int | None = Field(default=None, description="Image ID.")
    links: dict[str, Any] = Field(
        default_factory=dict, description="Map of image size → URL for each rendered variant."
    )
    name: str | None = Field(default=None, description="Original image file name.")
    check_status: str | None = Field(
        default=None,
        description="Upload/scan status — one of: check, ready, infected, error, deleted.",
    )


class AnswerSurveyOut(APIModel):
    """The form a response belongs to (``AnswerSurveyOut``).

    Example:
        >>> AnswerSurveyOut.model_validate({"id": "686d", "name": "Feedback"}).name
        'Feedback'
    """

    id: str | None = Field(default=None, description="Form ID (hex ObjectId string).")
    name: str | None = Field(default=None, description="Form name.")


class AnswerQuizOut(APIModel):
    """Quiz/test scoring summary for a response (``AnswerQuizOut``).

    Present only for forms configured as a quiz; ``scores``/``total`` are floats.

    Example:
        >>> AnswerQuizOut.model_validate({"scores": 1.5, "total": 3.0, "questions": 2}).total
        3.0
    """

    scores: float | None = Field(default=None, description="Points scored for this form response.")
    total: float | None = Field(
        default=None, description="Maximum points achievable for the response."
    )
    questions: int | None = Field(
        default=None, description="Number of graded (test) questions in the form."
    )
    title: str | None = Field(default=None, description="Title of the test result page.")
    subtitle: str | None = Field(default=None, description="Subtitle of the test result page.")
    image: ImageOut | None = Field(default=None, description="Image shown on the test result page.")
    show_results: bool | None = Field(
        default=None, description="Whether test results are shown to the respondent."
    )


class AnswerQuestionOut(APIModel):
    """One question's answer within a response (``AnswerQuestionOut``).

    ``value`` and ``items`` are polymorphic (they depend on ``type`` — a scalar, a
    date range, a file list, enum items, matrix items, or nested series answers), so
    both are passed through verbatim as ``Any``.

    Example:
        >>> AnswerQuestionOut.model_validate({"id": "q1", "type": "string", "value": "Ann"}).value
        'Ann'
    """

    id: str | None = Field(default=None, description="Question ID.")
    label: str | None = Field(default=None, description="Question name / label.")
    type: str | None = Field(
        default=None, description="Question type (string, radio, matrix, file, …)."
    )
    widget: str | None = Field(
        default=None,
        description="Display widget — one of: radio, checkbox, dropdown, stars, onerow.",
    )
    multiline: bool | None = Field(
        default=None, description="Whether the text answer spans multiple lines."
    )
    multichoice: bool | None = Field(
        default=None, description="Whether multiple answer options may be selected."
    )
    is_deleted: bool | None = Field(
        default=None, description="Whether the underlying question has been deleted."
    )
    items: Any = Field(
        default=None,
        description="Answer options for the question; shape varies by type "
        "(string-scores, enum items, or a matrix of rows/columns).",
    )
    scores: float | None = Field(
        default=None, description="Points awarded for this question (quiz forms)."
    )
    value: Any = Field(
        default=None,
        description="The submitted answer; type varies by question type — a scalar "
        "(string/bool/int), a date range, a file list, enum items, matrix items, "
        "or nested series answers.",
    )


class AnswerDetail(APIModel):
    """A single form response in full detail (``GET /v1/surveys/{id}/answers/{answer_id}``).

    Unlike the flat positional row in :class:`AnswersResponse`, this carries a per-question
    ``data`` array plus the parent form and (for quizzes) the scoring summary.

    Example:
        >>> AnswerDetail.model_validate(
        ...     {"id": 99, "survey": {"id": "686d", "name": "F"}, "data": []}
        ... ).survey.name
        'F'
    """

    id: int | None = Field(default=None, description="Answer ID (integer).")
    created: str | None = Field(default=None, description="Answer submission date.")
    survey: AnswerSurveyOut | None = Field(
        default=None, description="The form this response belongs to."
    )
    quiz: AnswerQuizOut | None = Field(
        default=None, description="Test/quiz scoring summary (present for quiz forms)."
    )
    data: list[AnswerQuestionOut] = Field(
        default_factory=list,
        description="Per-question answer detail — one entry per answered question.",
    )


#: Export-operation statuses at which polling stops — the export has finished (well or badly).
EXPORT_TERMINAL_STATUSES = frozenset({"ok", "fail"})


class AnswerExport(APIModel):
    """Typed request body for ``POST /v1/surveys/{id}/answers/export`` (start an async export).

    Every field is optional — the API defaults ``format`` to ``xlsx`` and ``upload`` to
    ``default``. Unset (``None``) fields are dropped before the request is sent, so a bare
    ``AnswerExport()`` exports every answer of the form in ``xlsx``.

    Example:
        >>> AnswerExport(format="csv", limit=100).model_dump(exclude_none=True)
        {'format': 'csv', 'limit': 100}
    """

    format: str | None = Field(
        default=None, description="Export format — ``csv`` or ``xlsx`` (API default ``xlsx``)."
    )
    upload: str | None = Field(
        default=None,
        description="Where to upload the result — ``default`` or ``disk`` (Yandex Disk).",
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


class ExportResult(APIModel):
    """An async answer-export operation — ``{id, status, message}``.

    Returned both by the trigger (``POST …/answers/export`` → ``202``) and by the status read
    (``GET …/answers/export-results?task_id=…``). ``status`` is one of ``ok``, ``fail``,
    ``wait`` or ``not_running``; poll the status read until :attr:`is_terminal`, then
    :attr:`is_ready` (``ok``) means the file can be downloaded. The same shape is exposed
    generically by :class:`~ycli.yandex.forms.operations.models.OperationResult`.

    Example:
        >>> ExportResult.model_validate({"id": "op-1", "status": "ok"}).is_ready
        True
    """

    id: str | None = Field(
        default=None,
        description="Operation id — poll it via ``export-results`` or ``operations get``.",
    )
    status: str | None = Field(
        default=None,
        description="Operation status: one of ``ok``, ``fail``, ``wait``, ``not_running``.",
    )
    message: str | None = Field(default=None, description="Human-readable operation message.")

    @property
    def is_terminal(self) -> bool:
        """``True`` once ``status`` is terminal (see :data:`EXPORT_TERMINAL_STATUSES`)."""
        return self.status in EXPORT_TERMINAL_STATUSES

    @property
    def is_ready(self) -> bool:
        """``True`` when the export finished successfully (``status == "ok"``); the file exists."""
        return self.status == "ok"
