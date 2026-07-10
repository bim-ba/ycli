"""Pydantic v2 models for Yandex Wiki /pages/{id}/resources responses (extra='ignore')."""

from __future__ import annotations

from typing import Any

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class ResourceItem(APIModel):
    """A page resource — a ``{type, item}`` envelope over an attachment or a grid.

    ``type`` discriminates the payload (``attachment`` → an ``AttachmentSchema``; ``grid`` → a
    ``PageGridsSchema``); ``item`` keeps that payload verbatim so both shapes flow through one
    listing without loss. This is the unified surface over the separate attachments/grids
    listings — use it to enumerate everything on a page in one pass.

    Example:
        >>> ResourceItem.model_validate({"type": "attachment", "item": {"name": "d.png"}}).type
        'attachment'
    """

    type: str | None = Field(default=None, description="Resource kind: ``attachment`` or ``grid``.")
    item: dict[str, Any] = Field(
        default_factory=dict,
        description="The resource payload (an AttachmentSchema or PageGridsSchema), kept verbatim.",
    )


class ResourcesResponse(APIModel):
    """Envelope for ``GET /pages/{id}/resources`` — ``{results, next_cursor}``.

    Internal per-page parse type used by ``ResourcesClient._list_page``. ``next_cursor`` is
    ``null`` (not absent / not empty string) once the listing is exhausted; a paginating caller
    feeds the previous response's ``next_cursor`` back as the next request's ``cursor``.

    Example:
        >>> r = ResourcesResponse.model_validate({"results": [{"type": "grid", "item": {}}]})
        >>> r.results[0].type
        'grid'
    """

    results: list[ResourceItem] = Field(
        default_factory=list, description="Resource envelopes on this page of the listing."
    )
    next_cursor: str | None = Field(
        default=None,
        description="Cursor for the next page; ``null`` when the listing is exhausted.",
    )


class ResourceItemList(RootModel[list[ResourceItem]]):
    """A drained, flat list of page resources (no cursor — pagination is internal).

    Public return type of ``ResourcesClient.list``.

    Example:
        >>> ResourceItemList([ResourceItem(type="grid", item={})]).root[0].type
        'grid'
    """

    root: list[ResourceItem] = Field(default_factory=list)
