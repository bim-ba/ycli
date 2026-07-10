"""Pydantic v2 models for Yandex Wiki /recovery_tokens responses (extra='ignore')."""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel


class RecoveredPage(APIModel):
    """The page restored by ``POST /recovery_tokens/{token}/recover`` — its ``id`` and ``slug``.

    Returned when a ``recovery_token`` (from ``pages.delete``) is redeemed; the page reappears
    at ``slug`` under numeric ``id``.

    Example:
        >>> RecoveredPage.model_validate({"id": 42, "slug": "data/x"}).slug
        'data/x'
    """

    id: int | None = Field(default=None, description="Numeric id of the restored page.")
    slug: str | None = Field(default=None, description="Permanent slug the page was restored to.")
