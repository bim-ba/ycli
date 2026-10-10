"""Pydantic v2 models for Yandex Wiki /pages/{id}/attachments responses."""

from typing import Annotated, Literal

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.sync.marks import Identity
from ycli.yandex.wiki.models import User

#: What a listing of attachments can be sorted by.
AttachmentOrder = Literal["name", "size", "created_at"] | str


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
    """A file attached to a page: an item of the listing, and what attaching one returns.

    Examples:
        >>> AttachedFile.model_validate({"id": 7, "name": "d.png"}).id
        7
    """

    id: Annotated[int | None, Identity()] = Field(
        default=None, description="Numeric id of the new attachment."
    )
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
        default=None,
        description="Whether the attachment has a rendered preview. The reply to an upload "
        "says false for an image: its preview is made a moment later, so read this from a get "
        "or a list (measured).",
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
