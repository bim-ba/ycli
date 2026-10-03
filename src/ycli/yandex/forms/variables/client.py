"""Forms ``/surveys/{id}/variables`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.variables import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.variables.models import VariableInfo
    from ycli.yandex.models import ItemList


class VariablesClient(Resource):
    """The variable types a form's integrations can reference."""

    def list(self, survey_id: str) -> ItemList[VariableInfo]:
        """``GET /surveys/{id}/variables`` → every variable type available to the form.

        Args:
            survey_id: The form's id.

        Returns:
            Every variable type available to the form.

        Examples:
            >>> forms.variables.list("686d0a1b2c3d4e5f000000c0").root[0].type
            'form.answer_url'
        """
        return self._session.send(endpoints.list_variables(survey_id))
