"""Pydantic models for Forms key sets (Keyset + ItemList[Keyset] + typed write bodies).

A *key set* is a batch of single-use keys the API turns into personal form-filling links —
see the Forms "form-filling keys" API. ``keyset_id`` is an **integer** (unlike ``survey_id``,
which is a 24-char hex string).
"""

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


class Keyset(APIModel):
    """A key set for form filling (``/surveys/{id}/keysets`` item and single get).

    Examples:
        >>> Keyset.model_validate({"id": 7, "name": "Q1", "total": 100, "used": 3}).used
        3
    """

    id: int | None = Field(default=None, description="Key set id (integer).")
    name: str | None = Field(default=None, description="Key set name.")
    total: int | None = Field(default=None, description="Number of keys in the set.")
    used: int | None = Field(default=None, description="Number of keys already used.")
    is_enabled: bool | None = Field(default=None, description="Whether the key set is active.")


class KeysetCreate(RequestBody):
    """Typed request body for creating a key set (``POST /surveys/{id}/keysets``).

    Unset (``None``) fields are dropped before the request is sent. The create endpoint,
    however, **requires** ``is_enabled`` (a body without it is rejected), so the CLI marks
    ``--enabled/--disabled`` required and always sends the flag; fields stay optional here so
    :class:`KeysetUpdate` can reuse the shape.

    Examples:
        >>> KeysetCreate(name="Q1 invites", total=250, is_enabled=True).is_enabled
        True
    """

    name: str | None = Field(default=None, description="Key set name.")
    total: int | None = Field(default=None, description="Number of keys to generate in the set.")
    is_enabled: bool | None = Field(
        default=None, description="Create the key set active (usable to build links)."
    )


class KeysetUpdate(KeysetCreate):
    """Typed request body for modifying a key set (``PATCH /surveys/{id}/keysets/{keyset_id}``).

    Same fields as :class:`KeysetCreate`. Although the verb is PATCH, the API validates the body as
    a full record — ``name``, ``total`` and ``is_enabled`` are all required (a missing field is
    rejected with ``400 value_error.missing``), so set every field. ``total`` can only grow: the
    API refuses a number smaller than the set has now (checked live on 2026-10-06).

    Examples:
        >>> KeysetUpdate(name="Q1", total=250, is_enabled=False).is_enabled
        False
    """
