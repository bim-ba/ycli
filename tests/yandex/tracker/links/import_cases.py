"""Contract cases for the import of Tracker links (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.links.models import ImportLink

IMPORT_CASES = [
    Case(
        "tracker.links.import_",
        args=(
            "TEST-3",
            ImportLink.model_validate(
                {
                    "relationship": "depends on",
                    "issue": "TEST-4",
                    "createdAt": "2020-03-04T05:06:07.000+0000",
                    "createdBy": "14",
                }
            ),
        ),
        cli=[
            "tracker",
            "links",
            "import",
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
            "tracker_links_import",
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
]
