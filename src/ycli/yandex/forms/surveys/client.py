"""Declarative Forms /surveys client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.surveys.models import Survey, SurveyList, SurveysResponse
from ycli.yandex.pagination import OffsetStrategy

_PAGE_SIZE = 100


class SurveysClient(FormsResource):
    """Declarative HTTP for ``/surveys`` (offset-paged list envelope + single get)."""

    @uplink.returns.json()
    @uplink.get("surveys")
    def _list_page(
        self,
        offset: uplink.Query = 0,  # ty: ignore[invalid-parameter-default]
        limit: uplink.Query = _PAGE_SIZE,  # ty: ignore[invalid-parameter-default]
    ) -> SurveysResponse:  # ty: ignore[empty-body]
        """One raw page of surveys at ``offset`` (page size ``limit``); internal — use ``list``."""

    def list(self, *, limit: int | None = None) -> SurveyList:
        """``GET /surveys`` → flat :class:`SurveyList`, draining offset pages internally.

        Capped at ``limit`` (``None`` = every form). The API pages by ``offset``/``limit``; this
        advances the offset until a short page comes back.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.list(limit=50).root[0].name  # doctest: +SKIP
            'Новая задача'
        """
        strategy = OffsetStrategy(extract=lambda page: page.result, page_size=_PAGE_SIZE)
        surveys = strategy.collect(
            lambda offset: self._list_page(offset=offset, limit=_PAGE_SIZE),
            limit,
        )
        return SurveyList(surveys)

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}")
    def get(self, survey_id: uplink.Path) -> Survey:  # ty: ignore[empty-body]
        """``GET /surveys/{id}`` → a single ``Survey`` (settings).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.surveys.get(survey_id="686d0a1b2c3d4e5f").is_published  # doctest: +SKIP
            True
        """
