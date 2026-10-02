"""Forms ``/surveys`` operations, declared once (sans-IO).

Examples:
    >>> get_survey("686d").path
    'surveys/686d'
    >>> publish_survey("686d").effect
    'write'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import OffsetLimitPagination
from ycli.yandex.forms.surveys.models import Survey, SurveysResponse

PAGE_SIZE = 100


def list_surveys() -> Paged[SurveysResponse, Survey]:
    """``GET /surveys``, paged by ``offset``/``limit`` until a short page."""
    return Paged(
        Endpoint("GET", "surveys", SurveysResponse),
        OffsetLimitPagination(page_size=PAGE_SIZE),
        lambda page: page.result,
    )


def get_survey(survey_id: str) -> Endpoint[Survey]:
    return Endpoint("GET", f"surveys/{segment(survey_id)}", Survey)


def create_survey(body: dict[str, Any]) -> Endpoint[Survey]:
    return Endpoint("POST", "surveys", Survey, json=body)


def modify_survey(survey_id: str, body: dict[str, Any]) -> Endpoint[Survey]:
    return Endpoint("PATCH", f"surveys/{segment(survey_id)}", Survey, json=body)


def delete_survey(survey_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"surveys/{segment(survey_id)}")


def publish_survey(survey_id: str) -> Endpoint[None]:
    return Endpoint("POST", f"surveys/{segment(survey_id)}/publish")


def unpublish_survey(survey_id: str) -> Endpoint[None]:
    return Endpoint("POST", f"surveys/{segment(survey_id)}/unpublish")
