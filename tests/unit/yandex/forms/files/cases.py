"""Contract cases for Forms file storage (see tests/contract/)."""

from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.forms.files.models import FileIn

SID = "686d0a1b2c3d4e5f00000040"
UPLOAD = Path(__file__).with_name("cv.txt")
FILE = {"path": "a/b/cv.txt", "url": "https://forms.test/a/b/cv.txt", "check_status": "ready"}

CASES = [
    Case(
        "forms.files.upload",
        args=(SID,),
        kwargs={"filename": "cv.txt", "data": b"resume bytes"},
        cli=["forms", "files", "upload", SID, str(UPLOAD)],
        mcp=None,
        exchanges=[
            (
                Sent("POST", f"surveys/{SID}/files", files={"file": ("cv.txt", b"resume bytes")}),
                Reply(json=FILE, status=201),
            )
        ],
    ),
    Case(
        "forms.files.verify",
        args=(
            SID,
            [
                FileIn(path="a/b/cv.txt", url="https://forms.test/a/b/cv.txt"),
                FileIn(path="c/d.pdf", url="https://forms.test/c/d.pdf"),
            ],
        ),
        cli=[
            "forms",
            "files",
            "verify",
            SID,
            "--path",
            "a/b/cv.txt",
            "--url",
            "https://forms.test/a/b/cv.txt",
            "--path",
            "c/d.pdf",
            "--url",
            "https://forms.test/c/d.pdf",
        ],
        mcp=(
            "forms_files_verify",
            {
                "survey_id": SID,
                "files": [
                    {"path": "a/b/cv.txt", "url": "https://forms.test/a/b/cv.txt"},
                    {"path": "c/d.pdf", "url": "https://forms.test/c/d.pdf"},
                ],
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"surveys/{SID}/files/verify",
                    json=[
                        {"path": "a/b/cv.txt", "url": "https://forms.test/a/b/cv.txt"},
                        {"path": "c/d.pdf", "url": "https://forms.test/c/d.pdf"},
                    ],
                ),
                Reply(json=[FILE]),
            )
        ],
        effect=Effect.READ,
    ),
    Case(
        "forms.files.download",
        args=("a/b/cv.txt",),
        kwargs={"download": True, "file_hash": "h4sh"},
        cli=["forms", "files", "download", "--path", "a/b/cv.txt", "--download", "--hash", "h4sh"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "files", {"path": "a/b/cv.txt", "download": "true", "hash": "h4sh"}),
                Reply(content=b"resume bytes"),
            )
        ],
    ),
    Case(
        "forms.files.delete",
        kwargs={"path": "a/b/cv.txt", "url": "https://forms.test/a/b/cv.txt"},
        cli=[
            "forms",
            "files",
            "delete",
            "--path",
            "a/b/cv.txt",
            "--url",
            "https://forms.test/a/b/cv.txt",
        ],
        mcp=("forms_files_delete", {"path": "a/b/cv.txt", "url": "https://forms.test/a/b/cv.txt"}),
        exchanges=[
            (
                Sent(
                    "DELETE",
                    "files",
                    json={"path": "a/b/cv.txt", "url": "https://forms.test/a/b/cv.txt"},
                ),
                Reply(),
            )
        ],
        output={
            "ok": True,
            "detail": "deleted file path=a/b/cv.txt url=https://forms.test/a/b/cv.txt",
        },
    ),
]
