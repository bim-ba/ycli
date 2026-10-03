"""Pydantic v2 models for Yandex Wiki /upload_sessions (the binary upload pipeline).

Every write in the pipeline (create / upload-part / finish / abort) returns the same
:class:`UploadSession` snapshot; ``abort_all`` returns the tiny :class:`AbortActiveUploadsResult`.
The lone typed request body is :class:`UploadSessionCreate` (``file_name`` + ``file_size``).
"""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel
from ycli.yandex.wiki.models import User, UserIdentity


class UploadSession(APIModel):
    """A file upload session — create / get / upload-part / finish / abort all return this shape.

    ``session_id`` addresses the session across the whole pipeline; ``status`` walks
    ``not_started`` → ``in_progress`` → ``finished`` (or ``aborted`` / ``used`` / ``cleanup``).
    Once ``finished`` the file can be attached to a page (see ``AttachmentsClient.attach``).

    Examples:
        >>> UploadSession.model_validate({"session_id": "s1", "status": "not_started"}).session_id
        's1'
    """

    session_id: str | None = Field(
        default=None, description="UUID4 identifying the upload session across the pipeline."
    )
    file_name: str | None = Field(default=None, description="Name of the file being uploaded.")
    file_size: int | None = Field(
        default=None, description="Declared total size of the file, in bytes."
    )
    status: str | None = Field(
        default=None,
        description=(
            "Session status — one of not_started, in_progress, finished, aborted, used, cleanup."
        ),
    )
    user: User | None = Field(default=None, description="The user that created the session.")
    created_at: str | None = Field(
        default=None, description="ISO-8601 timestamp when the session was created."
    )
    finished_at: str | None = Field(
        default=None, description="ISO-8601 timestamp when the session finished, if it has."
    )
    storage_type: str | None = Field(
        default=None, description="Backing storage of the upload — one of mds, s3, custom_s3."
    )


class UploadSessionCreate(APIModel):
    """Typed request body for ``uploadsessions.create`` (``POST /upload_sessions``).

    Examples:
        >>> UploadSessionCreate(file_name="diagram.png", file_size=2048).file_size
        2048
    """

    file_name: str = Field(description="Name to give the uploaded file.")
    file_size: int = Field(description="Total size of the file in bytes (sum of every part).")


class AbortActiveUploadsResult(APIModel):
    """Result of ``uploadsessions.abort_all`` (``POST /upload_sessions/abort_active_uploads``).

    Examples:
        >>> AbortActiveUploadsResult.model_validate({"status": "ok"}).status
        'ok'
    """

    status: str = Field(
        default="ok", description="Literal ``ok`` once every active session has been aborted."
    )


UploadSessionUserIdentity = UserIdentity  # deprecated, removed in 0.38


UploadSessionUser = User  # deprecated, removed in 0.39
