"""Forms display-conditions FastMCP tools (reads + writes, honest hints).

Four targets carry condition groups: a question, a page, the submit button and an integration
group (hook). Each target has the same six tools: list, get, create, update (a full
replacement), delete and set_operator (the operator BETWEEN the target's groups).
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.conditions.models import ConditionCreate, ConditionUpdate
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    SurveyId,
    forms_client,
)
from ycli.yandex.forms.models import Condition, ConditionsResponse
from ycli.yandex.models import Ack, require_found

mcp = FastMCP("forms-conditions")

QuestionId = Annotated[str, Field(description="Question id (integer) from questions_list.")]
PageId = Annotated[int, Field(description="Page id (integer) from questions_list pages.")]
HookId = Annotated[int, Field(description="Integration group id (integer) from hooks_list.")]
ConditionId = Annotated[
    int, Field(description="Condition group id (integer) from the matching *_list tool.")
]
Operator = Annotated[
    Literal["and", "or"], Field(description="Boolean operator joining the condition groups.")
]
NewGroup = Annotated[
    ConditionCreate, Field(description="The new group: operator + at least one clause.")
]
ReplacementGroup = Annotated[
    ConditionUpdate, Field(description="FULL replacement (PATCH validates the complete group).")
]


def _found(result: Condition, condition_id: int, where: str) -> Condition:
    # A 404 / empty body parses into an all-None group (lenient model): report it as missing.
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message=f"condition {condition_id!r} not found on {where} "
        "(empty response — check ids or permissions)",
    )


# --- question family ---


@mcp.tool(
    name="conditions_question_list",
    annotations={**RO, "title": "List Forms question show conditions"},
    tags=TAGS,
)
def question_list(
    survey_id: SurveyId, question_id: QuestionId, client: FormsClient = Depends(forms_client)
) -> ConditionsResponse:
    """A question's show conditions: the ``{operator, items}`` envelope of condition groups.

    The top-level ``operator`` joins the GROUPS; each group has its own ``operator`` joining its
    clauses. A group's integer ``id`` is what the get/update/delete tools take.
    """
    return client.conditions.question_list(survey_id, question_id)


@mcp.tool(
    name="conditions_question_get",
    annotations={**RO, "title": "Get Forms question show condition"},
    tags=TAGS,
)
def question_get(
    survey_id: SurveyId,
    question_id: QuestionId,
    condition_id: ConditionId,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """One condition group of a question by id — its ``operator`` and clause ``items``.

    Clauses have no ids of their own: edit one by replacing the whole group via
    ``conditions_question_update``.
    """
    result = client.conditions.question_get(survey_id, question_id, condition_id)
    return _found(result, condition_id, f"question {question_id!r} in survey {survey_id!r}")


@mcp.tool(
    name="conditions_question_create",
    annotations={**WRITE, "title": "Create Forms question show condition"},
    tags=WRITE_TAGS,
)
def question_create(
    survey_id: SurveyId,
    question_id: QuestionId,
    body: NewGroup,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Add a condition group to a question — it shows only when its conditions match.

    The group ``operator`` joins the clauses WITHIN it; at least one clause is required.
    Returns the created group with its server-assigned integer ``id``.
    """
    return client.conditions.question_create(survey_id, question_id, body)


