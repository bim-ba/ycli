"""Pydantic models for Forms display conditions (question / page / submit / hook targets).

The read side reuses the questions-owned lenient ``Condition`` / ``ConditionItem`` (one source,
ARCH-5). The list envelope ``{operator, items}`` is semantic: the top-level operator joins the
groups and is data, not transport, so it stays public (:class:`ConditionsResponse`; precedent:
``QuestionsResponse``). Write bodies are strict: the API requires ``operator`` + ``items``
(at least one) on both create and modify (PATCH is a full replace), and a clause ``value`` is
capped at 100 characters.
"""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.forms.models import (
    ConditionComparison,
    ConditionItemKind,
    ConditionOperatorType,
)
from ycli.yandex.models import RequestBody


class ConditionItemWrite(RequestBody):
    """One clause of a create/modify condition-group body (the API's ``ConditionItemIn``).

    Unlike the lenient read ``ConditionItem``, the write clause enforces the input schema:
    ``type`` and ``condition`` are required, ``value`` is capped at 100 characters (a string
    even for ``lt``/``gt``), and there is no per-clause ``operator``.

    Examples:
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


class ConditionCreate(RequestBody):
    """Typed body for ``POST …/conditions`` — one new condition group.

    The API requires both fields: ``operator`` joins the clauses WITHIN the group and
    ``items`` must hold at least one clause. Unset optional clause fields are dropped before
    the request is sent.

    Examples:
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

    Same shape as :class:`ConditionCreate`: despite the PATCH verb the API validates the body
    as a complete group (``operator`` and at least one clause are both required); there is no
    partial update, and the group ``id`` is never sent.

    Examples:
        >>> ConditionUpdate(
        ...     operator="or", items=[ConditionItemWrite(type="origin", condition="neq")]
        ... ).operator
        'or'
    """
