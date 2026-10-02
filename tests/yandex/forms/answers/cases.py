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
# One of each shape GET /answers/integrations documents (2026-10-02 spec).
INTEGRATIONS = [
    {"id": 1, "status": "success", "type": "email", "to_address": "ann@example.com"},
    {
        "id": 2,
        "status": "success",
        "type": "wiki",
        "wiki_page": "team/notes",
        "link": "https://wiki.test/team/notes",
    },
    {
        "id": 3,
        "status": "error",
        "type": "tracker",
        "issue_key": "DE-7",
        "link": "https://tracker.test/DE-7",
        "message": "queue closed",
    },
    {"id": 4, "status": "pending", "type": "http", "url": "https://example.com/hook"},
    {"id": 5, "status": "canceled", "type": "function", "function_id": "d4e0abc"},
]

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
        "forms.answers.list_all",
        args=(SID,),
        kwargs={"limit": None},
        cli=["forms", "answers", "list", SID, "--all"],
        mcp=None,
        exchanges=[
            (
                Sent("GET", f"surveys/{SID}/answers"),
                Reply(json={**PAGE, "answers": [{"id": 7}, {"id": 8}]}),
            )
        ],
        env={"YCLI__HTTP__MAX_ITEMS": "1"},
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
            "answers": [
                {"id": 7, "created": None, "data": []},
                {"id": 8, "created": None, "data": []},
            ],
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
    Case(
        "forms.answers.integrations_list",
        kwargs={"answer_id": 2542485382},
        cli=["forms", "answers", "integrations-list", "--answer-id", "2542485382"],
        mcp=("forms_answers_integrations_list", {"answer_id": 2542485382}),
        exchanges=[
            (
                Sent("GET", "answers/integrations", {"answer_id": "2542485382"}),
                Reply(json=INTEGRATIONS),
            )
        ],
    ),
    Case(
        "forms.answers.integrations_list",
        kwargs={"answer_key": "9eb7c89dd54e"},
        cli=["forms", "answers", "integrations-list", "--answer-key", "9eb7c89dd54e"],
        mcp=("forms_answers_integrations_list", {"answer_key": "9eb7c89dd54e"}),
        exchanges=[
            (Sent("GET", "answers/integrations", {"answer_key": "9eb7c89dd54e"}), Reply(json=[]))
        ],
    ),
    Case(
        "forms.answers.delete",
        args=("686d0a1b2c3d4e5f00000031", 2542485431),
        cli=["forms", "answers", "delete", "686d0a1b2c3d4e5f00000031", "2542485431"],
        mcp=(
            "forms_answers_delete",
            {"survey_id": "686d0a1b2c3d4e5f00000031", "answer_id": 2542485431},
        ),
        exchanges=[
            (
                Sent("DELETE", "surveys/686d0a1b2c3d4e5f00000031/answers/2542485431"),
                Reply(status=204),
            )
        ],
    ),
    Case(
        "forms.answers.restore",
        args=("686d0a1b2c3d4e5f00000032", 2542485498),
        cli=["forms", "answers", "restore", "686d0a1b2c3d4e5f00000032", "2542485498"],
        mcp=(
            "forms_answers_restore",
            {"survey_id": "686d0a1b2c3d4e5f00000032", "answer_id": 2542485498},
        ),
        exchanges=[
            (Sent("POST", "surveys/686d0a1b2c3d4e5f00000032/answers/2542485498/restore"), Reply())
        ],
    ),
]
