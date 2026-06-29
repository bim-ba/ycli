"""Declarative Forms answers client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

from urllib.parse import urljoin

import uplink

from ycli.yandex.forms._base import FormsResource
from ycli.yandex.forms.answers.models import AnswersResponse
from ycli.yandex.pagination import NextUrlStrategy


class AnswersClient(FormsResource):
    """Declarative HTTP for ``/surveys/{id}/answers``."""

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/answers")
    def list(self, survey_id: uplink.Path) -> AnswersResponse:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/answers`` → the ``{columns, answers, next}`` envelope (verbatim).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.answers.list(survey_id="686d0a1b2c3d4e5f").columns[0].slug  # doctest: +SKIP
            'answer_short_text_1'
        """

    def list_all(self, survey_id: str, *, limit: int | None = None) -> AnswersResponse:
        """Drain responses across pages (HATEOAS ``next.next_url``), capped at ``limit``.

        The single-page :meth:`list` under-reports — the API paginates via the ``id``
        cursor and hands the next page back as ``next.next_url`` (null when exhausted).
        ``columns`` come from the first page (identical across pages); the merged
        ``next`` is always ``None``. Pass ``limit=None`` to fetch every page.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> len(client.answers.list_all(survey_id="686d0a1b2c3d4e5f").answers)  # doctest: +SKIP
            317
        """
        first = self.list(survey_id)
        columns = first.columns

        def fetch_url(url: str) -> AnswersResponse:
            absolute = urljoin(self.base_url.rstrip("/") + "/", url)
            return AnswersResponse.model_validate(self._session.get(absolute).json())

        answers = NextUrlStrategy(
            extract=lambda page: page.answers,
            next_url_of=lambda page: (
                page.next.get("next_url") if isinstance(page.next, dict) else None
            ),
            fetch_url=fetch_url,
        ).collect(lambda cursor: first, limit)
        return AnswersResponse(columns=columns, answers=answers, next=None)
