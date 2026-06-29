"""Declarative Forms /surveys client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.forms._base import FormsResource
from ycli.yandex.forms.surveys.models import Survey, SurveyList, SurveysResponse
from ycli.yandex.pagination import collect_single_page


class SurveysClient(FormsResource):
    """Declarative HTTP for ``/surveys`` (list envelope + single get)."""

    @uplink.returns.json()
    @uplink.get("surveys")
    def _list_page(self) -> SurveysResponse:  # ty: ignore[empty-body]
        """``GET /surveys`` → raw ``SurveysResponse`` envelope (internal)."""

    def list(self, *, limit: int | None = None) -> SurveyList:
        """``GET /surveys`` → flat :class:`SurveyList`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.list().root[0].name  # doctest: +SKIP
            'Новая задача'
        """
        return collect_single_page(
            lambda cursor: self._list_page(),
            extract=lambda page: page.result,
            wrap=SurveyList,
            limit=limit,
        )

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}")
    def get(self, survey_id: uplink.Path) -> Survey:  # ty: ignore[empty-body]
        """``GET /surveys/{id}`` → a single ``Survey`` (settings).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.get(survey_id="686d0a1b2c3d4e5f").is_published  # doctest: +SKIP
            True
        """
