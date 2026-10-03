"""Contract cases for Tracker issue ``/attachments`` (see tests/contract.py)."""

from pathlib import Path

from tests.contract import Case, Reply, Sent

UPLOAD = Path(__file__).with_name("upload.txt")
TEMP_UPLOAD = Path(__file__).with_name("temp-upload.txt")
ATTACHMENT = {
    "self": "https://api.tracker.yandex.net/v3/issues/JUNE-5/attachments/4161",
    "id": "4161",
    "name": "upload.txt",
    "content": "https://api.tracker.yandex.net/v3/issues/JUNE-5/attachments/4161/upload.txt",
    "createdBy": {
        "self": "https://api.tracker.yandex.net/v3/users/11",
        "id": "11",
        "display": "Ann",
    },
    "createdAt": "2017-06-11T05:11:12.347+0000",
    "mimetype": "text/plain",
    "size": 16,
}

CASES = [
    Case(
        "tracker.attachments.list",
        args=("JUNE-2",),
        cli=["tracker", "attachments", "list", "JUNE-2"],
        mcp=("tracker_attachments_list", {"issue_key": "JUNE-2"}),
        exchanges=[
            (
                Sent("GET", "issues/JUNE-2/attachments"),
                Reply(json=[{"id": "123", "name": "picture.jpg", "size": 19090}]),
            )
        ],
    ),
    Case(
        "tracker.attachments.download",
        args=("JUNE-3", "4159", "report.pdf"),
        cli=["tracker", "attachments", "download", "JUNE-3", "4159", "report.pdf"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", "issues/JUNE-3/attachments/4159/report.pdf"),
                Reply(content=b"%PDF-attachment"),
            )
        ],
    ),
    Case(
        "tracker.attachments.download_thumbnail",
        args=("JUNE-4", "4160"),
        cli=["tracker", "attachments", "download-thumbnail", "JUNE-4", "4160"],
        mcp=None,
        exchanges=[
            (Sent("GET", "issues/JUNE-4/thumbnails/4160"), Reply(content=b"\x89PNGthumb")),
        ],
    ),
    Case(
        "tracker.attachments.get",
        args=("JUNE-5", "4161"),
        cli=["tracker", "attachments", "get", "JUNE-5", "4161"],
        mcp=("tracker_attachments_get", {"issue_key": "JUNE-5", "file_id": "4161"}),
        exchanges=[(Sent("GET", "issues/JUNE-5/attachments/4161"), Reply(json=ATTACHMENT))],
    ),
    Case(
        "tracker.attachments.delete",
        args=("JUNE-6", "4162"),
        cli=["tracker", "attachments", "delete", "JUNE-6", "4162"],
        mcp=("tracker_attachments_delete", {"issue_key": "JUNE-6", "file_id": "4162"}),
        exchanges=[(Sent("DELETE", "issues/JUNE-6/attachments/4162"), Reply(status=204))],
    ),
    Case(
        "tracker.attachments.upload",
        args=("JUNE-7",),
        kwargs={"filename": "upload.txt", "data": b"attachment bytes", "rename_to": "kept.txt"},
        cli=[
            "tracker",
            "attachments",
            "upload",
            "JUNE-7",
            str(UPLOAD),
            "--rename-to",
            "kept.txt",
        ],
        mcp=(
            "tracker_attachments_upload",
            {
                "issue_key": "JUNE-7",
                "file_name": "upload.txt",
                "data": "YXR0YWNobWVudCBieXRlcw==",
                "rename_to": "kept.txt",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-7/attachments",
                    {"filename": "kept.txt"},
                    files={"file": ("upload.txt", b"attachment bytes")},
                ),
                Reply(json=ATTACHMENT, status=201),
            )
        ],
    ),
    # Without --rename-to the file keeps its own name and no query is sent.
    Case(
        "tracker.attachments.upload",
        args=("JUNE-8",),
        kwargs={"filename": "upload.txt", "data": b"attachment bytes"},
        cli=["tracker", "attachments", "upload", "JUNE-8", str(UPLOAD)],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-8/attachments",
                    files={"file": ("upload.txt", b"attachment bytes")},
                ),
                Reply(json=ATTACHMENT, status=201),
            )
        ],
    ),
    Case(
        "tracker.attachments.upload_temp",
        kwargs={
            "filename": "temp-upload.txt",
            "data": b"temporary bytes",
            "rename_to": "scratch.txt",
        },
        cli=[
            "tracker",
            "attachments",
            "upload-temp",
            str(TEMP_UPLOAD),
            "--rename-to",
            "scratch.txt",
        ],
        mcp=(
            "tracker_attachments_upload_temp",
            {
                "file_name": "temp-upload.txt",
                "data": "dGVtcG9yYXJ5IGJ5dGVz",
                "rename_to": "scratch.txt",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "attachments",
                    {"filename": "scratch.txt"},
                    files={"file": ("temp-upload.txt", b"temporary bytes")},
                ),
                Reply(json={**ATTACHMENT, "id": "4170"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.attachments.upload_temp",
        kwargs={"filename": "temp-upload.txt", "data": b"temporary bytes"},
        cli=["tracker", "attachments", "upload-temp", str(TEMP_UPLOAD)],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST", "attachments", files={"file": ("temp-upload.txt", b"temporary bytes")}
                ),
                Reply(json={**ATTACHMENT, "id": "4171"}, status=201),
            )
        ],
    ),
]
