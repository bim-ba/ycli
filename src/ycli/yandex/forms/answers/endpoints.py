"""Forms answers operations, declared once (sans-IO).

Examples:
    >>> get(answer_id=7, answer_key=None).params
    {'answer_id': 7, 'answer_key': None}
    >>> export("686d", {"format": "xlsx"}).effect
    <Effect.WRITE: 'write'>
"""

from __future__ import annotations

from http import HTTPMethod
from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import NextURLPagination
from ycli.yandex.forms.answers.models import (
    Answer,
    AnswerDetails,
    AnswerExport,
    AnswerIntegration,
    AnswersResponse,
    Column,
)
from ycli.yandex.forms.models import OperationResult
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    import httpx2


def get(*, answer_id: int | None, answer_key: str | None) -> Endpoint[AnswerDetails]:
    """``GET /answers`` — a flat route keyed by query, not nested under ``/surveys/{id}``."""
    params = {"answer_id": answer_id, "answer_key": answer_key}
    return Endpoint(HTTPMethod.GET, "answers", AnswerDetails, params=params)


def _next_url(response: httpx2.Response) -> str | None:
    following = response.json().get("next")
    return following.get("next_url") if isinstance(following, dict) else None


def list_(
    survey_id: str,
    *,
    questions: str | None,
    use_slugs: bool | None,
    date_from: str | None,
    date_to: str | None,
    ordering: str | None,
    page_size: int | None,
    answer_format: str | None,
) -> Paged[AnswersResponse, Answer]:
    """``GET /surveys/{id}/answers``, paged by the ``next.next_url`` cursor.

    The links point at a retired ``/v3/`` route, so only their query (the ``id`` cursor) is
    carried over onto the v1 request.
    """
    params = {
        "questions": questions,
        "use_slugs": use_slugs,
        "date_from": date_from,
        "date_to": date_to,
        "ordering": ordering,
        "page_size": page_size,
        "format": answer_format,
    }
    return Paged(
        Endpoint(
            HTTPMethod.GET, f"surveys/{segment(survey_id)}/answers", AnswersResponse, params=params
        ),
        NextURLPagination(url_of=_next_url, query_only=True),
        lambda page: page.answers,
    )


def _columns(response: httpx2.Response) -> ItemList[Column]:
    return ItemList[Column](AnswersResponse.model_validate(response.json()).columns)


def columns_list(
    survey_id: str, *, questions: str | None, use_slugs: bool | None
) -> Endpoint[ItemList[Column]]:
    """``GET /surveys/{id}/answers`` for its ``columns``: the API has no request for them alone.

    One answer is asked for, the least a page holds, and left out of the result.
    """
    params = {"questions": questions, "use_slugs": use_slugs, "page_size": 1}
    path = f"surveys/{segment(survey_id)}/answers"
    return Endpoint(HTTPMethod.GET, path, params=params, parser=_columns)


def export(survey_id: str, body: AnswerExport) -> Endpoint[OperationResult]:
    return Endpoint(
        HTTPMethod.POST, f"surveys/{segment(survey_id)}/answers/export", OperationResult, json=body
    )


def _export_status(response: httpx2.Response) -> OperationResult:
    # A finished export redirects to the exported file: ready, and not worth downloading here.
    if response.is_redirect:
        return OperationResult(status="ok")
    return OperationResult.model_validate_json(response.content)


def export_results_get(survey_id: str, task_id: str) -> Endpoint[OperationResult]:
    path = f"surveys/{segment(survey_id)}/answers/export-results"
    params = {"task_id": task_id}
    return Endpoint(
        HTTPMethod.GET,
        path,
        OperationResult,
        params=params,
        parser=_export_status,
        follow_redirects=False,
    )


def export_download(survey_id: str, task_id: str) -> Endpoint[bytes]:
    path = f"surveys/{segment(survey_id)}/answers/export-results"
    return Endpoint(HTTPMethod.GET, path, bytes, params={"task_id": task_id})


def integrations_list(
    *, answer_id: int | None, answer_key: str | None
) -> Endpoint[ItemList[AnswerIntegration]]:
    """``GET /answers/integrations`` — flat like :func:`get`, keyed by query."""
    params = {"answer_id": answer_id, "answer_key": answer_key}
    return Endpoint(
        HTTPMethod.GET, "answers/integrations", ItemList[AnswerIntegration], params=params
    )


def delete(survey_id: str, answer_id: int) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"surveys/{segment(survey_id)}/answers/{segment(answer_id)}")


def restore(survey_id: str, answer_id: int) -> Endpoint[None]:
    path = f"surveys/{segment(survey_id)}/answers/{segment(answer_id)}/restore"
    return Endpoint(HTTPMethod.POST, path)
