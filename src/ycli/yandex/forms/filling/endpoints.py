"""Forms form-filling operations, declared once (sans-IO).

Examples:
    >>> submit_form("686d", {"name": "Ann"}, dry_run=True, key=None).params
    {'dry_run': 'true', 'key': None}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.filling.models import FillableForm, SubmitResult, SuggestionList


def get_form(survey: str, *, key: str | None) -> Endpoint[FillableForm]:
    return Endpoint("GET", f"surveys/{segment(survey)}/form", FillableForm, params={"key": key})


def submit_form(
    survey: str, body: dict[str, Any], *, dry_run: bool, key: str | None
) -> Endpoint[SubmitResult]:
    params = {"dry_run": "true" if dry_run else None, "key": key}
    return Endpoint(
        "POST", f"surveys/{segment(survey)}/form", SubmitResult, json=body, params=params
    )


def suggest(survey: str, params: dict[str, str | None]) -> Endpoint[SuggestionList]:
    return Endpoint("GET", f"surveys/{segment(survey)}/suggest", SuggestionList, params=params)
