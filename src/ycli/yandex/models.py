"""Shared pydantic base for every Yandex API model — lenient parsing only, no behavior.

Consolidates the per-domain ``_Lenient`` bases. ``extra="ignore"`` keeps unknown API
fields from raising; ``populate_by_name=True`` lets a field be set by its Python name as
well as its serialization alias. Serialization is NOT a model concern — see ``output.py``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel


class APIModel(BaseModel):
    """Base for all Yandex API models: ignore unknown fields, allow name-or-alias population."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class RawMapping(RootModel[dict[str, Any]]):
    """Wraps an unmodeled API dict so it renders through the Serializer (honoring --format)."""
