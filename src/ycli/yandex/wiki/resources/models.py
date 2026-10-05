"""Pydantic v2 models for Yandex Wiki /pages/{id}/resources responses."""

from typing import Any, Literal

from pydantic import Field

from ycli.yandex.models import APIModel

#: What a listing of resources can be sorted by.
ResourceOrder = Literal["name_title", "created_at"] | str


class ResourceItem(APIModel):
    """A page resource — a ``{type, item}`` envelope over an attachment or a grid.

    ``type`` discriminates the payload (``attachment`` → an ``AttachmentSchema``; ``grid`` → a
    ``PageGridsSchema``); ``item`` keeps that payload verbatim so both shapes flow through one
    listing without loss. This is the unified surface over the separate attachments/grids
    listings — use it to enumerate everything on a page in one pass.

    Examples:
        >>> ResourceItem.model_validate({"type": "attachment", "item": {"name": "d.png"}}).type
        'attachment'
    """

    type: str | None = Field(default=None, description="Resource kind: ``attachment`` or ``grid``.")
    item: dict[str, Any] = Field(
        default_factory=dict,
        description="The resource payload (an AttachmentSchema or PageGridsSchema), kept verbatim.",
    )
