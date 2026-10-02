"""Forms file-storage operations, declared once (sans-IO).

Example:
    >>> verify_files("686d", [{"path": "a/b.pdf"}]).effect
    'read'
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.files.models import FileList, FileOut


def upload_file(survey_id: str, *, filename: str, data: bytes) -> Endpoint[FileOut]:
    path = f"surveys/{segment(survey_id)}/files"
    return Endpoint("POST", path, FileOut, files={"file": (filename, data)})


def verify_files(survey_id: str, body: list[dict[str, Any]]) -> Endpoint[FileList]:
    """``POST …/files/verify`` only reads the status of files already uploaded."""
    path = f"surveys/{segment(survey_id)}/files/verify"
    return Endpoint("POST", path, FileList, json=body, effect="read")


def download_file(path: str, *, download: bool, file_hash: str | None) -> Endpoint[bytes]:
    params = {"path": path, "download": "true" if download else None, "hash": file_hash}
    return Endpoint("GET", "files", bytes, params=params)


def delete_file(body: dict[str, Any]) -> Endpoint[None]:
    return Endpoint("DELETE", "files", json=body)
