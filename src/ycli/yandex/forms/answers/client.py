"""Declarative Forms answers client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""
from urllib.parse import urljoin

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

    def list_all(self, survey_id: str) -> AnswersResponse:
        """Drain *every* page of responses into one merged envelope.

        The single-page :meth:`list` under-reports — the API paginates via the ``id``
        cursor and hands the next page back as ``next.next_url`` (null when exhausted).
        Follow that link verbatim (HATEOAS-style — no fragile cursor reconstruction)
        until it is null, concatenating ``answers``. ``columns`` are taken from the
        first page (identical across pages); the merged ``next`` is always ``None``.

        Example:
            >>> client = FormsClient.from_env()  # doctest: +SKIP
            >>> len(client.answers.list_all(survey_id="686d0a1b2c3d4e5f").answers)  # doctest: +SKIP
            317
        """
        page = self.list(survey_id)
        columns = page.columns
        answers = list(page.answers)
        seen: set[str] = set()
        nxt = page.next
        while isinstance(nxt, dict) and nxt.get("next_url"):
            url = urljoin(self.base_url.rstrip("/") + "/", str(nxt["next_url"]))
            if url in seen:  # defensive: a server pointing at itself must not hang us
                break
            seen.add(url)
            resp = self._session.get(url)
            page = AnswersResponse.model_validate(resp.json())
            answers.extend(page.answers)
            nxt = page.next
        return AnswersResponse(columns=columns, answers=answers, next=None)
