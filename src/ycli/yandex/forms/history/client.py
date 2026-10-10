"""Forms ``/surveys/{id}/history`` client on the httpx2 core (a form's change log)."""

from ycli.yandex.core.listing import Listing
from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.history import endpoints
from ycli.yandex.forms.history.models import HistoryEvent


class HistoryClient(Resource):
    """Read the change log of a form."""

    def list(
        self,
        survey_id: str,
        *,
        ordering: str | None = None,
        limit: int | None = None,
        next: str | None = None,
    ) -> Listing[HistoryEvent]:
        """``GET /surveys/{id}/history`` → the form's changes, page by page, at most ``limit``.

        ``ordering`` is ``desc`` (newest first, the API default) or ``asc``.

        Args:
            survey_id: The form's id.
            ordering: ``desc`` (newest first) or ``asc``.
            limit: The most events to return; ``None`` returns every event.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The form's change events.

        Examples:
            >>> events = forms.history.list("686d0a1b2c3d4e5f000000e1", ordering="asc", limit=500)
            >>> [event.model for event in events]
            ['servicesurveyhooksubscription', 'surveyhook']
        """
        paged = endpoints.list_(survey_id, ordering=ordering)
        return self._session.iterate(paged, limit=limit, next=next)
