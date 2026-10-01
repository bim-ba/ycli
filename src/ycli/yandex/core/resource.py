"""``Resource`` — the base of every resource client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.yandex.core.session import SyncSession


class Resource:
    """Holds the session a resource client sends its endpoints through.

    Example:
        >>> class SurveysClient(Resource):  # doctest: +SKIP
        ...     def get(self, survey_id: str) -> Survey:
        ...         return self._session.send(endpoints.get_survey(survey_id))
    """

    def __init__(self, *, session: SyncSession) -> None:
        self._session = session
