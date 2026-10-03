"""Forms ``/surveys`` operations, declared once (sans-IO).

Examples:
    >>> get_survey("686d").path
    'surveys/686d'
    >>> publish_survey("686d").effect
    'write'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, Paged, flag, segment
from ycli.yandex.core.pagination import OffsetLimitPagination
from ycli.yandex.forms.surveys.models import Survey, SurveyCreate, SurveysResponse, SurveyUpdate

PAGE_SIZE = 100


def list_surveys(
    *,
    name: str | None,
    published: bool | None,
    ownership: str | None,
    group: str | None,
    favourite: bool | None,
    show_all: bool,
    orderby: str | None,
) -> Paged[SurveysResponse, Survey]:
    """``GET /surveys``, paged by ``offset``/``limit`` until a short page."""
    params = {
        "name": name,
        "published": published,
        "ownership": ownership,
        "group": group,
        "favourite": favourite,
        "show_all": flag(show_all),
        "orderby": orderby,
    }
    return Paged(
        Endpoint("GET", "surveys", SurveysResponse, params=params),
        OffsetLimitPagination(page_size=PAGE_SIZE),
        lambda page: page.result,
    )


def get_survey(survey_id: str) -> Endpoint[Survey]:
    return Endpoint("GET", f"surveys/{segment(survey_id)}", Survey)


def create_survey(body: SurveyCreate) -> Endpoint[Survey]:
    return Endpoint("POST", "surveys", Survey, json=body)


def modify_survey(survey_id: str, body: SurveyUpdate) -> Endpoint[Survey]:
    return Endpoint("PATCH", f"surveys/{segment(survey_id)}", Survey, json=body)


def delete_survey(survey_id: str) -> Endpoint[None]:
    return Endpoint("DELETE", f"surveys/{segment(survey_id)}")


def publish_survey(survey_id: str) -> Endpoint[None]:
    return Endpoint("POST", f"surveys/{segment(survey_id)}/publish")


def unpublish_survey(survey_id: str) -> Endpoint[None]:
    return Endpoint("POST", f"surveys/{segment(survey_id)}/unpublish")
