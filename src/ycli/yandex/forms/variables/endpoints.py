"""Forms ``/surveys/{id}/variables`` operation, declared once (sans-IO).

Example:
    >>> list_variables("686d").path
    'surveys/686d/variables'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.variables.models import VariableInfoList


def list_variables(survey_id: str) -> Endpoint[VariableInfoList]:
    return Endpoint("GET", f"surveys/{segment(survey_id)}/variables", VariableInfoList)
