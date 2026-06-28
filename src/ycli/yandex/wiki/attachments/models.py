"""Pydantic v2 models for Yandex Wiki /pages/{id}/attachments responses (extra='ignore')."""
from __future__ import annotations

from pydantic import RootModel

from ycli.models import APIModel


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
    """Envelope for ``GET /pages/{id}/attachments`` — ``{results:[Attachment]}``.

    Internal per-page parse type used by ``AttachmentsClient._list_page``.

    Example:
        >>> AttachmentsResponse.model_validate({"results": [{"name": "d.png"}]}).results[0].name
        'd.png'
    """

    results: list[Attachment] = []


class AttachmentList(RootModel[list[Attachment]]):
    """Flat collection of :class:`Attachment` items — the public return type of ``AttachmentsClient.list``.

    Example:
        >>> AttachmentList([Attachment.model_validate({"name": "d.png"})]).root[0].name
        'd.png'
    """

    root: list[Attachment] = []
