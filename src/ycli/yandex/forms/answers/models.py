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
