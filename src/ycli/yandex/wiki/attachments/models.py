"""Pydantic v2 models for Yandex Wiki /pages/{id}/attachments responses (extra='ignore')."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Attachment(APIModel):
    """A page attachment descriptor (``/pages/{id}/attachments`` item).

    The list payload reports ``size`` as a human-readable string (e.g. ``"0.00"``) and names the
    MIME type ``mimetype`` — matching the sibling :class:`AttachedFile` and the ``resources``
    listing.

    Example:
        >>> Attachment.model_validate(
        ...     {"name": "d.png", "size": "0.00", "mimetype": "image/png"}
        ... ).mimetype
        'image/png'
    """

    name: str | None = None
    size: str | None = None
    mimetype: str | None = None


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


class AttachmentCreate(APIModel):
    """Typed request body for ``attachments.attach`` (``POST /pages/{id}/attachments``).

    Attaches file(s) already uploaded via the upload-session pipeline; each entry is a
    finished session's ``session_id``.

    Example:
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

    Example:
        >>> AttachedFile.model_validate({"id": 7, "name": "d.png"}).id
        7
    """

    id: int | None = Field(default=None, description="Numeric id of the new attachment.")
    name: str | None = Field(default=None, description="File name of the attachment.")
    download_url: str | None = Field(
        default=None, description="URL from which the attachment's bytes can be downloaded."
    )
    size: str | None = Field(default=None, description="Human-readable size of the attachment.")
    description: str | None = Field(default=None, description="Optional description of the file.")
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
    :class:`AttachedFileList`.

    Example:
        >>> AttachResponse.model_validate({"results": [{"id": 7}]}).results[0].id
        7
    """

    results: list[AttachedFile] = Field(default_factory=list)


class AttachedFileList(RootModel[list[AttachedFile]]):
    """Flat collection of :class:`AttachedFile` items — public return of ``attach`` / ``upload``.

    Example:
        >>> AttachedFileList([AttachedFile.model_validate({"id": 7})]).root[0].id
        7
    """

    root: list[AttachedFile] = Field(default_factory=list)
