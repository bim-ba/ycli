"""Forms answers client on the httpx2 core: ``/surveys/{id}/answers`` plus the flat ``/answers``."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.answers import endpoints
from ycli.yandex.forms.answers.models import (
    Answer,
    AnswerDetails,
    AnswerIntegrationList,
    AnswersResponse,
    Column,
)

if TYPE_CHECKING:
    from ycli.yandex.forms.models import OperationResult


class AnswersClient(Resource):
    """Read answers, list them page by page, and export them."""

    def get(self, *, answer_id: int | None = None, answer_key: str | None = None) -> AnswerDetails:
        """``GET /answers?answer_id=…`` (or ``?answer_key=…``) → one full :class:`AnswerDetails`.

        Exactly one selector: ``answer_id`` (the numeric id from a listing; needs form-edit
        access) or ``answer_key`` (the answer's hash; works without form-edit access).

        Args:
            answer_id: The numeric answer id.
            answer_key: The answer's hash.

        Returns:
            The full answer.

        Raises:
            ValueError: If both or neither of ``answer_id`` and ``answer_key`` are given.

        Examples:
            >>> forms.answers.get(answer_id=2469549806).survey.name
            'Feedback'
        """
        if (answer_id is None) == (answer_key is None):
            raise ValueError("pass exactly one of answer_id or answer_key")
        return self._session.send(endpoints.get_answer(answer_id=answer_id, answer_key=answer_key))

    def list(self, survey_id: str) -> AnswersResponse:
        """``GET /surveys/{id}/answers`` → the first page's ``{columns, answers, next}`` envelope.

        Args:
            survey_id: The form's id.

        Returns:
            The first page of answers, with its columns.

        Examples:
            >>> forms.answers.list("686d0a1b2c3d4e5f00000030").columns[0].slug
            'answer_short_text_1'
        """
        return self._session.send(endpoints.list_answers(survey_id).endpoint)

    def list_all(self, survey_id: str, *, limit: int | None = None) -> AnswersResponse:
        """Every answer across pages, at most ``limit`` (``None`` = all).

        ``columns`` come from the first page (identical across pages); the merged ``next`` is
        ``None``.

        Args:
            survey_id: The form's id.
            limit: The most answers to return; ``None`` returns every answer.

        Returns:
            The answers of every page, with the first page's columns.

        Examples:
            >>> len(forms.answers.list_all("686d0a1b2c3d4e5f00000030", limit=500).answers)
            1
        """
        paged = endpoints.list_answers(survey_id)
        columns: list[Column] = []

        def items_of(page: AnswersResponse) -> list[Answer]:
            if not columns:
                columns.extend(page.columns)
            return page.answers

        answers = list(self._session.iterate(replace(paged, items_of=items_of), limit=limit))
        return AnswersResponse(columns=columns, answers=answers, next=None)

    def export(self, survey_id: str, body: dict[str, Any]) -> OperationResult:
        """``POST /surveys/{id}/answers/export`` — start an export → ``202`` with its operation.

        Build ``body`` from an ``AnswerExport``; poll :meth:`export_results` (or
        ``operations.get``) on the returned ``id`` until ready, then :meth:`download_export`.

        Args:
            survey_id: The form's id.
            body: The dumped ``AnswerExport``: format, destination and filters.

        Returns:
            The export operation, with its ``id`` to poll.

        Examples:
            >>> forms.answers.export(
            ...     "686d0a1b2c3d4e5f00000030", {"format": "csv", "upload": "disk"}
            ... ).id
            'op-77'
        """
        return self._session.send(endpoints.export_answers(survey_id, body))

    def export_results(self, survey_id: str, task_id: str) -> OperationResult:
        """``GET /surveys/{id}/answers/export-results?task_id=`` → the export's status.

        While running or failed it answers ``{id, status, message}``; once ready it redirects to
        the exported file, reported as a terminal ``ok``.

        Args:
            survey_id: The form's id.
            task_id: The export operation's ``id``.

        Returns:
            The export's status.

        Examples:
            >>> forms.answers.export_results("686d0a1b2c3d4e5f00000030", "op-77").status
            'running'
        """
        return self._session.send(endpoints.export_results(survey_id, task_id))

    def download_export(self, survey_id: str, task_id: str) -> bytes:
        """The exported file's raw bytes, once :meth:`export_results` reports it ready.

        Binary payload — SDK and CLI only, never an MCP result.

        Args:
            survey_id: The form's id.
            task_id: The export operation's ``id``.

        Returns:
            The exported file's raw bytes.

        Examples:
            >>> forms.answers.export_results("686d0a1b2c3d4e5f00000030", "op-77").status  # poll
            'running'
            >>> # ...until it is no longer running, then:
            >>> forms.answers.download_export("686d0a1b2c3d4e5f00000030", "op-77").splitlines()[0]
            b'id,name'
        """
        return self._session.send(endpoints.download_export(survey_id, task_id))

    def integrations_list(
        self, *, answer_id: int | None = None, answer_key: str | None = None
    ) -> AnswerIntegrationList:
        """``GET /answers/integrations`` → the integration runs one answer triggered.

        Exactly one selector, as for :meth:`get`.

        Args:
            answer_id: The numeric answer id.
            answer_key: The answer's hash.

        Returns:
            The integration runs the answer triggered.

        Raises:
            ValueError: If both or neither of ``answer_id`` and ``answer_key`` are given.

        Examples:
            >>> forms.answers.integrations_list(answer_id=2542485382).root[0].status
            'success'
        """
        if (answer_id is None) == (answer_key is None):
            raise ValueError("pass exactly one of answer_id or answer_key")
        return self._session.send(
            endpoints.list_answer_integrations(answer_id=answer_id, answer_key=answer_key)
        )

    def delete(self, survey_id: str, answer_id: int) -> None:
        """``DELETE /surveys/{id}/answers/{answer_id}`` — delete an answer; see :meth:`restore`.

        Args:
            survey_id: The form's id.
            answer_id: The numeric answer id.

        Examples:
            >>> forms.answers.delete("686d0a1b2c3d4e5f00000031", 2542485431)
        """
        self._session.send(endpoints.delete_answer(survey_id, answer_id))

    def restore(self, survey_id: str, answer_id: int) -> None:
        """``POST /surveys/{id}/answers/{answer_id}/restore`` — bring a deleted answer back.

        Args:
            survey_id: The form's id.
            answer_id: The numeric answer id.

        Examples:
            >>> forms.answers.restore("686d0a1b2c3d4e5f00000032", 2542485498)
        """
        self._session.send(endpoints.restore_answer(survey_id, answer_id))
