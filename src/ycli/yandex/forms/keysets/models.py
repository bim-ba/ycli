"""Pydantic models for Forms key sets (Keyset + KeysetList + typed write bodies).

A *key set* is a batch of single-use keys the API turns into personal form-filling links —
see the Forms "form-filling keys" API. ``keyset_id`` is an **integer** (unlike ``survey_id``,
which is a 24-char hex string).
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Keyset(APIModel):
    """A key set for form filling (``/surveys/{id}/keysets`` item and single get).

    Example:
        >>> Keyset.model_validate({"id": 7, "name": "Q1", "total": 100, "used": 3}).used
        3
    """

    id: int | None = Field(default=None, description="Key set id (integer).")
    name: str | None = Field(default=None, description="Key set name.")
    total: int | None = Field(default=None, description="Number of keys in the set.")
    used: int | None = Field(default=None, description="Number of keys already used.")
    is_enabled: bool | None = Field(default=None, description="Whether the key set is active.")


class KeysetList(RootModel[list[Keyset]]):
    """A bare JSON array of :class:`Keyset` items — the return type of ``KeysetsClient.list``.

    Example:
        >>> KeysetList.model_validate([{"id": 7, "name": "Q1"}]).root[0].id
        7
    """


class KeysetCreate(APIModel):
    """Typed request body for creating a key set (``POST /surveys/{id}/keysets``).

    Unset (``None``) fields are dropped before the request is sent.

    Example:
        >>> KeysetCreate(name="Q1 invites", total=250).total
        250
    """

    name: str | None = Field(default=None, description="Key set name.")
    total: int | None = Field(default=None, description="Number of keys to generate in the set.")
    is_enabled: bool | None = Field(
        default=None, description="Create the key set active (usable to build links)."
    )


class KeysetUpdate(KeysetCreate):
    """Typed request body for modifying a key set (``PATCH /surveys/{id}/keysets/{keyset_id}``).

    Same optional fields as :class:`KeysetCreate`; only the fields you set are sent.

    Example:
        >>> KeysetUpdate(is_enabled=False).is_enabled
        False
    """
