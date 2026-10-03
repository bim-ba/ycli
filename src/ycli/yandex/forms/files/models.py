"""Pydantic models for Forms files (form-filling file storage).

Two families live here:

* **Read/out** — :class:`FileOut` (an uploaded/verified file: name, path, size, url, status) and
  the flat ``ItemList[FileOut]`` returned by ``verify``.
* **Write/in** — :class:`FileIn` (the ``{path, url}`` reference ``verify``/``delete`` take). The
  bodyless ``delete`` returns a shared :class:`~ycli.yandex.models.Ack`, not a domain-specific type.
"""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import RequestBody


class FileIn(RequestBody):
    """A stored-file reference by ``path`` / ``url`` — the ``verify`` / ``delete`` request item.

    Both fields are optional, but at least one must identify the file; ``path`` comes from the
    ``upload`` response.

    Examples:
        >>> FileIn(path="p", url="https://…").path
        'p'
    """

    path: str | None = Field(default=None, description="File download path.")
    url: str | None = Field(default=None, description="File download URL.")
