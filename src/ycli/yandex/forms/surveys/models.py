"""Pydantic models for Forms /surveys (Survey + SurveyList envelope)."""
from __future__ import annotations

from typing import Any

from ycli.yandex.forms._models import _Lenient


class Survey(_Lenient):
    """A form/survey (``GET /v1/surveys`` item and ``GET /v1/surveys/{id}``).

    ``id`` is a hex ObjectId **string** (not numeric); ``answers`` is an int
    response count. Settings-only fields (``texts``, ``followers``, …) are
    lenient-ignored.

    Example:
        >>> Survey.model_validate({"id": "686d", "name": "F", "answers": 444}).answers
        444
    """

    id: str | None = None
    name: str | None = None
    dir_id: str | None = None
    collab_id: str | None = None
    created: str | None = None
    modified: str | None = None
    language: str | None = None
    is_published: bool | None = None
    is_public: bool | None = None
    is_banned: bool | None = None
    answers: int | None = None
    is_favourite: bool | None = None


class SurveyList(_Lenient):
    """Envelope for ``GET /v1/surveys`` — ``{links, result:[Survey]}``.

    Example:
        >>> SurveyList.model_validate({"result": [{"id": "a"}]}).result[0].id
        'a'
    """

    links: dict[str, Any] = {}
    result: list[Survey] = []
