"""Contract cases for Tracker issue ``/checklistItems`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.tracker.checklists.models import ChecklistItemCreate, ChecklistItemUpdate

CASES = [
    Case(
        "tracker.checklists.get",
        args=("DE-31",),
        cli=["tracker", "checklists", "get", "DE-31"],
        mcp=("tracker_checklists_get", {"key": "DE-31"}),
        exchanges=[
            (
                Sent("GET", "issues/DE-31/checklistItems"),
                Reply(json=[{"id": "5f1", "text": "Review the PR", "checked": False}]),
            )
        ],
    ),
    Case(
        "tracker.checklists.create",
        args=(
            "DE-32",
            ChecklistItemCreate.model_validate(
                {
                    "text": "step 1",
                    "checked": True,
                    "assignee": "sava",
                    "deadline": {"date": "2021-05-09T00:00:00.000+0000", "deadlineType": "date"},
                }
            ),
        ),
        cli=[
            "tracker",
            "checklists",
            "create",
            "DE-32",
            "--text",
            "step 1",
            "--checked",
            "--assignee",
            "sava",
            "--deadline",
            "2021-05-09T00:00:00.000+0000",
        ],
        mcp=(
            "tracker_checklists_create",
            {
                "key": "DE-32",
                "body": {
                    "text": "step 1",
                    "checked": True,
                    "assignee": "sava",
                    "deadline": {"date": "2021-05-09T00:00:00.000+0000"},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/DE-32/checklistItems",
                    json={
                        "text": "step 1",
                        "checked": True,
                        "assignee": "sava",
                        "deadline": {
                            "date": "2021-05-09T00:00:00.000+0000",
                            "deadlineType": "date",
                        },
                    },
                ),
                Reply(json={"key": "DE-32", "checklistItems": [{"id": "5f2", "text": "step 1"}]}),
            )
        ],
    ),
    # A quarter deadline is an MCP/SDK-only choice.
    Case(
        "tracker.checklists.create",
        args=(
            "DE-33",
            ChecklistItemCreate.model_validate(
                {"text": "Q4 goal", "deadline": {"date": "2026-10-01", "deadlineType": "quarter"}}
            ),
        ),
        cli=None,
        mcp=(
            "tracker_checklists_create",
            {
                "key": "DE-33",
                "body": {
                    "text": "Q4 goal",
                    "deadline": {"date": "2026-10-01", "deadline_type": "quarter"},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "issues/DE-33/checklistItems",
                    json={
                        "text": "Q4 goal",
                        "deadline": {"date": "2026-10-01", "deadlineType": "quarter"},
                    },
                ),
                Reply(json={"key": "DE-33", "checklistItems": [{"id": "5f3", "text": "Q4 goal"}]}),
            )
        ],
    ),
    Case(
        "tracker.checklists.edit",
        args=(
            "DE-34",
            "5f4",
            ChecklistItemUpdate.model_validate(
                {
                    "text": "step 2",
                    "checked": False,
                    "assignee": "petr",
                    "deadline": {"date": "2022-01-02T00:00:00.000+0300", "deadlineType": "date"},
                }
            ),
        ),
        cli=[
            "tracker",
            "checklists",
            "update",
            "DE-34",
            "5f4",
            "--text",
            "step 2",
            "--no-checked",
            "--assignee",
            "petr",
            "--deadline",
            "2022-01-02T00:00:00.000+0300",
        ],
        mcp=(
            "tracker_checklists_update",
            {
                "key": "DE-34",
                "item_id": "5f4",
                "body": {
                    "text": "step 2",
                    "checked": False,
                    "assignee": "petr",
                    "deadline": {"date": "2022-01-02T00:00:00.000+0300"},
                },
            },
        ),
        exchanges=[
            (
                Sent(
                    "PATCH",
                    "issues/DE-34/checklistItems/5f4",
                    json={
                        "text": "step 2",
                        "checked": False,
                        "assignee": "petr",
                        "deadline": {
                            "date": "2022-01-02T00:00:00.000+0300",
                            "deadlineType": "date",
                        },
                    },
                ),
                Reply(json={"key": "DE-34", "checklistItems": [{"id": "5f4", "text": "step 2"}]}),
            )
        ],
    ),
    # Only the supplied fields are sent.
    Case(
        "tracker.checklists.edit",
        args=("DE-35", "5f5", ChecklistItemUpdate.model_validate({"checked": True})),
        cli=["tracker", "checklists", "update", "DE-35", "5f5", "--checked"],
        mcp=(
            "tracker_checklists_update",
            {"key": "DE-35", "item_id": "5f5", "body": {"checked": True}},
        ),
        exchanges=[
            (
                Sent("PATCH", "issues/DE-35/checklistItems/5f5", json={"checked": True}),
                Reply(json={"key": "DE-35", "checklistItems": [{"id": "5f5", "checked": True}]}),
            )
        ],
    ),
    # The API answers both deletes with 200 and the issue's remaining checklist.
    Case(
        "tracker.checklists.delete",
        args=("DE-36", "5f6"),
        cli=["tracker", "checklists", "delete", "DE-36", "5f6"],
        mcp=("tracker_checklists_delete", {"key": "DE-36", "item_id": "5f6"}),
        exchanges=[
            (
                Sent("DELETE", "issues/DE-36/checklistItems/5f6"),
                Reply(json={"key": "DE-36", "checklistItems": [{"id": "5f7", "text": "left"}]}),
            )
        ],
    ),
    Case(
        "tracker.checklists.clear",
        args=("DE-37",),
        cli=["tracker", "checklists", "clear", "DE-37"],
        mcp=("tracker_checklists_clear", {"key": "DE-37"}),
        exchanges=[
            (
                Sent("DELETE", "issues/DE-37/checklistItems"),
                Reply(json={"key": "DE-37", "checklistItems": []}),
            )
        ],
    ),
]
