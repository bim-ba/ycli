"""Pydantic v2 models for Yandex Wiki /pages/{id}/attachments responses (extra='ignore')."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Attachment(APIModel):
    """A page attachment descriptor (``/pages/{id}/attachments`` item).

    Example:
        >>> Attachment.model_validate({"name": "d.png", "size": 100, "mime_type": "image/png"}).name
        'd.png'
    """

    name: str | None = None
    size: int | None = None
    mime_type: str | None = None


class AttachmentsResponse(APIModel):
    """Envelope for ``GET /pages/{id}/attachments`` — ``{results, next_cursor}``.

    Internal per-page parse type used by ``AttachmentsClient._list_page``. ``next_cursor`` is
    ``null`` (not absent / not empty string) once the listing is exhausted; a paginating caller
    feeds the previous response's ``next_cursor`` back as the next request's ``cursor``.

    Example:
        >>> AttachmentsResponse.model_validate({"results": [{"name": "d.png"}]}).results[0].name
        'd.png'
    """

    results: list[Attachment] = Field(default_factory=list)
    next_cursor: str | None = Field(
        default=None,
        description="Cursor for the next page; ``null`` when the listing is exhausted.",
    )


class AttachmentList(RootModel[list[Attachment]]):
    """Flat collection of :class:`Attachment` items.

    Public return type of ``AttachmentsClient.list``.

    Example:
        >>> AttachmentList([Attachment.model_validate({"name": "d.png"})]).root[0].name
        'd.png'
    """

    root: list[Attachment] = Field(default_factory=list)