@mcp.tool(
    name="conditions_question_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms question show condition"},
    tags=WRITE_TAGS,
)
def question_update(
    survey_id: SurveyId,
    question_id: QuestionId,
    condition_id: ConditionId,
    body: ReplacementGroup,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Replace a question's condition group — a FULL replacement, not a partial update.

    Despite the PATCH verb the API validates a complete group: ``operator`` and at least one
    clause are both required; the group ``id`` is never sent.
    """
    return client.conditions.question_update(survey_id, question_id, condition_id, body)


@mcp.tool(
    name="conditions_question_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms question show condition"},
    tags=WRITE_TAGS,
)
def question_delete(
    survey_id: SurveyId,
    question_id: QuestionId,
    condition_id: ConditionId,
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one condition group from a question; the other groups stay untouched."""
    client.conditions.question_delete(survey_id, question_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"question {question_id}")


@mcp.tool(
    name="conditions_question_set_operator",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms question conditions operator"},
    tags=WRITE_TAGS,
)
def question_set_operator(
    survey_id: SurveyId,
    question_id: QuestionId,
    operator: Operator,
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """Set the boolean operator BETWEEN a question's condition groups; returns the envelope.

    Group-internal operators are untouched — change those via ``conditions_question_update``.
    """
    return client.conditions.question_set_operator(survey_id, question_id, operator)


# --- page family ---


@mcp.tool(
    name="conditions_page_list",
    annotations={**RO, "title": "List Forms page show conditions"},
    tags=TAGS,
)
def page_list(
    survey_id: SurveyId, page_id: PageId, client: FormsClient = Depends(forms_client)
) -> ConditionsResponse:
    """A page's show conditions: the ``{operator, items}`` envelope of condition groups.

    The top-level ``operator`` joins the GROUPS; each group has its own ``operator`` joining its
    clauses. A group's integer ``id`` is what the get/update/delete tools take.
    """
    return client.conditions.page_list(survey_id, page_id)


@mcp.tool(
    name="conditions_page_get",
    annotations={**RO, "title": "Get Forms page show condition"},
    tags=TAGS,
)
def page_get(
    survey_id: SurveyId,
    page_id: PageId,
    condition_id: ConditionId,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """One condition group of a page by id — its ``operator`` and clause ``items``."""
    result = client.conditions.page_get(survey_id, page_id, condition_id)
    return _found(result, condition_id, f"page {page_id!r} in survey {survey_id!r}")


@mcp.tool(
    name="conditions_page_create",
    annotations={**WRITE, "title": "Create Forms page show condition"},
    tags=WRITE_TAGS,
)
def page_create(
    survey_id: SurveyId,
    page_id: PageId,
    body: NewGroup,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Add a condition group to a page — the page shows only when its conditions match.

    Page clauses still reference QUESTION slugs (``type=question`` + ``question``). Returns the
    created group with its server-assigned integer ``id``.
    """
    return client.conditions.page_create(survey_id, page_id, body)


@mcp.tool(
    name="conditions_page_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms page show condition"},
    tags=WRITE_TAGS,
)
def page_update(
    survey_id: SurveyId,
    page_id: PageId,
    condition_id: ConditionId,
    body: ReplacementGroup,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Replace a page's condition group — a FULL replacement, not a partial update."""
    return client.conditions.page_update(survey_id, page_id, condition_id, body)


@mcp.tool(
    name="conditions_page_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms page show condition"},
    tags=WRITE_TAGS,
)
def page_delete(
    survey_id: SurveyId,
    page_id: PageId,
    condition_id: ConditionId,
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one condition group from a page; the other groups stay untouched."""
    client.conditions.page_delete(survey_id, page_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"page {page_id}")


@mcp.tool(
    name="conditions_page_set_operator",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms page conditions operator"},
    tags=WRITE_TAGS,
)
def page_set_operator(
    survey_id: SurveyId,
    page_id: PageId,
    operator: Operator,
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """Set the boolean operator BETWEEN a page's condition groups; returns the envelope."""
    return client.conditions.page_set_operator(survey_id, page_id, operator)


# --- submit family (conditions of the form's Submit button, right on the survey) ---


@mcp.tool(
    name="conditions_submit_list",
    annotations={**RO, "title": "List Forms submit-button show conditions"},
    tags=TAGS,
)
def submit_list(
    survey_id: SurveyId, client: FormsClient = Depends(forms_client)
) -> ConditionsResponse:
    """The submit button's show conditions: the ``{operator, items}`` envelope of groups.

    These hang directly on the survey (``GET /surveys/{id}/conditions``).
    """
    return client.conditions.submit_list(survey_id)


@mcp.tool(
    name="conditions_submit_get",
    annotations={**RO, "title": "Get Forms submit-button show condition"},
    tags=TAGS,
)
def submit_get(
    survey_id: SurveyId, condition_id: ConditionId, client: FormsClient = Depends(forms_client)
) -> Condition:
    """One condition group of the submit button by id — its ``operator`` and clauses."""
    result = client.conditions.submit_get(survey_id, condition_id)
    return _found(result, condition_id, f"survey {survey_id!r}")


@mcp.tool(
    name="conditions_submit_create",
    annotations={**WRITE, "title": "Create Forms submit-button show condition"},
    tags=WRITE_TAGS,
)
def submit_create(
    survey_id: SurveyId, body: NewGroup, client: FormsClient = Depends(forms_client)
) -> Condition:
    """Add a condition group gating the form's submit button; returns it with its ``id``."""
    return client.conditions.submit_create(survey_id, body)


@mcp.tool(
    name="conditions_submit_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms submit-button show condition"},
    tags=WRITE_TAGS,
)
def submit_update(
    survey_id: SurveyId,
    condition_id: ConditionId,
    body: ReplacementGroup,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Replace a submit-button condition group — a FULL replacement, not a partial update."""
    return client.conditions.submit_update(survey_id, condition_id, body)


@mcp.tool(
    name="conditions_submit_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms submit-button show condition"},
    tags=WRITE_TAGS,
)
def submit_delete(
    survey_id: SurveyId, condition_id: ConditionId, client: FormsClient = Depends(forms_client)
) -> Ack:
    """Delete one condition group from the submit button; the other groups stay untouched."""
    client.conditions.submit_delete(survey_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"survey {survey_id}")


@mcp.tool(
    name="conditions_submit_set_operator",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms submit-button conditions operator"},
    tags=WRITE_TAGS,
)
def submit_set_operator(
    survey_id: SurveyId, operator: Operator, client: FormsClient = Depends(forms_client)
) -> ConditionsResponse:
    """Set the boolean operator BETWEEN the submit button's condition groups."""
    return client.conditions.submit_set_operator(survey_id, operator)


# --- hook family (conditions that gate an integration group) ---


@mcp.tool(
    name="conditions_hook_list",
    annotations={**RO, "title": "List Forms integration-group conditions"},
    tags=TAGS,
)
def hook_list(
    survey_id: SurveyId, hook_id: HookId, client: FormsClient = Depends(forms_client)
) -> ConditionsResponse:
    """An integration group's conditions: the ``{operator, items}`` envelope of groups.

    The group's integrations run on a new answer only when these conditions match.
    """
    return client.conditions.hook_list(survey_id, hook_id)


@mcp.tool(
    name="conditions_hook_get",
    annotations={**RO, "title": "Get Forms integration-group condition"},
    tags=TAGS,
)
def hook_get(
    survey_id: SurveyId,
    hook_id: HookId,
    condition_id: ConditionId,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """One condition group of an integration group by id — its ``operator`` and clauses."""
    result = client.conditions.hook_get(survey_id, hook_id, condition_id)
    return _found(result, condition_id, f"hook {hook_id!r} in survey {survey_id!r}")


@mcp.tool(
    name="conditions_hook_create",
    annotations={**WRITE, "title": "Create Forms integration-group condition"},
    tags=WRITE_TAGS,
)
def hook_create(
    survey_id: SurveyId,
    hook_id: HookId,
    body: NewGroup,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Add a condition group to an integration group; returns it with its ``id``."""
    return client.conditions.hook_create(survey_id, hook_id, body)


@mcp.tool(
    name="conditions_hook_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms integration-group condition"},
    tags=WRITE_TAGS,
)
def hook_update(
    survey_id: SurveyId,
    hook_id: HookId,
    condition_id: ConditionId,
    body: ReplacementGroup,
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Replace an integration group's condition group — a FULL replacement."""
    return client.conditions.hook_update(survey_id, hook_id, condition_id, body)


@mcp.tool(
    name="conditions_hook_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms integration-group condition"},
    tags=WRITE_TAGS,
)
def hook_delete(
    survey_id: SurveyId,
    hook_id: HookId,
    condition_id: ConditionId,
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one condition group from an integration group; the others stay untouched."""
    client.conditions.hook_delete(survey_id, hook_id, condition_id)
    return Ack.deleted("condition", condition_id, from_=f"hook {hook_id}")


@mcp.tool(
    name="conditions_hook_set_operator",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms integration-group conditions operator"},
    tags=WRITE_TAGS,
)
def hook_set_operator(
    survey_id: SurveyId,
    hook_id: HookId,
    operator: Operator,
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """Set the boolean operator BETWEEN an integration group's condition groups."""
    return client.conditions.hook_set_operator(survey_id, hook_id, operator)
