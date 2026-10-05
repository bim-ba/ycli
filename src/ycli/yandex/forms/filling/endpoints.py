"""Forms form-filling operations, declared once (sans-IO).

Examples:
    >>> submit("686d", {"name": "Ann"}, validate_only=True, key=None).params
    {'dry_run': True, 'key': None}
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.filling.models import FillableForm, SubmitBody, SubmitResult, Suggestion
from ycli.yandex.models import ItemList


def get(survey_id: str, *, key: str | None) -> Endpoint[FillableForm]:
    return Endpoint(
        HTTPMethod.GET, f"surveys/{segment(survey_id)}/form", FillableForm, params={"key": key}
    )


def submit(
    survey_id: str, body: SubmitBody, *, validate_only: bool | None, key: str | None
) -> Endpoint[SubmitResult]:
    params = {"dry_run": validate_only, "key": key}
    return Endpoint(
        HTTPMethod.POST,
        f"surveys/{segment(survey_id)}/form",
        SubmitResult,
        json=body,
        params=params,
    )


def suggest(survey_id: str, params: dict[str, str | None]) -> Endpoint[ItemList[Suggestion]]:
    return Endpoint(
        HTTPMethod.GET, f"surveys/{segment(survey_id)}/suggest", ItemList[Suggestion], params=params
    )
