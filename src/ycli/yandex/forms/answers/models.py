"""Pydantic models for Forms answers (Column + Answer + AnswersResponse envelope)."""
from __future__ import annotations

from typing import Any

from ycli.yandex.forms._models import _Lenient


class Column(_Lenient):
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


class Answer(_Lenient):
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
    data: list[Any] = []


class AnswersResponse(_Lenient):
    """Envelope for ``GET …/answers`` — ``{columns, answers, next}``.

    ``next`` is ``{"next_url": …}`` or ``null`` (a pagination cursor), passed
    through as ``Any``.

    Example:
        >>> AnswersResponse.model_validate({"columns": [], "answers": [], "next": None}).answers
        []
    """

    columns: list[Column] = []
    answers: list[Answer] = []
    next: Any = None
