"""Forms file-storage client on the httpx2 core: upload, verify, download and delete.

Upload and download move raw bytes, which a JSON MCP result cannot carry, so they stay SDK
and CLI only; verify and delete also ship as MCP tools.
"""

from __future__ import annotations

from ycli.yandex.core.resource import Resource
from ycli.yandex.forms.files import endpoints
from ycli.yandex.forms.files.models import FileIn, FileList, FileOut
from ycli.yandex.models import Ack


class FilesClient(Resource):
    """The files attached while filling a form."""

    def upload(self, survey_id: str, *, filename: str, data: bytes) -> FileOut:
        """Upload a file for form filling (multipart field ``file``) → :class:`FileOut`.

        Needs external file storage connected in the form's settings; the returned ``path`` /
        ``url`` then reference the file in a ``File``-type answer.

        Args:
            survey_id: The form's id.
            filename: The file's name.
            data: The file's raw bytes.

        Returns:
            The stored file, with its ``path`` and ``url``.

        Examples:
            >>> forms.files.upload(
            ...     "686d0a1b2c3d4e5f00000040", filename="cv.txt", data=b"resume bytes"
            ... ).path
            'a/b/cv.txt'
        """
        return self._session.send(endpoints.upload_file(survey_id, filename=filename, data=data))

    def verify(self, survey_id: str, files: list[FileIn]) -> FileList:
        """``POST …/files/verify`` (a read) → the upload status and access of each file.

        Args:
            survey_id: The form's id.
            files: The files to check, each by ``path`` and/or ``url``.

        Returns:
            The upload status and access of each file.

        Examples:
            >>> forms.files.verify(
            ...     "686d0a1b2c3d4e5f00000040",
            ...     [
            ...         FileIn(path="a/b/cv.txt", url="https://forms.test/a/b/cv.txt"),
            ...         FileIn(path="c/d.pdf"),
            ...     ],
            ... ).root[0].check_status
            'ready'
        """
        body = [file.model_dump(exclude_none=True) for file in files]
        return self._session.send(endpoints.verify_files(survey_id, body))

    def download(self, path: str, *, download: bool = False, file_hash: str | None = None) -> bytes:
        """``GET /files?path=…`` → a stored file's raw bytes.

        ``download=True`` asks for a ``Content-Disposition`` filename header; ``file_hash`` (the
        ``hash`` from an upload) lets an anonymous caller download a file whose access cannot
        otherwise be verified.

        Args:
            path: The stored file's path.
            download: Whether to ask for a ``Content-Disposition`` filename header.
            file_hash: The ``hash`` from an upload, for an anonymous caller.

        Returns:
            The file's raw bytes.

        Examples:
            >>> forms.files.download("a/b/cv.txt", download=True, file_hash="h4sh")
            b'resume bytes'
        """
        endpoint = endpoints.download_file(path, download=download, file_hash=file_hash or None)
        return self._session.send(endpoint)

    def delete(self, *, path: str | None = None, url: str | None = None) -> Ack:
        """``DELETE /files`` (body ``{path, url}``) → an :class:`Ack` naming what was given.

        Args:
            path: The stored file's path.
            url: The stored file's url.

        Returns:
            An acknowledgement naming the deleted file.

        Examples:
            >>> forms.files.delete(path="a/b/cv.txt", url="https://forms.test/a/b/cv.txt").ok
            True
        """
        self._session.send(
            endpoints.delete_file(FileIn(path=path, url=url).model_dump(exclude_none=True))
        )
        named = " ".join(
            f"{name}={value}" for name, value in (("path", path), ("url", url)) if value
        )
        return Ack.deleted("file", named)
