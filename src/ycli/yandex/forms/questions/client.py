"""Forms ``/surveys/{id}/questions`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.questions import endpoints
from ycli.yandex.models import Ack

if TYPE_CHECKING:
    from ycli.yandex.forms.questions.models import (
        Question,
        QuestionCreate,
        QuestionMove,
        QuestionMoveResult,
        QuestionsResponse,
    )


class QuestionsClient(Resource):
    """Get, list, create, modify, delete and move the questions of a form."""

    def get(self, survey_id: str, question_id: str) -> Question:
        """``GET /surveys/{id}/questions/{question_id}`` → a single :class:`Question` (settings).

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.questions.get("686d0a1b", "17").slug  # doctest: +SKIP
            'answer_short_text_1'
        """
        return self._session.send(endpoints.get_question(survey_id, question_id))

    def list(self, survey_id: str) -> QuestionsResponse:
        """``GET /surveys/{id}/questions`` → every question, grouped into the ``{pages}`` envelope.

        Example:
            >>> client.questions.list("686d0a1b2c3d4e5f").pages[0].items[0].slug  # doctest: +SKIP
            'answer_short_text_1'
        """
        return self._session.send(endpoints.list_questions(survey_id))

    def create(self, survey_id: str, body: QuestionCreate) -> Question:
        """``POST /surveys/{id}/questions`` — append a question from a typed body.

        ``body`` is one member of the :data:`~ycli.yandex.forms.questions.models.QuestionCreate`
        union (``StringQuestion``, ``EnumQuestion``, …). The question lands at the end of the
        form; reorder it with :meth:`move`.

        Example:
            >>> from ycli.yandex.forms.questions.models import StringQuestion
            >>> client.questions.create(
            ...     "686d0a1b", StringQuestion(label="Name")
            ... ).id  # doctest: +SKIP
            17
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_question(survey_id, dumped))

    def modify(self, survey_id: str, question_id: str, body: QuestionCreate) -> Question:
        """``PATCH /surveys/{id}/questions/{question_id}`` — replace a question's settings.

        Takes the same typed body as :meth:`create`; its type must match the existing question.

        Example:
            >>> client.questions.modify(
            ...     "686d0a1b", "17", StringQuestion(label="Full name")
            ... ).label  # doctest: +SKIP
            'Full name'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.modify_question(survey_id, question_id, dumped))

    def delete(self, survey_id: str, question_id: str, *, force: bool = False) -> Ack:
        """``DELETE /surveys/{id}/questions/{question_id}`` → an :class:`Ack`.

        The API refuses to delete a question that another question's display conditions still
        reference; ``force=True`` skips that check.

        Example:
            >>> client.questions.delete("686d0a1b", "17", force=True).ok  # doctest: +SKIP
            True
        """
        self._session.send(endpoints.delete_question(survey_id, question_id, force=force))
        return Ack.deleted("question", question_id, on=f"survey {survey_id}")

    def move(self, survey_id: str, question_id: str, body: QuestionMove) -> QuestionMoveResult:
        """``POST /surveys/{id}/questions/{question_id}/move`` — reposition a question.

        ``body`` names the target page (``page`` / ``page_id`` / ``create_page``) and
        ``position``; the API ignores a bare ``position``, so ``QuestionMove`` refuses one.

        Example:
            >>> from ycli.yandex.forms.questions.models import QuestionMove
            >>> client.questions.move(
            ...     "686d0a1b", "17", QuestionMove(page=2, position=1)
            ... ).id  # doctest: +SKIP
            17
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.move_question(survey_id, question_id, dumped))
