"""Declarative Forms /surveys client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""
import uplink

from ycli.yandex.forms._base import FormsResource
from ycli.yandex.forms.surveys.models import Survey, SurveyCollection, SurveyList
from ycli.yandex.pagination import SinglePageStrategy


class SurveysClient(FormsResource):
    """Declarative HTTP for ``/surveys`` (list envelope + single get)."""

    @uplink.returns.json()
    @uplink.get("surveys")
    def _list_page(self) -> SurveyList:  # ty: ignore[empty-body]
        """``GET /surveys`` → raw ``SurveyList`` envelope (internal)."""

    def list(self, *, limit: int | None = None) -> SurveyCollection:
        """``GET /surveys`` → flat :class:`SurveyCollection`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.list().root[0].name  # doctest: +SKIP
            'Новая задача'
        """
        items = SinglePageStrategy(extract=lambda page: page.result).collect(
            lambda cursor: self._list_page(), limit
        )
        return SurveyCollection(items)

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}")
    def get(self, survey_id: uplink.Path) -> Survey:  # ty: ignore[empty-body]
        """``GET /surveys/{id}`` → a single ``Survey`` (settings).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.get(survey_id="686d0a1b2c3d4e5f").is_published  # doctest: +SKIP
            True
        """
