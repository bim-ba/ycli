"""Pydantic v2 models for Yandex Wiki /recovery_tokens responses."""

from pydantic import Field

from ycli.yandex.wiki.models import PageIdentity


class RecoveredPage(PageIdentity):
    """The page a restore brought back, and how many pages came back with it.

    Examples:
        >>> RecoveredPage.model_validate({"id": 7, "slug": "data/x", "pages_count": 3}).pages_count
        3
    """

    pages_count: int | None = Field(
        default=None, description="Number of pages restored: the page and those under it."
    )
