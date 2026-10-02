"""Forms ``/surveys/{id}/questions`` operations, declared once (sans-IO).

Example:
    >>> delete_question("686d", "17", force=True).params
    {'force': 'true'}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.questions.models import Question, QuestionMoveResult, QuestionsResponse


def _questions(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/questions"


def get_question(survey_id: str, question_id: str) -> Endpoint[Question]:
    return Endpoint("GET", f"{_questions(survey_id)}/{segment(question_id)}", Question)


def list_questions(survey_id: str) -> Endpoint[QuestionsResponse]:
    return Endpoint("GET", _questions(survey_id), QuestionsResponse)


def create_question(survey_id: str, body: dict[str, Any]) -> Endpoint[Question]:
    return Endpoint("POST", _questions(survey_id), Question, json=body)


def modify_question(survey_id: str, question_id: str, body: dict[str, Any]) -> Endpoint[Question]:
    path = f"{_questions(survey_id)}/{segment(question_id)}"
    return Endpoint("PATCH", path, Question, json=body)


def delete_question(survey_id: str, question_id: str, *, force: bool) -> Endpoint[None]:
    path = f"{_questions(survey_id)}/{segment(question_id)}"
    return Endpoint("DELETE", path, params={"force": "true" if force else None})


def move_question(
    survey_id: str, question_id: str, body: dict[str, Any]
) -> Endpoint[QuestionMoveResult]:
    path = f"{_questions(survey_id)}/{segment(question_id)}/move"
    return Endpoint("POST", path, QuestionMoveResult, json=body)
