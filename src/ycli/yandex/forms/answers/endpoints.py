"""Forms answers operations, declared once (sans-IO).

Example:
    >>> get_answer(answer_id=7, answer_key=None).params
    {'answer_id': 7, 'answer_key': None}
    >>> export_answers("686d", {"format": "xlsx"}).effect
    'write'
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import NextURLPagination
from ycli.yandex.forms.answers.models import Answer, AnswerDetails, AnswersResponse, ExportResult

if TYPE_CHECKING:
    import httpx2


def get_answer(*, answer_id: int | None, answer_key: str | None) -> Endpoint[AnswerDetails]:
    """``GET /answers`` — a flat route keyed by query, not nested under ``/surveys/{id}``."""
    params = {"answer_id": answer_id, "answer_key": answer_key}
    return Endpoint("GET", "answers", AnswerDetails, params=params)


def _next_url(response: httpx2.Response) -> str | None:
    following = response.json().get("next")
    return following.get("next_url") if isinstance(following, dict) else None


def list_answers(survey_id: str) -> Paged[AnswersResponse, Answer]:
    """``GET /surveys/{id}/answers``, paged by the ``next.next_url`` cursor.

    The links point at a retired ``/v3/`` route, so only their query (the ``id`` cursor) is
    carried over onto the v1 request.
    """
    return Paged(
        Endpoint("GET", f"surveys/{segment(survey_id)}/answers", AnswersResponse),
        NextURLPagination(url_of=_next_url, query_only=True),
        lambda page: page.answers,
    )


def export_answers(survey_id: str, body: dict[str, Any]) -> Endpoint[ExportResult]:
    return Endpoint("POST", f"surveys/{segment(survey_id)}/answers/export", ExportResult, json=body)


def _export_status(response: httpx2.Response) -> ExportResult:
    # A finished export redirects to the exported file: ready, and not worth downloading here.
    if response.is_redirect:
        return ExportResult(status="ok")
    return ExportResult.model_validate_json(response.content)


def export_results(survey_id: str, task_id: str) -> Endpoint[ExportResult]:
    path = f"surveys/{segment(survey_id)}/answers/export-results"
    params = {"task_id": task_id}
    return Endpoint(
        "GET", path, ExportResult, params=params, parser=_export_status, follow_redirects=False
    )


def download_export(survey_id: str, task_id: str) -> Endpoint[bytes]:
    path = f"surveys/{segment(survey_id)}/answers/export-results"
    return Endpoint("GET", path, bytes, params={"task_id": task_id})
