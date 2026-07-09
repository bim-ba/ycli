"""Declarative Forms questions client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.
"""

import requests
import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.questions.models import (
    Question,
    QuestionActionResult,
    QuestionCreate,
    QuestionMove,
    QuestionMoveResult,
    QuestionsResponse,
)


class QuestionsClient(FormsResource):
    """Declarative HTTP for ``/surveys/{id}/questions`` (get/list/create/modify/delete/move)."""

    @uplink.returns.json()
    @uplink.get("surveys/{survey_id}/questions/{question_id}")
    def get(self, survey_id: uplink.Path, question_id: uplink.Path) -> Question:  # ty: ignore[empty-body]
        """``GET /surveys/{id}/questions/{question_id}`` → a single :class:`Question` (settings).

        Where :meth:`list` returns every question grouped into pages, this fetches one question
        keyed by ``question_id``. Type-specific detail (validators, options) is lenient-ignored.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.questions.get(survey_id="686d0a1b", question_id=17).slug  # doctest: +SKIP
            'answer_short_text_1'
        """

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

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/questions")
    def _create(self, survey_id: uplink.Path, body: uplink.Body) -> Question:  # ty: ignore[empty-body]
        """Raw ``POST …/questions`` from a ready dict; internal — callers use ``create``."""

    def create(self, survey_id: str, body: QuestionCreate) -> Question:
        """``POST /surveys/{id}/questions`` — append a question from a typed body.

        ``body`` is one member of the :data:`~ycli.yandex.forms.questions.models.QuestionCreate`
        discriminated union (``StringQuestion``, ``EnumQuestion``, ``MatrixQuestion``, …); it is
        dumped to JSON (``by_alias``, ``exclude_none``) before the request. The new question is
        added to the end of the form; reorder it afterwards with :meth:`move`. Returns the created
        :class:`Question`.

        Example:
            >>> from ycli.yandex.forms.questions.models import StringQuestion
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.questions.create(
            ...     "686d0a1b", StringQuestion(label="Name")
            ... ).id  # doctest: +SKIP
            17
        """
        return self._create(survey_id, body.model_dump(by_alias=True, exclude_none=True))

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("surveys/{survey_id}/questions/{question_id}")
    def _modify(
        self, survey_id: uplink.Path, question_id: uplink.Path, body: uplink.Body
    ) -> Question:  # ty: ignore[empty-body]
        """Raw ``PATCH …/questions/{id}`` from a ready dict; internal — callers use ``modify``."""

    def modify(self, survey_id: str, question_id: str, body: QuestionCreate) -> Question:
        """``PATCH /surveys/{id}/questions/{question_id}`` — replace a question's settings.

        Takes the same typed :data:`~ycli.yandex.forms.questions.models.QuestionCreate` body as
        :meth:`create` (the type must match the existing question). Returns the updated
        :class:`Question`.

        Example:
            >>> from ycli.yandex.forms.questions.models import StringQuestion
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.questions.modify(
            ...     "686d0a1b", "17", StringQuestion(label="Full name")
            ... ).label  # doctest: +SKIP
            'Full name'
        """
        return self._modify(
            survey_id, question_id, body.model_dump(by_alias=True, exclude_none=True)
        )

    @uplink.delete("surveys/{survey_id}/questions/{question_id}")
    def _delete(
        self,
        survey_id: uplink.Path,
        question_id: uplink.Path,
        force: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> requests.Response:  # ty: ignore[empty-body]
        """Raw ``DELETE …/questions/{id}`` (204 No Content); internal — callers use ``delete``."""

    def delete(
        self, survey_id: str, question_id: str, *, force: bool = False
    ) -> QuestionActionResult:
        """``DELETE /surveys/{id}/questions/{question_id}`` → a typed :class:`QuestionActionResult`.

        By default the API refuses to delete a question still referenced by another question's
        display conditions; pass ``force=True`` to skip that check. The API answers ``204 No
        Content``, so the result is synthesized; a non-2xx status raises a typed ``YandexError``
        before this returns.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.questions.delete("686d0a1b", "17", force=True).ok  # doctest: +SKIP
            True
        """
        self._delete(survey_id, question_id, force="true" if force else None)
        return QuestionActionResult(survey_id=survey_id, question_id=question_id, action="delete")

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/questions/{question_id}/move")
    def _move(
        self, survey_id: uplink.Path, question_id: uplink.Path, body: uplink.Body
    ) -> QuestionMoveResult:  # ty: ignore[empty-body]
        """Raw ``POST …/questions/{id}/move`` from a ready dict; internal — callers use ``move``."""

    def move(self, survey_id: str, question_id: str, body: QuestionMove) -> QuestionMoveResult:
        """``POST /surveys/{id}/questions/{question_id}/move`` — reposition a question.

        ``body`` is a typed :class:`~ycli.yandex.forms.questions.models.QuestionMove` naming the
        target page (``page`` / ``page_id`` / ``create_page``) and ``position``; display-condition
        consistency is validated server-side. Returns the moved question's id.

        Example:
            >>> from ycli.yandex.forms.questions.models import QuestionMove
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.questions.move(
            ...     "686d0a1b", "17", QuestionMove(page=2, position=1)
            ... ).id  # doctest: +SKIP
            17
        """
        return self._move(survey_id, question_id, body.model_dump(by_alias=True, exclude_none=True))
