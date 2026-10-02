"""Forms ``/surveys/{id}/history`` client on the httpx2 core (a form's change log)."""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.history import endpoints
from ycli.yandex.forms.history.models import HistoryEventList


class HistoryClient(Resource):
    """Read the change log of a form."""

    def list(
        self, survey_id: str, *, ordering: str | None = None, limit: int | None = None
    ) -> HistoryEventList:
        """``GET /surveys/{id}/history`` → the form's changes, page by page, at most ``limit``.

        ``ordering`` is ``desc`` (newest first, the API default) or ``asc``.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.history.list("686d0a1b", limit=5).root[0].model  # doctest: +SKIP
            'surveyhook'
        """
        paged = endpoints.list_history(survey_id, ordering=ordering)
        return HistoryEventList(list(self._session.iterate(paged, limit=limit)))
