"""Contract cases for Tracker ``/_import`` (see tests/contract.py)."""

from pathlib import Path

from tests.contract import Case, Reply, Sent

UPLOAD = Path(__file__).with_name("pic.png")

CASES = [
    Case(
        "tracker.import_.task",
        args=(
            {
                "queue": "TEST",
                "summary": "Old task",
                "createdAt": "2017-08-29T12:34:41.740+0000",
                "createdBy": "11",
                "key": "TEST-41",
                "description": "Imported from Jira",
                "assignee": "bob",
            },
        ),
        cli=[
            "tracker",
            "import",
            "task",
            "--queue",
            "TEST",
            "--summary",
            "Old task",
            "--created-at",
            "2017-08-29T12:34:41.740+0000",
            "--created-by",
            "11",
            "--key",
            "TEST-41",
            "--description",
            "Imported from Jira",
            "--assignee",
            "bob",
        ],
        mcp=(
            "tracker_import_task",
            {
                "body": {
                    "queue": "TEST",
                    "summary": "Old task",
                    "createdAt": "2017-08-29T12:34:41.740+0000",
                    "createdBy": "11",
                    "key": "TEST-41",
                    "description": "Imported from Jira",
                    "assignee": "bob",
                }
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/_import",
                    json={
                        "queue": "TEST",
                        "summary": "Old task",
                        "createdAt": "2017-08-29T12:34:41.740+0000",
                        "createdBy": "11",
                        "key": "TEST-41",
                        "description": "Imported from Jira",
                        "assignee": "bob",
                    },
                ),
                Reply(json={"key": "TEST-41"}, status=201),
            )
        ],
    ),
    # Only the required options: the CLI leaves key/description/assignee out.
    Case(
        "tracker.import_.task",
        args=(
            {
                "queue": "OPS",
                "summary": "Bare import",
                "createdAt": "2018-01-02T03:04:05.000+0000",
                "createdBy": "12",
            },
        ),
        cli=[
            "tracker",
            "import",
            "task",
            "--queue",
            "OPS",
            "--summary",
            "Bare import",
            "--created-at",
            "2018-01-02T03:04:05.000+0000",
            "--created-by",
            "12",
        ],
        mcp=None,
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/_import",
                    json={
                        "queue": "OPS",
                        "summary": "Bare import",
                        "createdAt": "2018-01-02T03:04:05.000+0000",
                        "createdBy": "12",
                    },
                ),
                Reply(json={"key": "OPS-1"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.import_.comment",
        args=(
            "TEST-2",
            {"text": "Old comment", "createdAt": "2019-02-03T04:05:06.000+0000", "createdBy": "13"},
        ),
        cli=[
            "tracker",
            "import",
            "comment",
            "TEST-2",
            "--text",
            "Old comment",
            "--created-at",
            "2019-02-03T04:05:06.000+0000",
            "--created-by",
            "13",
        ],
        mcp=(
            "tracker_import_comment",
            {
                "issue_key": "TEST-2",
                "body": {
                    "text": "Old comment",
                    "createdAt": "2019-02-03T04:05:06.000+0000",
                    "createdBy": "13",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/TEST-2/comments/_import",
                    json={
                        "text": "Old comment",
                        "createdAt": "2019-02-03T04:05:06.000+0000",
                        "createdBy": "13",
                    },
                ),
                Reply(json={"id": 3, "text": "Old comment"}, status=201),
            )
        ],
    ),
    Case(
        "tracker.import_.link",
        args=(
            "TEST-3",
            {
                "relationship": "depends on",
                "issue": "TEST-4",
                "createdAt": "2020-03-04T05:06:07.000+0000",
                "createdBy": "14",
            },
        ),
        cli=[
            "tracker",
            "import",
            "link",
            "TEST-3",
            "--relationship",
            "depends on",
            "--issue",
            "TEST-4",
            "--created-at",
            "2020-03-04T05:06:07.000+0000",
            "--created-by",
            "14",
        ],
        mcp=(
            "tracker_import_link",
            {
                "issue_key": "TEST-3",
                "body": {
                    "relationship": "depends on",
                    "issue": "TEST-4",
                    "createdAt": "2020-03-04T05:06:07.000+0000",
                    "createdBy": "14",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/TEST-3/links/_import",
                    json={
                        "relationship": "depends on",
                        "issue": "TEST-4",
                        "createdAt": "2020-03-04T05:06:07.000+0000",
                        "createdBy": "14",
                    },
                ),
                Reply(json={"id": 51, "object": {"key": "TEST-4"}}, status=201),
            )
        ],
    ),
    # The worklog import answers with a JSON array of the created records.
    Case(
        "tracker.import_.worklog",
        args=(
            "TEST-5",
            {
                "duration": "PT2H",
                "createdAt": "2021-04-05T06:07:08.000+0000",
                "createdBy": "15",
                "start": "2021-04-05T09:00:00.000+0000",
                "comment": "Backfilled",
            },
        ),
        cli=[
            "tracker",
            "import",
            "worklog",
            "TEST-5",
            "--duration",
            "PT2H",
            "--created-at",
            "2021-04-05T06:07:08.000+0000",
            "--created-by",
            "15",
            "--start",
            "2021-04-05T09:00:00.000+0000",
            "--comment",
            "Backfilled",
        ],
        mcp=(
            "tracker_import_worklog",
            {
                "issue_key": "TEST-5",
                "body": {
                    "duration": "PT2H",
                    "createdAt": "2021-04-05T06:07:08.000+0000",
                    "createdBy": "15",
                    "start": "2021-04-05T09:00:00.000+0000",
                    "comment": "Backfilled",
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/TEST-5/worklogs/_import",
                    json={
                        "duration": "PT2H",
                        "createdAt": "2021-04-05T06:07:08.000+0000",
                        "createdBy": "15",
                        "start": "2021-04-05T09:00:00.000+0000",
                        "comment": "Backfilled",
                    },
                ),
                Reply(json=[{"id": 37, "duration": "PT2H"}], status=201),
            )
        ],
    ),
    # The part keeps the name ycli has always sent (`file_data`); the API docs name none.
    Case(
        "tracker.import_.file",
        args=("JUNE-5",),
        kwargs={
            "filename": "renamed.png",
            "created_at": "2022-05-06T07:08:09.000+0000",
            "created_by": "16",
            "data": b"PNGDATA",
        },
        cli=[
            "tracker",
            "import",
            "file",
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
            "tracker_import_file",
            {
                "issue_key": "JUNE-5",
                "filename": "renamed.png",
                "created_at": "2022-05-06T07:08:09.000+0000",
                "created_by": "16",
                "data": "PNGDATA",
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
        "tracker.import_.file",
        args=("JUNE-6",),
        kwargs={
            "filename": "pic.png",
            "created_at": "2023-06-07T08:09:10.000+0000",
            "created_by": "17",
            "data": b"PNGDATA",
        },
        cli=[
            "tracker",
            "import",
            "file",
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
]
