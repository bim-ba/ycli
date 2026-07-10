"""Pydantic models for Tracker issue attachments (Attachment + AttachmentList)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)


class AttachmentMetadata(APIModel):
    """The ``metadata`` sub-object of an attachment — extra file metadata.

    Present for graphic files, where it carries the image's pixel dimensions.

    Example:
        >>> AttachmentMetadata.model_validate({"size": "550x175"}).size
        '550x175'
    """

    size: str | None = Field(
        default=None,
        description="Image dimensions in pixels (``WIDTHxHEIGHT``); graphic files only.",
    )


class Attachment(APIModel):
    """A file attached to a Tracker issue (``/issues/{key}/attachments`` item).

    Example:
        >>> Attachment.model_validate(
        ...     {"id": "123", "name": "picture.jpg", "createdBy": {"display": "Full Name"}}
        ... ).created_by
        'Full Name'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource address of this attachment.",
    )
    id: str | None = Field(default=None, description="Unique file identifier.")
    name: str | None = Field(default=None, description="File name.")
    content: str | None = Field(
        default=None,
        description="Download URL for the file's raw bytes (fetch via ``attachments download``).",
    )
    thumbnail: str | None = Field(
        default=None,
        description="Download URL for the preview thumbnail; graphic files only.",
    )
    created_by: DisplayStr = Field(
        default=None,
        alias="createdBy",
        description="Display name of the user who attached the file.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Upload timestamp (``YYYY-MM-DDThh:mm:ss.sss±hhmm``).",
    )
    mimetype: str | None = Field(
        default=None,
        description="MIME type of the file, e.g. ``image/png`` or ``text/plain``.",
    )
    size: int | None = Field(default=None, description="File size in bytes.")
    metadata: AttachmentMetadata | None = Field(
        default=None,
        description="Extra file metadata (image pixel dimensions for graphic files).",
    )


class AttachmentList(RootModel[list[Attachment]]):
    """A bare JSON array of issue attachments — public return type of ``AttachmentsClient.list``.

    Example:
        >>> AttachmentList.model_validate([{"name": "picture.jpg"}]).root[0].name
        'picture.jpg'
    """
