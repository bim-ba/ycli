"""Pydantic models for Forms files (form-filling file storage).

Two families live here:

* **Read/out** — :class:`FileOut` (an uploaded/verified file: name, path, size, url, status) and
  the flat :class:`FileList` returned by ``verify``.
* **Write/in** — :class:`FileIn` (the ``{path, url}`` reference ``verify``/``delete`` take). The
  bodyless ``delete`` returns a shared :class:`~ycli.yandex.models.Ack`, not a domain-specific type.
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class FileOut(APIModel):
    """A file stored for form filling (``upload`` result and each ``verify`` item).

    A ``File``-type form field is filled by first uploading the file here; the returned
    ``path`` / ``url`` then reference it in a form response. ``check_status`` reports the
    antivirus/upload scan.

    Example:
        >>> FileOut.model_validate(
        ...     {"name": "cv.pdf", "path": "p", "size": 12, "url": "u", "check_status": "ready"}
        ... ).check_status
        'ready'
    """

    name: str | None = Field(default=None, description="File name.")
    path: str | None = Field(
        default=None, description="File download path (pass to download / verify / delete)."
    )
    size: int | None = Field(default=None, description="File size in bytes.")
    url: str | None = Field(default=None, description="File download URL.")
    check_status: str | None = Field(
        default=None,
        description="Virus/upload scan status — one of: check, ready, infected, error, deleted.",
    )


class FileList(RootModel[list[FileOut]]):
    """Flat list of :class:`FileOut` — the public return of ``FilesClient.verify``.

    Example:
        >>> FileList.model_validate([{"name": "cv.pdf", "check_status": "ready"}]).root[0].name
        'cv.pdf'
    """

    root: list[FileOut] = []


class FileIn(APIModel):
    """A stored-file reference by ``path`` / ``url`` — the ``verify`` / ``delete`` request item.

    Both fields are optional, but at least one must identify the file; ``path`` comes from the
    ``upload`` response.

    Example:
        >>> FileIn(path="p", url="https://…").path
        'p'
    """

    path: str | None = Field(default=None, description="File download path.")
    url: str | None = Field(default=None, description="File download URL.")
