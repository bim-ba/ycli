"""Contract cases for Forms answers (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

SID = "686d0a1b2c3d4e5f00000030"
ANSWER = {"id": 2469549806, "survey": {"id": SID, "name": "Feedback"}, "data": []}
PAGE = {
    "columns": [{"slug": "answer_short_text_1", "label": "Name"}],
    "answers": [{"id": 1, "data": ["Ann"]}],
    "next": None,
}
EXPORT = {
    "format": "csv",
    "upload": "disk",
    "started_at": "2026-01-01T00:00:00",
    "finished_at": "2026-02-01T00:00:00",
    "pks": [11, 12],
    "columns": ["answer_short_text_1"],
    "limit": 30,
    "upload_files": True,
}
OPERATION = {"id": "op-77", "status": "running"}

CASES = [
    Case(
        "forms.answers.get",
        kwargs={"answer_id": 2469549806},
        cli=["forms", "answers", "get", "--answer-id", "2469549806"],
        mcp=("forms_answers_get", {"answer_id": 2469549806}),
        exchanges=[(Sent("GET", "answers", {"answer_id": "2469549806"}), Reply(json=ANSWER))],
    ),
    Case(
        "forms.answers.get",
        kwargs={"answer_key": "a1b2c3"},
        cli=["forms", "answers", "get", "--answer-key", "a1b2c3"],
        mcp=("forms_answers_get", {"answer_key": "a1b2c3"}),
        exchanges=[(Sent("GET", "answers", {"answer_key": "a1b2c3"}), Reply(json=ANSWER))],
    ),
    Case(
        "forms.answers.list",
        args=(SID,),
        cli=None,
        mcp=None,
        exchanges=[(Sent("GET", f"surveys/{SID}/answers"), Reply(json=PAGE))],
    ),
    Case(
        "forms.answers.list_all",
        args=(SID,),
        kwargs={"limit": 500},
        cli=["forms", "answers", "list", SID],
        mcp=("forms_answers_list", {"survey_id": SID}),
        exchanges=[(Sent("GET", f"surveys/{SID}/answers"), Reply(json=PAGE))],
    ),
    # A limit below the page keeps only that many answers (MCP always uses the configured cap).
    Case(
        "forms.answers.list_all",
        args=(SID,),
        kwargs={"limit": 1},
        cli=["forms", "answers", "list", SID, "--limit", "1"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", f"surveys/{SID}/answers"),
                Reply(json={**PAGE, "answers": [{"id": 1}, {"id": 2}]}),
            )
        ],
        output={
            "columns": [
                {
                    "id": None,
                    "slug": "answer_short_text_1",
                    "type": None,
                    "text": None,
                    "has_scores": None,
                }
            ],
            "answers": [{"id": 1, "created": None, "data": []}],
            "next": None,
        },
    ),
    Case(
        "forms.answers.export",
        args=(SID, EXPORT),
        cli=[
            "forms",
            "answers",
            "export",
            SID,
            "--format",
            "csv",
            "--upload",
            "disk",
            "--started-at",
            "2026-01-01T00:00:00",
            "--finished-at",
            "2026-02-01T00:00:00",
            "--pk",
            "11",
            "--pk",
            "12",
            "--column",
            "answer_short_text_1",
            "--limit",
            "30",
            "--upload-files",
            "--no-wait",
        ],
        mcp=("forms_answers_export", {"survey_id": SID, "body": EXPORT}),
        exchanges=[
            (
                Sent("POST", f"surveys/{SID}/answers/export", json=EXPORT),
                Reply(json=OPERATION, status=202),
            )
        ],
    ),
    Case(
        "forms.answers.export_results",
        args=(SID, "op-77"),
        cli=None,
        mcp=None,
        exchanges=[
            (
                Sent("GET", f"surveys/{SID}/answers/export-results", {"task_id": "op-77"}),
                Reply(json=OPERATION),
            )
        ],
    ),
    Case(
        "forms.answers.download_export",
        args=(SID, "op-77"),
        cli=None,
        mcp=None,
        exchanges=[
            (
                Sent("GET", f"surveys/{SID}/answers/export-results", {"task_id": "op-77"}),
                Reply(content=b"id,name\n1,Ann\n"),
            )
        ],
    ),
]
