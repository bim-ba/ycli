"""Contract cases for the import of Tracker issues (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.issues.models import ImportTask

IMPORT_CASES = [
    Case(
        "tracker.issues.import_",
        args=(
            ImportTask.model_validate(
                {
                    "queue": "TEST",
                    "summary": "Old task",
                    "createdAt": "2017-08-29T12:34:41.740+0000",
                    "createdBy": "11",
                    "key": "TEST-41",
                    "description": "Imported from Jira",
                    "assignee": "bob",
                }
            ),
        ),
        cli=[
            "tracker",
            "issues",
            "import",
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
            "tracker_issues_import",
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
        "tracker.issues.import_",
        args=(
            ImportTask.model_validate(
                {
                    "queue": "OPS",
                    "summary": "Bare import",
                    "createdAt": "2018-01-02T03:04:05.000+0000",
                    "createdBy": "12",
                }
            ),
        ),
        cli=[
            "tracker",
            "issues",
            "import",
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
]
