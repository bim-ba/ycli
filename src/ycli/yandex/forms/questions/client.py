"""Declarative Forms questions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.questions.models import QuestionsResponse


class QuestionsClient(FormsResource):
    """Declarative HTTP for ``/surveys/{id}/questions``."""

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/questions")
    def list(self, survey_id: uplink.Path) -> QuestionsResponse:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/questions`` → the ``{pages}`` envelope (verbatim).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.questions.list(survey_id="686d0a1b2c3d4e5f").pages[0].items[
            ...     0
            ... ].slug  # doctest: +SKIP
            'answer_short_text_1'
        """
