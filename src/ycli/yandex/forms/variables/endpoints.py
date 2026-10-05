"""Forms ``/surveys/{id}/variables`` operation, declared once (sans-IO).

Examples:
    >>> list_("686d").path
    'surveys/686d/variables'
"""

from __future__ import annotations

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.variables.models import VariableInfo
from ycli.yandex.models import ItemList


def list_(survey_id: str) -> Endpoint[ItemList[VariableInfo]]:
    return Endpoint(
        HTTPMethod.GET, f"surveys/{segment(survey_id)}/variables", ItemList[VariableInfo]
    )
