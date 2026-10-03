"""Forms ``/surveys/{id}/questions`` client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.questions import endpoints
from ycli.yandex.forms.questions.models import FORCE_IGNORED
from ycli.yandex.models import Ack, warn_ignored

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

    def get(self, survey_id: str, question_id: str, *, with_slugs: bool = False) -> Question:
        """``GET /surveys/{id}/questions/{question_id}`` → a single :class:`Question` (settings).

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            with_slugs: The API's flag of that name: refer to other questions by slug.

        Returns:
            The question.

        Examples:
            >>> forms.questions.get("686d0a1b2c3d4e5f00000010", "17").slug
            'name'
        """
        endpoint = endpoints.get_question(survey_id, question_id, with_slugs=with_slugs)
        return self._session.send(endpoint)

    def list(self, survey_id: str) -> QuestionsResponse:
        """``GET /surveys/{id}/questions`` → every question, grouped into the ``{pages}`` envelope.

        Args:
            survey_id: The form's id.

        Returns:
            Every question, grouped by page.

        Examples:
            >>> forms.questions.list("686d0a1b2c3d4e5f00000010").pages[0].items[0].slug
            'name'
        """
        return self._session.send(endpoints.list_questions(survey_id))

    def create(self, survey_id: str, body: QuestionCreate) -> Question:
        """``POST /surveys/{id}/questions`` — append a question from a typed body.

        ``body`` is one member of the :data:`~ycli.yandex.forms.questions.models.QuestionCreate`
        union (``StringQuestion``, ``EnumQuestion``, …). The question lands at the end of the
        form; reorder it with :meth:`move`.

        Args:
            survey_id: The form's id.
            body: The new question's settings.

        Returns:
            The created question, with its ``id``.

        Examples:
            >>> from ycli.yandex.forms.questions.models import StringQuestion
            >>> forms.questions.create("686d0a1b2c3d4e5f00000010", StringQuestion(label="Name")).id
            17
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.create_question(survey_id, dumped))

    def modify(self, survey_id: str, question_id: str, body: QuestionCreate) -> Question:
        """``PATCH /surveys/{id}/questions/{question_id}`` — replace a question's settings.

        Takes the same typed body as :meth:`create`; its type must match the existing question.

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            body: The question's new settings.

        Returns:
            The updated question.

        Examples:
            >>> from ycli.yandex.forms.questions.models import StringQuestion
            >>> forms.questions.modify(
            ...     "686d0a1b2c3d4e5f00000010", "22", StringQuestion(label="Name")
            ... ).label
            'Name'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.modify_question(survey_id, question_id, dumped))

    def delete(self, survey_id: str, question_id: str, *, force: bool = False) -> Ack:
        """``DELETE /surveys/{id}/questions/{question_id}`` → an :class:`Ack`.

        The API refuses to delete a question that another question's display conditions still
        reference (400 ``dependency_error.question_condition``): delete the condition first.
        ``force`` is sent, and the API ignores it (checked live on 2026-10-04).

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            force: Ignored by the API: the display-conditions check is not skipped.

        Returns:
            An acknowledgement naming the deleted question.

        Examples:
            >>> forms.questions.delete("686d0a1b2c3d4e5f00000010", "28").ok
            True
        """
        if force:
            warn_ignored("force", FORCE_IGNORED)
        self._session.send(endpoints.delete_question(survey_id, question_id, force=force))
        return Ack.deleted("question", question_id, on=f"survey {survey_id}")

    def move(self, survey_id: str, question_id: str, body: QuestionMove) -> QuestionMoveResult:
        """``POST /surveys/{id}/questions/{question_id}/move`` — reposition a question.

        ``body`` names the target page (``page`` / ``page_id`` / ``create_page``) and
        ``position``; the API ignores a bare ``position``, so ``QuestionMove`` refuses one.

        Args:
            survey_id: The form's id.
            question_id: The question's id.
            body: The target page and position.

        Returns:
            The result, carrying the moved question's ``id``.

        Examples:
            >>> from ycli.yandex.forms.questions.models import QuestionMove
            >>> forms.questions.move(
            ...     "686d0a1b2c3d4e5f00000010", "20", QuestionMove(page_id=55, position=2)
            ... ).id
            20
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.move_question(survey_id, question_id, dumped))
