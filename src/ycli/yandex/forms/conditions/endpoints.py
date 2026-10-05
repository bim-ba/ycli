"""Forms display-condition operations, declared once (sans-IO).

The four condition targets (a question, a page, the submit button, an integration group) take
the same six operations, and Yandex publishes each of the 24 on its own: one function per
published operation, named like the client method that sends it.

Examples:
    >>> question_list("686d", "17").path
    'surveys/686d/questions/17/conditions'
    >>> submit_update_operator("686d", "or").json
    {'operator': 'or'}
"""

from __future__ import annotations

from http import HTTPMethod
from typing import TYPE_CHECKING

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.models import Condition, ConditionsResponse

if TYPE_CHECKING:
    from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionUpdate


def question_list(survey_id: str, question_id: str) -> Endpoint[ConditionsResponse]:
    return Endpoint(
        HTTPMethod.GET,
        f"surveys/{segment(survey_id)}/questions/{segment(question_id)}/conditions",
        ConditionsResponse,
    )


def question_get(survey_id: str, question_id: str, condition_id: int) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.GET,
        f"surveys/{segment(survey_id)}/questions/{segment(question_id)}/conditions/{segment(condition_id)}",
        Condition,
    )


def question_create(survey_id: str, question_id: str, body: ConditionCreate) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.POST,
        f"surveys/{segment(survey_id)}/questions/{segment(question_id)}/conditions",
        Condition,
        json=body,
    )


def question_update(
    survey_id: str, question_id: str, condition_id: int, body: ConditionUpdate
) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/questions/{segment(question_id)}/conditions/{segment(condition_id)}",
        Condition,
        json=body,
    )


def question_delete(survey_id: str, question_id: str, condition_id: int) -> Endpoint[None]:
    return Endpoint(
        HTTPMethod.DELETE,
        f"surveys/{segment(survey_id)}/questions/{segment(question_id)}/conditions/{segment(condition_id)}",
    )


def question_update_operator(
    survey_id: str, question_id: str, operator: str
) -> Endpoint[ConditionsResponse]:
    """``PATCH`` on the collection sets the operator BETWEEN the groups."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/questions/{segment(question_id)}/conditions",
        ConditionsResponse,
        json={"operator": operator},
    )


def page_list(survey_id: str, page_id: int) -> Endpoint[ConditionsResponse]:
    return Endpoint(
        HTTPMethod.GET,
        f"surveys/{segment(survey_id)}/pages/{segment(page_id)}/conditions",
        ConditionsResponse,
    )


def page_get(survey_id: str, page_id: int, condition_id: int) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.GET,
        f"surveys/{segment(survey_id)}/pages/{segment(page_id)}/conditions/{segment(condition_id)}",
        Condition,
    )


def page_create(survey_id: str, page_id: int, body: ConditionCreate) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.POST,
        f"surveys/{segment(survey_id)}/pages/{segment(page_id)}/conditions",
        Condition,
        json=body,
    )


def page_update(
    survey_id: str, page_id: int, condition_id: int, body: ConditionUpdate
) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/pages/{segment(page_id)}/conditions/{segment(condition_id)}",
        Condition,
        json=body,
    )


def page_delete(survey_id: str, page_id: int, condition_id: int) -> Endpoint[None]:
    return Endpoint(
        HTTPMethod.DELETE,
        f"surveys/{segment(survey_id)}/pages/{segment(page_id)}/conditions/{segment(condition_id)}",
    )


def page_update_operator(
    survey_id: str, page_id: int, operator: str
) -> Endpoint[ConditionsResponse]:
    """``PATCH`` on the collection sets the operator BETWEEN the groups."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/pages/{segment(page_id)}/conditions",
        ConditionsResponse,
        json={"operator": operator},
    )


def submit_list(survey_id: str) -> Endpoint[ConditionsResponse]:
    return Endpoint(HTTPMethod.GET, f"surveys/{segment(survey_id)}/conditions", ConditionsResponse)


def submit_get(survey_id: str, condition_id: int) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.GET,
        f"surveys/{segment(survey_id)}/conditions/{segment(condition_id)}",
        Condition,
    )


def submit_create(survey_id: str, body: ConditionCreate) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.POST, f"surveys/{segment(survey_id)}/conditions", Condition, json=body
    )


def submit_update(survey_id: str, condition_id: int, body: ConditionUpdate) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/conditions/{segment(condition_id)}",
        Condition,
        json=body,
    )


def submit_delete(survey_id: str, condition_id: int) -> Endpoint[None]:
    return Endpoint(
        HTTPMethod.DELETE, f"surveys/{segment(survey_id)}/conditions/{segment(condition_id)}"
    )


def submit_update_operator(survey_id: str, operator: str) -> Endpoint[ConditionsResponse]:
    """``PATCH`` on the collection sets the operator BETWEEN the groups."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/conditions",
        ConditionsResponse,
        json={"operator": operator},
    )


def hook_list(survey_id: str, hook_id: int) -> Endpoint[ConditionsResponse]:
    return Endpoint(
        HTTPMethod.GET,
        f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/conditions",
        ConditionsResponse,
    )


def hook_get(survey_id: str, hook_id: int, condition_id: int) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.GET,
        f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/conditions/{segment(condition_id)}",
        Condition,
    )


def hook_create(survey_id: str, hook_id: int, body: ConditionCreate) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.POST,
        f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/conditions",
        Condition,
        json=body,
    )


def hook_update(
    survey_id: str, hook_id: int, condition_id: int, body: ConditionUpdate
) -> Endpoint[Condition]:
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/conditions/{segment(condition_id)}",
        Condition,
        json=body,
    )


def hook_delete(survey_id: str, hook_id: int, condition_id: int) -> Endpoint[None]:
    return Endpoint(
        HTTPMethod.DELETE,
        f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/conditions/{segment(condition_id)}",
    )


def hook_update_operator(
    survey_id: str, hook_id: int, operator: str
) -> Endpoint[ConditionsResponse]:
    """``PATCH`` on the collection sets the operator BETWEEN the groups."""
    return Endpoint(
        HTTPMethod.PATCH,
        f"surveys/{segment(survey_id)}/hooks/{segment(hook_id)}/conditions",
        ConditionsResponse,
        json={"operator": operator},
    )
