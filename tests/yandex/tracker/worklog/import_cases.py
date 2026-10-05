"""Contract cases for the import of Tracker worklog (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.worklog.models import ImportWorklog

IMPORT_CASES = [
    Case(
        "tracker.worklog.import_",
        args=(
            "TEST-5",
            ImportWorklog.model_validate(
                {
                    "duration": "PT2H",
                    "createdAt": "2021-04-05T06:07:08.000+0000",
                    "createdBy": "15",
                    "start": "2021-04-05T09:00:00.000+0000",
                    "comment": "Backfilled",
                }
            ),
        ),
        cli=[
            "tracker",
            "worklog",
            "import",
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
            "tracker_worklog_import",
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
]
