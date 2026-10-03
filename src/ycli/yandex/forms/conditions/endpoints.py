"""Forms display-condition operations, declared once (sans-IO).

The four condition targets share one shape: a target path (a question, a page, the submit
button, an integration group) under which the same six operations live. A ``*_target``
function builds the target path; the six operation functions take it.

Examples:
    >>> list_conditions(question_target("686d", "17")).path
    'surveys/686d/questions/17/conditions'
    >>> set_operator(submit_target("686d"), "or").json
    {'operator': 'or'}
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.models import Condition, ConditionsResponse


def question_target(survey_id: str, question_id: str) -> str:
    return f"surveys/{segment(survey_id)}/questions/{segment(question_id)}/conditions"


def page_target(survey_id: str, page_id: int) -> str:
    return f"surveys/{segment(survey_id)}/pages/{segment(page_id)}/conditions"


def submit_target(survey_id: str) -> str:
    return f"surveys/{segment(survey_id)}/conditions"


def hook_target(survey_id: str, hook_id: int) -> str:
    return f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/conditions"


def list_conditions(target: str) -> Endpoint[ConditionsResponse]:
    return Endpoint("GET", target, ConditionsResponse)


def get_condition(target: str, condition_id: int) -> Endpoint[Condition]:
    return Endpoint("GET", f"{target}/{segment(condition_id)}", Condition)


def create_condition(target: str, body: dict[str, Any]) -> Endpoint[Condition]:
    return Endpoint("POST", target, Condition, json=body)


def modify_condition(target: str, condition_id: int, body: dict[str, Any]) -> Endpoint[Condition]:
    return Endpoint("PATCH", f"{target}/{segment(condition_id)}", Condition, json=body)


def delete_condition(target: str, condition_id: int) -> Endpoint[None]:
    return Endpoint("DELETE", f"{target}/{segment(condition_id)}")


def set_operator(target: str, operator: str) -> Endpoint[ConditionsResponse]:
    """``PATCH`` on the collection sets the operator BETWEEN the groups."""
    return Endpoint("PATCH", target, ConditionsResponse, json={"operator": operator})
