"""Pydantic models for Tracker issue attachments (Attachment + ItemList[Attachment])."""

from pydantic import Field

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    DisplayStr,
)
from ycli.yandex.tracker.models import AttachmentMetadata


class Attachment(APIModel):
    """A file attached to a Tracker issue (``/issues/{key}/attachments`` item).

    Examples:
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
