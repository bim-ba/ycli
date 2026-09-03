"""Pydantic models for Forms display conditions (question / page / submit show targets).

Read side reuses the questions-owned lenient ``Condition`` / ``ConditionItem`` (single
source, ARCH-5). The list envelope ``{operator, items}`` is SEMANTIC — the top-level
operator joins the groups and is data, not transport — so it stays public
(:class:`ConditionsResponse`; precedent: ``QuestionsResponse``). Write bodies are strict:
the API requires ``operator`` + ``items`` (min 1) on both create and modify (PATCH is a
full replace), and a clause ``value`` is capped at 100 characters.
"""

from pydantic import Field

from ycli.yandex.forms.questions.models import (
    Condition,
    ConditionComparison,
    ConditionItemKind,
    ConditionOperatorType,
)
from ycli.yandex.models import APIModel


class ConditionsResponse(APIModel):
    """The ``{operator, items}`` envelope of a target's condition groups.

    Returned verbatim by every ``*_list`` and ``*_set_operator`` op. Unlike the transport
    envelopes convention §2 flattens, ``operator`` here is data — the boolean operator
    BETWEEN the groups — so the envelope itself is the public return type.

    Example:
        >>> ConditionsResponse.model_validate(
        ...     {"operator": "and", "items": [{"id": 1, "operator": "or", "items": []}]}
        ... ).items[0].id
        1
    """

    operator: str | None = Field(
        default=None, description="Boolean operator joining the condition groups: and / or."
    )
    items: list[Condition] = Field(
        default_factory=list, description="The target's condition groups."
    )


class ConditionItemWrite(APIModel):
    """One clause of a create/modify condition-group body (the API's ``ConditionItemIn``).

    Unlike the lenient read ``ConditionItem``, the write clause enforces the In-schema:
    ``type`` and ``condition`` are required, ``value`` is capped at 100 characters (a
    string even for ``lt``/``gt``), and there is no per-clause ``operator``.

    Example:
        >>> ConditionItemWrite(type="question", condition="eq", question="q1", value="y").value
        'y'
    """

    type: ConditionItemKind = Field(
        description="Clause subject: question, language, origin or quiz."
    )
    condition: ConditionComparison = Field(description="Comparison operator: eq, neq, lt, gt.")
    question: str | None = Field(
        default=None,
        description="Slug of the question the clause tests (required for type=question).",
    )
    value: str | None = Field(
        default=None,
        max_length=100,
        description="Value the clause compares against (string, max 100 chars).",
    )


class ConditionCreate(APIModel):
    """Typed body for ``POST …/conditions`` — one new condition group.

    The API requires both fields: ``operator`` joins the clauses WITHIN the group and
    ``items`` must hold at least one clause. Unset optional clause fields are dropped
    before the request is sent.

    Example:
        >>> ConditionCreate(
        ...     operator="and", items=[ConditionItemWrite(type="language", condition="eq")]
        ... ).operator
        'and'
    """

    operator: ConditionOperatorType = Field(
        description="Boolean operator joining the clauses within the group: and / or."
    )
    items: list[ConditionItemWrite] = Field(
        min_length=1, description="Clauses of the group (at least one)."
    )


class ConditionUpdate(ConditionCreate):
    """Typed body for ``PATCH …/conditions/{condition_id}`` — a FULL replacement.

    Same shape as :class:`ConditionCreate`: despite the PATCH verb the API validates the
    body as a complete group (``operator`` and ``items`` with min 1 clause are both
    required) — there is no partial update, and the group ``id`` is never sent.

    Example:
        >>> ConditionUpdate(
        ...     operator="or", items=[ConditionItemWrite(type="origin", condition="neq")]
        ... ).operator
        'or'
    """
