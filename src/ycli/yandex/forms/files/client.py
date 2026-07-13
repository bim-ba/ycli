"""Declarative Forms files client (uplink) — transport ONLY.

NOTE: no ``from __future__ import annotations`` — uplink reads annotations eagerly.

Covers the four form-filling file-storage endpoints: a ``multipart/form-data`` **upload**, a
read-via-POST **verify** (status of already-uploaded files), a **binary download** (returns raw
bytes — never ``@uplink.returns.json()``), and a JSON-body **delete**. Upload and download move
raw bytes (binary payloads a JSON MCP tool cannot carry), so they stay CLI/SDK-only; verify and
delete also ship as MCP tools.
"""

import requests
import uplink

from ycli.yandex.forms.base import FormsResource
from ycli.yandex.forms.files.models import FileIn, FileList, FileOut
from ycli.yandex.models import Ack


class FilesClient(FormsResource):
    """Declarative HTTP for the Forms file-storage endpoints (upload/verify/download/delete)."""

    @uplink.returns.json()
    @uplink.multipart
    @uplink.post("surveys/{survey_id}/files")
    def _upload(
        self,
        survey_id: uplink.Path,
        file_data: uplink.Part("file"),  # ty: ignore[invalid-type-form]
    ) -> FileOut:  # ty: ignore[empty-body]
        """``POST …/files`` (multipart; internal — callers use :meth:`upload`)."""

    def upload(self, survey_id: str, *, filename: str, data: bytes) -> FileOut:
        """Upload a file for form filling (multipart field ``file``) → :class:`FileOut`.

        Requires external file storage to be connected in the form's settings; the returned
        ``path`` / ``url`` then reference the file in a ``File``-type answer. ``data`` are the raw
        file bytes; ``filename`` is recorded as the multipart part filename.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.files.upload(
            ...     "686d0a1b2c3d4e5f00000001", filename="cv.pdf", data=b"%PDF…"
            ... ).path  # doctest: +SKIP
            'a/b/cv.pdf'
        """
        return self._upload(survey_id, file_data=(filename, data))

    @uplink.returns.json()
    @uplink.json
    @uplink.post("surveys/{survey_id}/files/verify")
    def _verify(self, survey_id: uplink.Path, body: uplink.Body) -> FileList:  # ty: ignore[empty-body]
        """``POST …/files/verify`` from a ready list; internal — callers use :meth:`verify`."""

    def verify(self, survey_id: str, files: list[FileIn]) -> FileList:
        """``POST …/files/verify`` (a read via POST) → per-file :class:`FileList` statuses.

        Checks the upload status and download access of already-uploaded files; ``files`` is the
        list of ``{path, url}`` references to check. This is read-only (no mutation).

        Example:
            >>> from ycli.yandex.forms.files.models import FileIn
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.files.verify("686d0a1b2c3d4e5f00000001", [FileIn(path="a/b/cv.pdf")]).root[
            ...     0
            ... ].check_status  # doctest: +SKIP
            'ready'
        """
        return self._verify(survey_id, [f.model_dump(exclude_none=True) for f in files])

    @uplink.get("files")
    def _download(
        self,
        path: uplink.Query,
        download: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        file_hash: uplink.Query("hash") = None,  # ty: ignore[invalid-type-form]
    ) -> requests.Response:  # ty: ignore[empty-body]
        """GET the raw file bytes (internal; callers use :meth:`download`)."""

    def download(self, path: str, *, download: bool = False, file_hash: str | None = None) -> bytes:
        """Download a stored file's raw bytes (``GET /files?path=…``); raises on non-2xx.

        ``download=True`` asks the API to add a ``Content-Disposition`` filename header;
        ``file_hash`` (the ``hash`` from an upload response) lets an anonymous caller download a
        file whose access cannot otherwise be verified. Binary output is CLI/SDK-only — never an
        MCP payload; in the CLI this feeds ``ycli.cli.binary.write_output``.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.files.download("a/b/cv.pdf")[:4]  # doctest: +SKIP
            b'%PDF'
        """
        return self._download(
            path=path,
            download="true" if download else None,
            file_hash=file_hash or None,
        ).content

    @uplink.json
    @uplink.delete("files")
    def _delete(self, body: uplink.Body) -> requests.Response:  # ty: ignore[empty-body]
        """Raw ``DELETE /files`` from a ready body; internal — callers use :meth:`delete`."""

    def delete(self, *, path: str | None = None, url: str | None = None) -> Ack:
        """``DELETE /files`` (body ``{path, url}``) → an :class:`Ack`.

        Deletes an attached file, identified by ``path`` and/or ``url``. The API answers
        ``200 OK`` with no useful body, so the result is synthesized; a non-2xx status raises a
        typed ``YandexError`` before this returns. ``detail`` names whichever of ``path`` / ``url``
        were passed, so no identifying information the caller gave is lost.

        Example:
            >>> client = FormsClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.files.delete(path="a/b/cv.pdf").ok  # doctest: +SKIP
            True
        """
        self._delete(FileIn(path=path, url=url).model_dump(exclude_none=True))
        fields = (("path", path), ("url", url))
        ident = " ".join(f"{name}={value}" for name, value in fields if value)
        return Ack.deleted("file", ident)
