"""Pydantic v2 models for Yandex Wiki /pages/{id}/attachments responses."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.wiki.models import User

#: What a listing of attachments can be sorted by.
AttachmentOrder = Literal["name", "size", "created_at"] | str


class Attachment(APIModel):
    """A page attachment descriptor (``/pages/{id}/attachments`` item).

    The list payload reports ``size`` as a human-readable string (e.g. ``"0.00"``) and names the
    MIME type ``mimetype`` — matching the sibling :class:`AttachedFile` and the ``resources``
    listing.

    Examples:
        >>> Attachment.model_validate(
        ...     {"id": 7, "name": "d.png", "size": "0.00", "mimetype": "image/png"}
        ... ).id
        7
    """

    id: int | None = Field(
        default=None, description="Numeric id of the attachment (the ``file_id`` other calls take)."
    )
    name: str | None = Field(default=None, description="File name of the attachment.")
    size: str | None = Field(default=None, description="Human-readable size, e.g. `0.00`.")
    mimetype: str | None = Field(default=None, description="MIME type of the attachment.")


class AttachmentCreate(RequestBody):
    """Typed request body for ``attachments.attach`` (``POST /pages/{id}/attachments``).

    Attaches file(s) already uploaded via the upload-session pipeline; each entry is a
    finished session's ``session_id``.

    Examples:
        >>> AttachmentCreate(upload_sessions=["1e5c…"]).upload_sessions
        ['1e5c…']
    """

    upload_sessions: list[str] = Field(
        description="UUID4 ids of finished upload sessions whose files to attach to the page.",
    )


class AttachedFile(APIModel):
    """A file just attached to a page (``results[]`` item of ``POST /pages/{id}/attachments``).

    Richer than the list-surface :class:`Attachment`: carries the new ``id``, ``download_url``
    and virus-``check_status`` the attach response returns.

    Examples:
        >>> AttachedFile.model_validate({"id": 7, "name": "d.png"}).id
        7
    """

    id: int | None = Field(default=None, description="Numeric id of the new attachment.")
    name: str | None = Field(default=None, description="File name of the attachment.")
    is_downloadable: bool | None = Field(
        default=None, description="Whether the file's bytes can be downloaded."
    )
    download_url: str | None = Field(
        default=None, description="URL from which the attachment's bytes can be downloaded."
    )
    size: str | None = Field(default=None, description="Human-readable size of the attachment.")
    description: str | None = Field(default=None, description="Optional description of the file.")
    user: User | None = Field(default=None, description="Who attached the file.")
    mimetype: str | None = Field(default=None, description="MIME type of the attachment.")
    has_preview: bool | None = Field(
        default=None, description="Whether the attachment has a rendered preview."
    )
    check_status: str | None = Field(
        default=None,
        description="Virus-scan status — one of check, ready, deleted, infected, error.",
    )
    created_at: str | None = Field(
        default=None, description="ISO-8601 timestamp when the file was attached."
    )


class AttachResponse(APIModel):
    """Envelope for ``POST /pages/{id}/attachments`` — ``{results: [AttachedFile, …]}``.

    Internal parse type used by ``AttachmentsClient._attach``; callers get the flat
    ``ItemList[AttachedFile]``.

    Examples:
        >>> AttachResponse.model_validate({"results": [{"id": 7}]}).results[0].id
        7
    """

    results: list[AttachedFile] = Field(
        default_factory=list, description="The files that were attached."
    )
