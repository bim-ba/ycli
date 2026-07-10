"""Declarative Forms answers client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

from urllib.parse import urljoin

import requests
import uplink

from ycli.yandex.forms.answers.models import AnswerDetail, AnswersResponse, ExportResult
from ycli.yandex.forms.base import FormsResource
from ycli.yandex.pagination import NextUrlStrategy


class AnswersClient(FormsResource):
    """Declarative HTTP for ``/surveys/{id}/answers``."""

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/answers/{answer_id}")
    def get(self, survey_id: uplink.Path, answer_id: uplink.Path) -> AnswerDetail:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/answers/{answer_id}`` → a single rich :class:`AnswerDetail`.

        Where :meth:`list` returns a flat positional table across all responses, this returns
        one response keyed by ``answer_id`` with per-question detail (label, type, value, scores).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.answers.get(survey_id="686d0a1b", answer_id=99).data[
            ...     0
            ... ].label  # doctest: +SKIP
            'Your name'
        """

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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/answers/export")
    def export(self, survey_id: uplink.Path, body: uplink.Body) -> ExportResult:  # ty: ignore[empty-body]
        """``POST /surveys/{id}/answers/export`` — start an async export → ``202`` ExportResult.

        An *action* (SDK/CLI only, never MCP): it kicks off a background job and returns its
        ``{id, status, message}``. Build ``body`` from an
        :class:`~ycli.yandex.forms.answers.models.AnswerExport`; then poll :meth:`export_results`
        (or ``operations.get``) on the returned ``id`` until ready and fetch it with
        :meth:`download_export`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.answers.export("686d0a1b2c3d4e5f", {"format": "xlsx"}).id  # doctest: +SKIP
            'op-4a1b…'
        """

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/answers/export-results")
    def export_results(self, survey_id: uplink.Path, task_id: uplink.Query) -> ExportResult:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/answers/export-results?task_id=`` → the export's ExportResult.

        The status read for an export started by :meth:`export`; answers ``200``/``202`` with
        ``{id, status, message}`` while running or done, and ``302``-redirects to the file once
        ready. Poll this until :attr:`ExportResult.is_terminal`, then use :meth:`download_export`
        for the bytes.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.answers.export_results(
            ...     "686d0a1b2c3d4e5f", "op-4a1b"
            ... ).status  # doctest: +SKIP
            'ok'
        """

    @uplink.get("surveys/{survey_id}/answers/export-results")
    def _download_export(self, survey_id: uplink.Path, task_id: uplink.Query) -> requests.Response:  # ty: ignore[empty-body]
        """Raw export bytes — follows the ``302`` to the file (internal; use ``download_export``).

        No ``@uplink.returns.json()`` — this is the exported file (a byte stream), not JSON."""

    def download_export(self, survey_id: str, task_id: str) -> bytes:
        """``GET …/answers/export-results?task_id=`` (once ready) → the exported file's raw bytes.

        Binary payload — SDK/CLI only (never MCP: a base64 blob is not an agent payload). The
        transport raises a typed ``YandexError`` on any non-2xx before this returns; call it only
        after :meth:`export_results` reports :attr:`ExportResult.is_ready`.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> Path("answers.xlsx").write_bytes(
            ...     client.answers.download_export("686d0a1b2c3d4e5f", "op-4a1b")
            ... )  # doctest: +SKIP
        """
        return self._download_export(survey_id, task_id).content
