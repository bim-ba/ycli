"""Pydantic models for Forms questions (Question + Page + QuestionsResponse envelope)."""

from __future__ import annotations

from pydantic import Field

from ycli.models import APIModel


class Question(APIModel):
    """A single question item within a page (``…/questions`` → ``pages[].items[]``).

    ``id`` is an **int**. Type-specific fields (``data_source``, ``items``,
    ``validators``, ``conditions``, …) are lenient-ignored.

    Example:
        >>> Question.model_validate({"id": 1, "slug": "s", "type": "string", "label": "L"}).slug
        's'
    """

    id: int | None = None
    label: str | None = None
    slug: str | None = None
    type: str | None = None
    hidden: bool | None = None
    comment: str | None = None


class Page(APIModel):
    """A page grouping questions (``…/questions`` → ``pages[]``).

    Example:
        >>> Page.model_validate({"id": 7, "items": [{"id": 1}]}).items[0].id
        1
    """

    id: int | None = None
    items: list[Question] = Field(default_factory=list)


class QuestionsResponse(APIModel):
    """Envelope for ``GET …/questions`` — ``{pages:[Page]}``.

    Example:
        >>> QuestionsResponse.model_validate({"pages": [{"items": [{"id": 1}]}]}).pages[0].items[
        ...     0
        ... ].id
        1
    """

    pages: list[Page] = Field(default_factory=list)
