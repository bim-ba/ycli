"""Forms ``/surveys`` operations, declared once (sans-IO).

Examples:
    >>> get("686d").path
    'surveys/686d'
    >>> publish("686d").effect
    <Effect.WRITE: 'write'>
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.core.pagination import OffsetLimitPagination
from ycli.yandex.forms.surveys.models import Survey, SurveyCreate, SurveysResponse, SurveyUpdate

PAGE_SIZE = 100


def list_(
    *,
    name: str | None,
    published: bool | None,
    ownership: str | None,
    group: str | None,
    favourite: bool | None,
    show_all: bool | None,
    orderby: str | None,
) -> Paged[SurveysResponse, Survey]:
    """``GET /surveys``, paged by ``offset``/``limit`` until a short page."""
    params = {
        "name": name,
        "published": published,
        "ownership": ownership,
        "group": group,
        "favourite": favourite,
        "show_all": show_all,
        "orderby": orderby,
    }
    return Paged(
        Endpoint(HTTPMethod.GET, "surveys", SurveysResponse, params=params),
        OffsetLimitPagination(page_size=PAGE_SIZE),
        lambda page: page.result,
    )


def get(survey_id: str) -> Endpoint[Survey]:
    return Endpoint(HTTPMethod.GET, f"surveys/{segment(survey_id)}", Survey)


def create(body: SurveyCreate) -> Endpoint[Survey]:
    return Endpoint(HTTPMethod.POST, "surveys", Survey, json=body)


def update(survey_id: str, body: SurveyUpdate) -> Endpoint[Survey]:
    return Endpoint(HTTPMethod.PATCH, f"surveys/{segment(survey_id)}", Survey, json=body)


def delete(survey_id: str) -> Endpoint[None]:
    return Endpoint(HTTPMethod.DELETE, f"surveys/{segment(survey_id)}")


def publish(survey_id: str) -> Endpoint[None]:
    return Endpoint(HTTPMethod.POST, f"surveys/{segment(survey_id)}/publish")


def unpublish(survey_id: str) -> Endpoint[None]:
    return Endpoint(HTTPMethod.POST, f"surveys/{segment(survey_id)}/unpublish")
