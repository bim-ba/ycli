"""Contract cases for the import of Tracker comments (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.comments.models import ImportComment

IMPORT_CASES = [
    Case(
        "tracker.comments.import_",
        args=(
            "TEST-2",
            ImportComment.model_validate(
                {
                    "text": "Old comment",
                    "createdAt": "2019-02-03T04:05:06.000+0000",
                    "createdBy": "13",
                }
            ),
        ),
        cli=[
            "tracker",
            "comments",
            "import",
            "TEST-2",
            "--text",
            "Old comment",
            "--created-at",
            "2019-02-03T04:05:06.000+0000",
            "--created-by",
            "13",
        ],
        mcp=(
            "tracker_comments_import",
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
]
