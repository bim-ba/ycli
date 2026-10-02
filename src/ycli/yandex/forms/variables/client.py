"""Forms ``/surveys/{id}/variables`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.variables import endpoints

if TYPE_CHECKING:
    from ycli.yandex.forms.variables.models import VariableInfoList


class VariablesClient(Resource):
    """The variable types a form's integrations can reference."""

    def list(self, survey_id: str) -> VariableInfoList:
        """``GET /surveys/{id}/variables`` → every variable type available to the form.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.variables.list("686d0a1b").root[0].type  # doctest: +SKIP
            'tracker.issue_key'
        """
        return self._session.send(endpoints.list_variables(survey_id))
