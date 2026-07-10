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
