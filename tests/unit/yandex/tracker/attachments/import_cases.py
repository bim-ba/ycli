"""Contract cases for the import of Tracker attachments (see tests/contract/)."""

from pathlib import Path

from tests.contract import Case, Reply, Sent

UPLOAD = Path(__file__).with_name("pic.png")

IMPORT_CASES = [
    Case(
        "tracker.attachments.import_",
        args=("JUNE-5",),
        kwargs={
            "filename": "renamed.png",
            "created_at": "2022-05-06T07:08:09.000+0000",
            "created_by": "16",
            "data": b"PNGDATA",
        },
        cli=[
            "tracker",
            "attachments",
            "import",
            "JUNE-5",
            str(UPLOAD),
            "--created-at",
            "2022-05-06T07:08:09.000+0000",
            "--created-by",
            "16",
            "--filename",
            "renamed.png",
        ],
        mcp=(
            "tracker_attachments_import",
            {
                "issue_key": "JUNE-5",
                "filename": "renamed.png",
                "created_at": "2022-05-06T07:08:09.000+0000",
                "created_by": "16",
                "data": "UE5HREFUQQ==",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-5/attachments/_import",
                    {
                        "filename": "renamed.png",
                        "createdAt": "2022-05-06T07:08:09.000+0000",
                        "createdBy": "16",
                    },
                    files={"file_data": ("file_data", b"PNGDATA")},
                ),
                Reply(json={"id": "123", "name": "renamed.png"}, status=201),
            )
        ],
    ),
    # Without --filename the CLI names the attachment after the local file.
    Case(
        "tracker.attachments.import_",
        args=("JUNE-6",),
        kwargs={
            "filename": "pic.png",
            "created_at": "2023-06-07T08:09:10.000+0000",
            "created_by": "17",
            "data": b"PNGDATA",
        },
        cli=[
            "tracker",
            "attachments",
            "import",
            "JUNE-6",
            str(UPLOAD),
            "--created-at",
            "2023-06-07T08:09:10.000+0000",
            "--created-by",
            "17",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-6/attachments/_import",
                    {
                        "filename": "pic.png",
                        "createdAt": "2023-06-07T08:09:10.000+0000",
                        "createdBy": "17",
                    },
                    files={"file_data": ("file_data", b"PNGDATA")},
                ),
                Reply(json={"id": "124", "name": "pic.png"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.attachments.import_for_comment",
        args=("JUNE-7", "2238"),
        kwargs={
            "filename": "scan.png",
            "created_at": "2024-07-08T09:10:11.000+0000",
            "created_by": "18",
            "data": b"PNGDATA",
        },
        cli=[
            "tracker",
            "attachments",
            "import-for-comment",
            "JUNE-7",
            "2238",
            str(UPLOAD),
            "--created-at",
            "2024-07-08T09:10:11.000+0000",
            "--created-by",
            "18",
            "--filename",
            "scan.png",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-7/comments/2238/attachments/_import",
                    {
                        "filename": "scan.png",
                        "createdAt": "2024-07-08T09:10:11.000+0000",
                        "createdBy": "18",
                    },
                    files={"file_data": ("file_data", b"PNGDATA")},
                ),
                Reply(json={"id": "125", "name": "scan.png"}),
            )
        ],
    ),
    # Without --filename the CLI names the attachment after the local file.
    Case(
        "tracker.attachments.import_for_comment",
        args=("JUNE-8", "2239"),
        kwargs={
            "filename": "pic.png",
            "created_at": "2025-08-09T10:11:12.000+0000",
            "created_by": "19",
            "data": b"PNGDATA",
        },
        cli=[
            "tracker",
            "attachments",
            "import-for-comment",
            "JUNE-8",
            "2239",
            str(UPLOAD),
            "--created-at",
            "2025-08-09T10:11:12.000+0000",
            "--created-by",
            "19",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/JUNE-8/comments/2239/attachments/_import",
                    {
                        "filename": "pic.png",
                        "createdAt": "2025-08-09T10:11:12.000+0000",
                        "createdBy": "19",
                    },
                    files={"file_data": ("file_data", b"PNGDATA")},
                ),
                Reply(json={"id": "126", "name": "pic.png"}),
            )
        ],
    ),
]
