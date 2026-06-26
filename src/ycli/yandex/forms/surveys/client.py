"""Declarative Forms /surveys client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""
import uplink

from ycli.yandex.forms._base import FormsResource
from ycli.yandex.forms.surveys.models import Survey, SurveyList


class SurveysClient(FormsResource):
    """Declarative HTTP for ``/surveys`` (list envelope + single get)."""

    @uplink.timeout(30)
    @uplink.returns.json()
    @uplink.get("surveys")
    def list(self) -> SurveyList:  # ty: ignore[empty-body]
        """``GET /surveys`` → the ``{links, result}`` envelope (verbatim).

        Example:
            >>> client = FormsClient.from_env()  # doctest: +SKIP
            >>> client.surveys.list().result[0].name  # doctest: +SKIP
            'Новая задача'
        """

    @uplink.timeout(30)
    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}")
    def get(self, survey_id: uplink.Path) -> Survey:  # ty: ignore[empty-body]
        """``GET /surveys/{id}`` → a single ``Survey`` (settings).

        Example:
            >>> client = FormsClient.from_env()  # doctest: +SKIP
            >>> client.surveys.get(survey_id="686d0a1b2c3d4e5f").is_published  # doctest: +SKIP
            True
        """
