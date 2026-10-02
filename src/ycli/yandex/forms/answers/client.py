"""Forms answers client on the httpx2 core: ``/surveys/{id}/answers`` plus the flat ``/answers``."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.answers import endpoints
from ycli.yandex.forms.answers.models import (
    Answer,
    AnswerDetails,
    AnswerIntegrationList,
    AnswersResponse,
    Column,
    ExportResult,
)


class AnswersClient(Resource):
    """Read answers, list them page by page, and export them."""

    def get(self, *, answer_id: int | None = None, answer_key: str | None = None) -> AnswerDetails:
        """``GET /answers?answer_id=…`` (or ``?answer_key=…``) → one full :class:`AnswerDetails`.

        Exactly one selector: ``answer_id`` (the numeric id from a listing; needs form-edit
        access) or ``answer_key`` (the answer's hash; works without form-edit access).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.answers.get(answer_id=2469549806).survey.name  # doctest: +SKIP
            'Feedback'
        """
        if (answer_id is None) == (answer_key is None):
            raise ValueError("pass exactly one of answer_id or answer_key")
        return self._session.send(endpoints.get_answer(answer_id=answer_id, answer_key=answer_key))

    def list(self, survey_id: str) -> AnswersResponse:
        """``GET /surveys/{id}/answers`` → the first page's ``{columns, answers, next}`` envelope.

        Example:
            >>> client.answers.list("686d0a1b2c3d4e5f").columns[0].slug  # doctest: +SKIP
            'answer_short_text_1'
        """
        return self._session.send(endpoints.list_answers(survey_id).endpoint)

    def list_all(self, survey_id: str, *, limit: int | None = None) -> AnswersResponse:
        """Every answer across pages, at most ``limit`` (``None`` = all).

        ``columns`` come from the first page (identical across pages); the merged ``next`` is
        ``None``.

        Example:
            >>> len(client.answers.list_all("686d0a1b2c3d4e5f").answers)  # doctest: +SKIP
            317
        """
        paged = endpoints.list_answers(survey_id)
        columns: list[Column] = []

        def items_of(page: AnswersResponse) -> list[Answer]:
            if not columns:
                columns.extend(page.columns)
            return page.answers

        answers = list(self._session.iterate(replace(paged, items_of=items_of), limit=limit))
        return AnswersResponse(columns=columns, answers=answers, next=None)

    def export(self, survey_id: str, body: dict[str, Any]) -> ExportResult:
        """``POST /surveys/{id}/answers/export`` — start an export → ``202`` with its operation.

        Build ``body`` from an ``AnswerExport``; poll :meth:`export_results` (or
        ``operations.get``) on the returned ``id`` until ready, then :meth:`download_export`.

        Example:
            >>> client.answers.export("686d0a1b2c3d4e5f", {"format": "xlsx"}).id  # doctest: +SKIP
            'op-4a1b…'
        """
        return self._session.send(endpoints.export_answers(survey_id, body))

    def export_results(self, survey_id: str, task_id: str) -> ExportResult:
        """``GET /surveys/{id}/answers/export-results?task_id=`` → the export's status.

        While running or failed it answers ``{id, status, message}``; once ready it redirects to
        the exported file, reported as a terminal ``ok``.

        Example:
            >>> client.answers.export_results(
            ...     "686d0a1b2c3d4e5f", "op-4a1b"
            ... ).status  # doctest: +SKIP
            'ok'
        """
        return self._session.send(endpoints.export_results(survey_id, task_id))

    def download_export(self, survey_id: str, task_id: str) -> bytes:
        """The exported file's raw bytes, once :meth:`export_results` reports it ready.

        Binary payload — SDK and CLI only, never an MCP result.

        Example:
            >>> Path("answers.xlsx").write_bytes(
            ...     client.answers.download_export("686d0a1b2c3d4e5f", "op-4a1b")
            ... )  # doctest: +SKIP
        """
        return self._session.send(endpoints.download_export(survey_id, task_id))

    def integrations_list(
        self, *, answer_id: int | None = None, answer_key: str | None = None
    ) -> AnswerIntegrationList:
        """``GET /answers/integrations`` → the integration runs one answer triggered.

        Exactly one selector, as for :meth:`get`.

        Example:
            >>> client.answers.integrations_list(answer_id=2469549806).root[
            ...     0
            ... ].status  # doctest: +SKIP
            'success'
        """
        if (answer_id is None) == (answer_key is None):
            raise ValueError("pass exactly one of answer_id or answer_key")
        return self._session.send(
            endpoints.list_answer_integrations(answer_id=answer_id, answer_key=answer_key)
        )

    def delete(self, survey_id: str, answer_id: int) -> None:
        """``DELETE /surveys/{id}/answers/{answer_id}`` — delete an answer; see :meth:`restore`.

        Example:
            >>> client.answers.delete("686d0a1b2c3d4e5f", 2469549806)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_answer(survey_id, answer_id))

    def restore(self, survey_id: str, answer_id: int) -> None:
        """``POST /surveys/{id}/answers/{answer_id}/restore`` — bring a deleted answer back.

        Example:
            >>> client.answers.restore("686d0a1b2c3d4e5f", 2469549806)  # doctest: +SKIP
        """
        self._session.send(endpoints.restore_answer(survey_id, answer_id))
