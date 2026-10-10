"""Forms answers client on the httpx2 core: ``/surveys/{id}/answers`` plus the flat ``/answers``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.answers import endpoints

if TYPE_CHECKING:
    from ycli.yandex.core.listing import Listing
    from ycli.yandex.forms.answers.models import (
        Answer,
        AnswerDetails,
        AnswerExport,
        AnswerIntegration,
        Column,
    )
    from ycli.yandex.forms.models import OperationResult
    from ycli.yandex.models import ItemList


class AnswersClient(Resource):
    """Read answers, list them page by page, and export them."""

    def get(self, *, answer_id: int | None = None, answer_key: str | None = None) -> AnswerDetails:
        """``GET /answers?answer_id=…`` (or ``?answer_key=…``) → one full :class:`AnswerDetails`.

        The API takes one selector: ``answer_id`` (the numeric id from a listing; needs form-edit
        access) or ``answer_key`` (the answer's hash; works without form-edit access).

        Args:
            answer_id: The numeric answer id.
            answer_key: The answer's hash.

        Returns:
            The full answer.

        Examples:
            >>> forms.answers.get(answer_id=2469549806).survey.name
            'Feedback'
        """
        return self._session.send(endpoints.get(answer_id=answer_id, answer_key=answer_key))

    def list(
        self,
        survey_id: str,
        *,
        limit: int | None = None,
        next: str | None = None,
        questions: str | None = None,
        use_slugs: bool | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        ordering: str | None = None,
        page_size: int | None = None,
        answer_format: str | None = None,
    ) -> Listing[Answer]:
        """``GET /surveys/{id}/answers`` → the form's answers, page by page, at most ``limit``.

        The cells of an answer (``data``) stand in the order of :meth:`columns_list`, asked
        with the same ``questions`` and ``use_slugs``; ``answer_format="raw"`` gives each
        answer's data keyed by question instead, which needs no columns.

        Args:
            survey_id: The form's id.
            limit: The most answers to return; ``None`` returns every answer.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            questions: The comma-separated question ids to return answers for.
            use_slugs: Name questions and options by slug instead of id.
            date_from: ISO-8601 start of the period the answers were given in.
            date_to: ISO-8601 end of that period.
            ordering: ``asc`` (oldest first) or ``desc`` (the API's default).
            page_size: The most answers a page holds (the API's default is 25).
            answer_format: ``default`` (cells in the order of the columns) or ``raw`` (each
                answer's data as the API stores it).

        Returns:
            The form's answers.

        Examples:
            >>> [answer.id for answer in forms.answers.list("686d0a1b2c3d4e5f00000030", limit=500)]
            [2, 1]
        """
        paged = endpoints.list_(
            survey_id,
            questions=questions,
            use_slugs=use_slugs,
            date_from=date_from,
            date_to=date_to,
            ordering=ordering,
            page_size=page_size,
            answer_format=answer_format,
        )
        return self._session.iterate(paged, limit=limit, next=next)

    def columns_list(
        self, survey_id: str, *, questions: str | None = None, use_slugs: bool | None = None
    ) -> ItemList[Column]:
        """``GET /surveys/{id}/answers`` → the columns the cells of an answer stand in.

        The API has no request for the columns alone: one answer is read to learn them, and
        left out. A form nobody answered yet has its columns all the same.

        Args:
            survey_id: The form's id.
            questions: The comma-separated question ids to return columns for.
            use_slugs: Name questions by slug instead of id.

        Returns:
            The columns, in the order of the cells of :meth:`list` asked the same way.

        Examples:
            >>> forms.answers.columns_list("686d0a1b2c3d4e5f00000037").root[0].text
            'Name'
        """
        return self._session.send(
            endpoints.columns_list(survey_id, questions=questions, use_slugs=use_slugs)
        )

    def export(self, survey_id: str, body: AnswerExport) -> OperationResult:
        """``POST /surveys/{id}/answers/export`` — start an export → ``202`` with its operation.

        Build ``body`` from an ``AnswerExport``; poll :meth:`export_results_get` (or
        ``operations.get``) on the returned ``id`` until ready, then :meth:`export_download`.

        Args:
            survey_id: The form's id.
            body: The ``AnswerExport``: format, destination and filters.

        Returns:
            The export operation, with its ``id`` to poll.

        Examples:
            >>> from ycli.yandex.forms.answers.models import AnswerExport
            >>> forms.answers.export(
            ...     "686d0a1b2c3d4e5f00000030",
            ...     AnswerExport.model_validate({"format": "csv", "upload": "disk"}),
            ... ).id
            'op-77'
        """
        return self._session.send(endpoints.export(survey_id, body))

    # violation(arch-1): CLI-only, the poll step of `answers export`; MCP serves `export` itself
    def export_results_get(self, survey_id: str, task_id: str) -> OperationResult:
        """``GET /surveys/{id}/answers/export-results?task_id=`` → the export's status.

        While running or failed it answers ``{id, status, message}``; once ready it redirects to
        the exported file, reported as a terminal ``ok``.

        Args:
            survey_id: The form's id.
            task_id: The export operation's ``id``.

        Returns:
            The export's status.

        Examples:
            >>> forms.answers.export_results_get("686d0a1b2c3d4e5f00000030", "op-77").status
            'running'
        """
        return self._session.send(endpoints.export_results_get(survey_id, task_id))

    def export_download(self, survey_id: str, task_id: str) -> bytes:
        """The exported file's raw bytes, once :meth:`export_results_get` reports it ready.

        Binary payload — SDK and CLI only, never an MCP result.

        Args:
            survey_id: The form's id.
            task_id: The export operation's ``id``.

        Returns:
            The exported file's raw bytes.

        Examples:
            >>> forms.answers.export_results_get("686d0a1b2c3d4e5f00000030", "op-77").status  # poll
            'running'
            >>> # ...until it is no longer running, then:
            >>> forms.answers.export_download("686d0a1b2c3d4e5f00000030", "op-77").splitlines()[0]
            b'id,name'
        """
        return self._session.send(endpoints.export_download(survey_id, task_id))

    def integrations_list(
        self, *, answer_id: int | None = None, answer_key: str | None = None
    ) -> ItemList[AnswerIntegration]:
        """``GET /answers/integrations`` → the integration runs one answer triggered.

        One selector, as for :meth:`get`.

        Args:
            answer_id: The numeric answer id.
            answer_key: The answer's hash.

        Returns:
            The integration runs the answer triggered.

        Examples:
            >>> forms.answers.integrations_list(answer_id=2542485382).root[0].status
            'success'
        """
        return self._session.send(
            endpoints.integrations_list(answer_id=answer_id, answer_key=answer_key)
        )

    def delete(self, survey_id: str, answer_id: int) -> None:
        """``DELETE /surveys/{id}/answers/{answer_id}`` — delete an answer; see :meth:`restore`.

        Args:
            survey_id: The form's id.
            answer_id: The numeric answer id.

        Examples:
            >>> forms.answers.delete("686d0a1b2c3d4e5f00000031", 2542485431)
        """
        self._session.send(endpoints.delete(survey_id, answer_id))

    def restore(self, survey_id: str, answer_id: int) -> None:
        """``POST /surveys/{id}/answers/{answer_id}/restore`` — bring a deleted answer back.

        Args:
            survey_id: The form's id.
            answer_id: The numeric answer id.

        Examples:
            >>> forms.answers.restore("686d0a1b2c3d4e5f00000032", 2542485498)
        """
        self._session.send(endpoints.restore(survey_id, answer_id))
