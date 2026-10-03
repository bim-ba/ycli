"""Forms ``/surveys/{id}/questions`` operations, declared once (sans-IO).

Examples:
    >>> delete_question("686d", "17", force=True).params
    {'force': 'true'}
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, flag, segment
from ycli.yandex.forms.questions.models import (
    Question,
    QuestionCreate,
    QuestionMove,
    QuestionMoveResult,
    QuestionsResponse,
)


def _questions(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/questions"


def get_question(survey_id: str, question_id: str, *, with_slugs: bool) -> Endpoint[Question]:
    path = f"{_questions(survey_id)}/{segment(question_id)}"
    return Endpoint("GET", path, Question, params={"with_slugs": flag(with_slugs)})


def list_questions(survey_id: str) -> Endpoint[QuestionsResponse]:
    return Endpoint("GET", _questions(survey_id), QuestionsResponse)


def create_question(survey_id: str, body: QuestionCreate) -> Endpoint[Question]:
    return Endpoint("POST", _questions(survey_id), Question, json=body)


def modify_question(survey_id: str, question_id: str, body: QuestionCreate) -> Endpoint[Question]:
    path = f"{_questions(survey_id)}/{segment(question_id)}"
    return Endpoint("PATCH", path, Question, json=body)


def delete_question(survey_id: str, question_id: str, *, force: bool) -> Endpoint[None]:
    path = f"{_questions(survey_id)}/{segment(question_id)}"
    return Endpoint("DELETE", path, params={"force": flag(force)})


def move_question(
    survey_id: str, question_id: str, body: QuestionMove
) -> Endpoint[QuestionMoveResult]:
    path = f"{_questions(survey_id)}/{segment(question_id)}/move"
    return Endpoint("POST", path, QuestionMoveResult, json=body)
