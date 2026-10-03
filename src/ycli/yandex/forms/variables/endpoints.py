"""Forms ``/surveys/{id}/variables`` operation, declared once (sans-IO).

Examples:
    >>> list_variables("686d").path
    'surveys/686d/variables'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.variables.models import VariableInfo
from ycli.yandex.models import ItemList


def list_variables(survey_id: str) -> Endpoint[ItemList[VariableInfo]]:
    return Endpoint("GET", f"surveys/{segment(survey_id)}/variables", ItemList[VariableInfo])
