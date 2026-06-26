"""Declarative Forms answers client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""
import uplink

from ycli.yandex.forms._base import FormsResource
from ycli.yandex.forms.answers.models import AnswersResponse


class AnswersClient(FormsResource):
    """Declarative HTTP for ``/surveys/{id}/answers``."""

    @uplink.timeout(30)
    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/answers")
    def list(self, survey_id: uplink.Path) -> AnswersResponse:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/answers`` → the ``{columns, answers, next}`` envelope (verbatim).

        Example:
            >>> client = FormsClient.from_env()  # doctest: +SKIP
            >>> client.answers.list(survey_id="686d0a1b2c3d4e5f").columns[0].slug  # doctest: +SKIP
            'answer_short_text_1'
        """
