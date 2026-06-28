"""Pydantic v2 models for Yandex Wiki /pages/{id}/attachments responses (extra='ignore')."""
from __future__ import annotations

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

    Example:
        >>> AttachmentsResponse.model_validate({"results": [{"name": "d.png"}]}).results[0].name
        'd.png'
    """

    results: list[Attachment] = []
