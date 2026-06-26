"""Shared pydantic base for Forms resources — lenient model config.

``_Lenient`` ignores extra fields (the API returns more than we project) and accepts
population by name OR alias.

Example:
    >>> _Lenient.model_validate({"unknown": 1}).model_config["extra"]
    'ignore'
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Lenient(BaseModel):
    """Base model: extra fields silently ignored, population by name OR alias allowed."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
