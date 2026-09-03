"""Forms display-conditions FastMCP tools (reads + writes, honest hints)."""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.conditions.models import (
    Condition,
    ConditionCreate,
    ConditionsResponse,
    ConditionUpdate,
)
from ycli.yandex.forms.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAGS,
    forms_client,
)
from ycli.yandex.models import Ack, require_found

mcp = FastMCP("forms-conditions")


# --------------------------------------------------------------------------------------------
# question family
# --------------------------------------------------------------------------------------------


@mcp.tool(
    name="conditions_question_list",
    annotations={**RO, "title": "List Forms question show conditions"},
    tags=TAGS,
)
def question_list(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    question_id: Annotated[str, Field(description="Question id (integer) from questions_list.")],
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """A question's show conditions: the ``{operator, items}`` envelope of condition groups.

    The top-level ``operator`` joins the GROUPS; each group has its own ``operator``
    joining its clauses. A group's integer ``id`` is what the get/modify/delete tools take.

    Example:
        >>> conditions_question_list(
        ...     survey_id="6818ceffe010db4f59d11329", question_id="17"
        ... )  # doctest: +SKIP
    """
    return client.conditions.question_list(survey_id, question_id)


@mcp.tool(
    name="conditions_question_get",
    annotations={**RO, "title": "Get Forms question show condition"},
    tags=TAGS,
)
def question_get(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    question_id: Annotated[str, Field(description="Question id (integer) from questions_list.")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_question_list.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """One condition group by id — its ``operator`` and clause ``items``.

    A "condition" here is a GROUP of clauses; individual clauses have no ids and are
    edited only by replacing the whole group via ``conditions_question_modify``.

    Example:
        >>> conditions_question_get(
        ...     survey_id="6818ceffe010db4f59d11329", question_id="17", condition_id=5
        ... )  # doctest: +SKIP
    """
    result = client.conditions.question_get(survey_id, question_id, condition_id)
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message=f"condition {condition_id!r} not found on question {question_id!r} "
        f"in survey {survey_id!r} (empty response — check ids or permissions)",
    )


@mcp.tool(
    name="conditions_question_create",
    annotations={**WRITE, "title": "Create Forms question show condition"},
    tags=WRITE_TAGS,
)
def question_create(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    question_id: Annotated[str, Field(description="Question id (integer) from questions_list.")],
    body: Annotated[
        ConditionCreate, Field(description="The new group: operator + at least one clause.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Create a condition group on a question — it shows only when its conditions match.

    The group ``operator`` joins the clauses WITHIN it, and at least one clause is
    required. Returns the created group with its server-assigned integer ``id``.

    Example:
        >>> conditions_question_create(
        ...     survey_id="6818ceffe010db4f59d11329",
        ...     question_id="17",
        ...     body={"operator": "and", "items": [{"type": "question", "condition": "eq"}]},
        ... )  # doctest: +SKIP
    """
    return client.conditions.question_create(survey_id, question_id, body)


@mcp.tool(
    name="conditions_question_modify",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms question show condition"},
    tags=WRITE_TAGS,
)
def question_modify(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    question_id: Annotated[str, Field(description="Question id (integer) from questions_list.")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_question_list.")
    ],
    body: Annotated[
        ConditionUpdate,
        Field(description="FULL replacement (PATCH validates the complete group)."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Replace condition group ``condition_id`` — a FULL replacement, not a partial update.

    Despite the PATCH verb the API validates the body as a complete group: ``operator`` and
    at least one clause are both required; the group ``id`` is never sent. Clauses have no
    ids of their own — editing one clause means resending the whole group.

    Example:
        >>> conditions_question_modify(
        ...     survey_id="6818ceffe010db4f59d11329",
        ...     question_id="17",
        ...     condition_id=5,
        ...     body={"operator": "or", "items": [{"type": "language", "condition": "eq"}]},
        ... )  # doctest: +SKIP
    """
    return client.conditions.question_modify(survey_id, question_id, condition_id, body)


@mcp.tool(
    name="conditions_question_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms question show condition"},
    tags=WRITE_TAGS,
)
def question_delete(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    question_id: Annotated[str, Field(description="Question id (integer) from questions_list.")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_question_list.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one condition group from a question; the other groups stay untouched.

    The API answers ``200 OK`` with no body, so a typed acknowledgement is returned.

    Example:
        >>> conditions_question_delete(
        ...     survey_id="6818ceffe010db4f59d11329", question_id="17", condition_id=5
        ... )  # doctest: +SKIP
    """
    return client.conditions.question_delete(survey_id, question_id, condition_id)


@mcp.tool(
    name="conditions_question_set_operator",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms question conditions operator"},
    tags=WRITE_TAGS,
)
def question_set_operator(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    question_id: Annotated[str, Field(description="Question id (integer) from questions_list.")],
    operator: Annotated[
        Literal["and", "or"], Field(description="Boolean operator joining the condition groups.")
    ],
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """Set the boolean operator BETWEEN a question's condition groups (collection PATCH).

    Group-internal operators are untouched — change those via ``conditions_question_modify``.
    Idempotent: the body fully determines the state. Returns the full ``{operator, items}``
    envelope, exactly like ``conditions_question_list``.

    Example:
        >>> conditions_question_set_operator(
        ...     survey_id="6818ceffe010db4f59d11329", question_id="17", operator="or"
        ... )  # doctest: +SKIP
    """
    return client.conditions.question_set_operator(survey_id, question_id, operator)


# --------------------------------------------------------------------------------------------
# page family
# --------------------------------------------------------------------------------------------


@mcp.tool(
    name="conditions_page_list",
    annotations={**RO, "title": "List Forms page show conditions"},
    tags=TAGS,
)
def page_list(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    page_id: Annotated[int, Field(description="Page id (integer) from questions_list pages.")],
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """A page's show conditions: the ``{operator, items}`` envelope of condition groups.

    The top-level ``operator`` joins the GROUPS; each group has its own ``operator``
    joining its clauses. A group's integer ``id`` is what the get/modify/delete tools take.

    Example:
        >>> conditions_page_list(survey_id="6818ceffe010db4f59d11329", page_id=3)  # doctest: +SKIP
    """
    return client.conditions.page_list(survey_id, page_id)


@mcp.tool(
    name="conditions_page_get",
    annotations={**RO, "title": "Get Forms page show condition"},
    tags=TAGS,
)
def page_get(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    page_id: Annotated[int, Field(description="Page id (integer) from questions_list pages.")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_page_list.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """One condition group by id — its ``operator`` and clause ``items``.

    A "condition" here is a GROUP of clauses; individual clauses have no ids and are
    edited only by replacing the whole group via ``conditions_page_modify``.

    Example:
        >>> conditions_page_get(
        ...     survey_id="6818ceffe010db4f59d11329", page_id=3, condition_id=5
        ... )  # doctest: +SKIP
    """
    result = client.conditions.page_get(survey_id, page_id, condition_id)
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message=f"condition {condition_id!r} not found on page {page_id!r} "
        f"in survey {survey_id!r} (empty response — check ids or permissions)",
    )


@mcp.tool(
    name="conditions_page_create",
    annotations={**WRITE, "title": "Create Forms page show condition"},
    tags=WRITE_TAGS,
)
def page_create(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    page_id: Annotated[int, Field(description="Page id (integer) from questions_list pages.")],
    body: Annotated[
        ConditionCreate, Field(description="The new group: operator + at least one clause.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Create a condition group on a page — it shows only when its conditions match.

    Page clauses still reference QUESTION slugs (``type=question`` + ``question``). The
    group ``operator`` joins the clauses within it, and at least one clause is required.
    Returns the created group with its server-assigned integer ``id``.

    Example:
        >>> conditions_page_create(
        ...     survey_id="6818ceffe010db4f59d11329",
        ...     page_id=3,
        ...     body={"operator": "and", "items": [{"type": "question", "condition": "eq"}]},
        ... )  # doctest: +SKIP
    """
    return client.conditions.page_create(survey_id, page_id, body)


@mcp.tool(
    name="conditions_page_modify",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms page show condition"},
    tags=WRITE_TAGS,
)
def page_modify(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    page_id: Annotated[int, Field(description="Page id (integer) from questions_list pages.")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_page_list.")
    ],
    body: Annotated[
        ConditionUpdate,
        Field(description="FULL replacement (PATCH validates the complete group)."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Replace condition group ``condition_id`` — a FULL replacement, not a partial update.

    Despite the PATCH verb the API validates the body as a complete group: ``operator`` and
    at least one clause are both required; the group ``id`` is never sent. Clauses have no
    ids of their own — editing one clause means resending the whole group.

    Example:
        >>> conditions_page_modify(
        ...     survey_id="6818ceffe010db4f59d11329",
        ...     page_id=3,
        ...     condition_id=5,
        ...     body={"operator": "or", "items": [{"type": "language", "condition": "eq"}]},
        ... )  # doctest: +SKIP
    """
    return client.conditions.page_modify(survey_id, page_id, condition_id, body)


@mcp.tool(
    name="conditions_page_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms page show condition"},
    tags=WRITE_TAGS,
)
def page_delete(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    page_id: Annotated[int, Field(description="Page id (integer) from questions_list pages.")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_page_list.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one condition group from a page; the other groups stay untouched.

    The API answers ``200 OK`` with no body, so a typed acknowledgement is returned.

    Example:
        >>> conditions_page_delete(
        ...     survey_id="6818ceffe010db4f59d11329", page_id=3, condition_id=5
        ... )  # doctest: +SKIP
    """
    return client.conditions.page_delete(survey_id, page_id, condition_id)


@mcp.tool(
    name="conditions_page_set_operator",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms page conditions operator"},
    tags=WRITE_TAGS,
)
def page_set_operator(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    page_id: Annotated[int, Field(description="Page id (integer) from questions_list pages.")],
    operator: Annotated[
        Literal["and", "or"], Field(description="Boolean operator joining the condition groups.")
    ],
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """Set the boolean operator BETWEEN a page's condition groups (collection PATCH).

    Group-internal operators are untouched — change those via ``conditions_page_modify``.
    Idempotent: the body fully determines the state. Returns the full ``{operator, items}``
    envelope, exactly like ``conditions_page_list``.

    Example:
        >>> conditions_page_set_operator(
        ...     survey_id="6818ceffe010db4f59d11329", page_id=3, operator="or"
        ... )  # doctest: +SKIP
    """
    return client.conditions.page_set_operator(survey_id, page_id, operator)


# --------------------------------------------------------------------------------------------
# submit family (conditions of the form's Submit button, right on the survey)
# --------------------------------------------------------------------------------------------


@mcp.tool(
    name="conditions_submit_list",
    annotations={**RO, "title": "List Forms submit-button show conditions"},
    tags=TAGS,
)
def submit_list(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """The submit button's show conditions: the ``{operator, items}`` envelope of groups.

    These hang directly on the survey (``GET /surveys/{id}/conditions`` — no intermediate
    segment). The top-level ``operator`` joins the GROUPS; each group has its own
    ``operator`` joining its clauses.

    Example:
        >>> conditions_submit_list(survey_id="6818ceffe010db4f59d11329")  # doctest: +SKIP
    """
    return client.conditions.submit_list(survey_id)


@mcp.tool(
    name="conditions_submit_get",
    annotations={**RO, "title": "Get Forms submit-button show condition"},
    tags=TAGS,
)
def submit_get(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_submit_list.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """One condition group by id — its ``operator`` and clause ``items``.

    A "condition" here is a GROUP of clauses; individual clauses have no ids and are
    edited only by replacing the whole group via ``conditions_submit_modify``.

    Example:
        >>> conditions_submit_get(
        ...     survey_id="6818ceffe010db4f59d11329", condition_id=5
        ... )  # doctest: +SKIP
    """
    result = client.conditions.submit_get(survey_id, condition_id)
    return require_found(
        result,
        sentinel=lambda r: r.id is None,
        message=f"condition {condition_id!r} not found in survey {survey_id!r} "
        "(empty response — check ids or permissions)",
    )


@mcp.tool(
    name="conditions_submit_create",
    annotations={**WRITE, "title": "Create Forms submit-button show condition"},
    tags=WRITE_TAGS,
)
def submit_create(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    body: Annotated[
        ConditionCreate, Field(description="The new group: operator + at least one clause.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Create a condition group gating the form's submit button.

    Clauses reference question slugs (``type=question`` + ``question``). The group
    ``operator`` joins the clauses within it, and at least one clause is required.
    Returns the created group with its server-assigned integer ``id``.

    Example:
        >>> conditions_submit_create(
        ...     survey_id="6818ceffe010db4f59d11329",
        ...     body={"operator": "and", "items": [{"type": "question", "condition": "eq"}]},
        ... )  # doctest: +SKIP
    """
    return client.conditions.submit_create(survey_id, body)


@mcp.tool(
    name="conditions_submit_modify",
    annotations={**WRITE_IDEMPOTENT, "title": "Modify Forms submit-button show condition"},
    tags=WRITE_TAGS,
)
def submit_modify(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_submit_list.")
    ],
    body: Annotated[
        ConditionUpdate,
        Field(description="FULL replacement (PATCH validates the complete group)."),
    ],
    client: FormsClient = Depends(forms_client),
) -> Condition:
    """Replace condition group ``condition_id`` — a FULL replacement, not a partial update.

    Despite the PATCH verb the API validates the body as a complete group: ``operator`` and
    at least one clause are both required; the group ``id`` is never sent. Clauses have no
    ids of their own — editing one clause means resending the whole group.

    Example:
        >>> conditions_submit_modify(
        ...     survey_id="6818ceffe010db4f59d11329",
        ...     condition_id=5,
        ...     body={"operator": "or", "items": [{"type": "language", "condition": "eq"}]},
        ... )  # doctest: +SKIP
    """
    return client.conditions.submit_modify(survey_id, condition_id, body)


@mcp.tool(
    name="conditions_submit_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Forms submit-button show condition"},
    tags=WRITE_TAGS,
)
def submit_delete(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    condition_id: Annotated[
        int, Field(description="Condition group id (integer) from conditions_submit_list.")
    ],
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete one condition group from the submit button; the other groups stay untouched.

    The API answers ``200 OK`` with no body, so a typed acknowledgement is returned.

    Example:
        >>> conditions_submit_delete(
        ...     survey_id="6818ceffe010db4f59d11329", condition_id=5
        ... )  # doctest: +SKIP
    """
    return client.conditions.submit_delete(survey_id, condition_id)


@mcp.tool(
    name="conditions_submit_set_operator",
    annotations={**WRITE_IDEMPOTENT, "title": "Set Forms submit-button conditions operator"},
    tags=WRITE_TAGS,
)
def submit_set_operator(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    operator: Annotated[
        Literal["and", "or"], Field(description="Boolean operator joining the condition groups.")
    ],
    client: FormsClient = Depends(forms_client),
) -> ConditionsResponse:
    """Set the boolean operator BETWEEN the submit button's condition groups.

    A collection-level PATCH; group-internal operators are untouched — change those via
    ``conditions_submit_modify``. Idempotent: the body fully determines the state. Returns
    the full ``{operator, items}`` envelope, exactly like ``conditions_submit_list``.

    Example:
        >>> conditions_submit_set_operator(
        ...     survey_id="6818ceffe010db4f59d11329", operator="or"
        ... )  # doctest: +SKIP
    """
    return client.conditions.submit_set_operator(survey_id, operator)
