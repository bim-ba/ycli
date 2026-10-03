"""Forms ``/surveys/{id}/history`` client on the httpx2 core (a form's change log)."""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.history import endpoints
from ycli.yandex.forms.history.models import HistoryEvent
from ycli.yandex.models import ItemList


class HistoryClient(Resource):
    """Read the change log of a form."""

    def list(
        self, survey_id: str, *, ordering: str | None = None, limit: int | None = None
    ) -> ItemList[HistoryEvent]:
        """``GET /surveys/{id}/history`` → the form's changes, page by page, at most ``limit``.

        ``ordering`` is ``desc`` (newest first, the API default) or ``asc``.

        Args:
            survey_id: The form's id.
            ordering: ``desc`` (newest first) or ``asc``.
            limit: The most events to return; ``None`` returns every event.

        Returns:
            The form's change events.

        Examples:
            >>> events = forms.history.list("686d0a1b2c3d4e5f000000e1", ordering="asc", limit=500)
            >>> [event.model for event in events.root]
            ['servicesurveyhooksubscription', 'surveyhook']
        """
        paged = endpoints.list_history(survey_id, ordering=ordering)
        return ItemList[HistoryEvent](list(self._session.iterate(paged, limit=limit)))
