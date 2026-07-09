"""Pydantic models for Forms questions (Question + Page + QuestionsResponse envelope)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ycli.yandex.models import APIModel


class Question(APIModel):
    """A single question / form field.

    Serves both ``GET …/questions`` (``pages[].items[]``) and ``GET …/questions/{id}``
    (a single question's settings). ``id`` is an **int**. Type-specific detail
    (``data_source``, ``items``, ``validators``, ``conditions``, ``image``,
    ``quiz_items``, …) is lenient-ignored — the common fields below cover every type.

    Example:
        >>> Question.model_validate({"id": 1, "slug": "s", "type": "string", "label": "L"}).slug
        's'
    """

    id: int | None = Field(default=None, description="Question ID (integer).")
    label: str | None = Field(default=None, description="Question label / title.")
    slug: str | None = Field(
        default=None, description="Stable machine slug (also the answers-table column key)."
    )
    type: str | None = Field(
        default=None,
        description="Question type — string, boolean, integer, date, daterange, file, enum, "
        "suggest, matrix, comment, payment, series, ….",
    )
    hidden: bool | None = Field(
        default=None,
        description="Whether the question is hidden (shown only when its conditions match).",
    )
    comment: str | None = Field(default=None, description="Question hint / helper text.")
    placeholder: str | None = Field(
        default=None, description="Placeholder text shown in the empty input."
    )
    initial: Any = Field(
        default=None,
        description="Default / initial value; type varies by question type (string, int, bool, "
        "or a list of enum items).",
    )
    multiline: bool | None = Field(
        default=None, description="Whether a text answer spans multiple lines (string questions)."
    )
    has_quiz: bool | None = Field(
        default=None, description="Whether the question is graded as part of a quiz / test."
    )


class Page(APIModel):
    """A page grouping questions (``…/questions`` → ``pages[]``).

    Example:
        >>> Page.model_validate({"id": 7, "items": [{"id": 1}]}).items[0].id
        1
    """

    id: int | None = Field(default=None, description="Page ID (integer).")
    items: list[Question] = Field(
        default_factory=list, description="Questions grouped on this page, in display order."
    )


class QuestionsResponse(APIModel):
    """Envelope for ``GET …/questions`` — ``{pages:[Page]}``.

    Example:
        >>> QuestionsResponse.model_validate({"pages": [{"items": [{"id": 1}]}]}).pages[0].items[
        ...     0
        ... ].id
        1
    """

    pages: list[Page] = Field(
        default_factory=list, description="Form pages, each grouping a set of questions."
    )
