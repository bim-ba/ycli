"""Contract cases for Forms form filling (see tests/contract.py)."""

from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.filling.models import SubmitBody

SID = "686d0a1b2c3d4e5f00000060"
ANSWER_FILE = Path(__file__).with_name("answer.json")
FORM = {"id": SID, "name": "Feedback", "pages": [{"items": []}]}

CASES = [
    Case(
        "forms.filling.get",
        args=(SID,),
        kwargs={"key": "k-1"},
        cli=["forms", "filling", "get", SID, "--key", "k-1"],
        mcp=("forms_filling_get", {"survey_id": SID, "key": "k-1"}),
        exchanges=[(Sent("GET", f"surveys/{SID}/form", {"key": "k-1"}), Reply(json=FORM))],
    ),
    Case(
        "forms.filling.submit",
        args=(SID, SubmitBody.model_validate({"name": "Ann", "rating": 5})),
        kwargs={"validate_only": True, "key": "k-2"},
        cli=[
            "forms",
            "filling",
            "submit",
            SID,
            "--body-file",
            str(ANSWER_FILE),
            "--validate-only",
            "--key",
            "k-2",
        ],
        mcp=(
            "forms_filling_submit",
            {
                "survey_id": SID,
                "body": {"name": "Ann", "rating": 5},
                "validate_only": True,
                "key": "k-2",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"surveys/{SID}/form",
                    {"dry_run": "true", "key": "k-2"},
                    {"name": "Ann", "rating": 5},
                ),
                Reply(json={"answer_id": 99}),
            )
        ],
    ),
    Case(
        "forms.filling.suggest",
        args=(SID,),
        kwargs={"question": "city", "text": "Ber", "suggest_id": "1,2", "parent_id": "de"},
        cli=[
            "forms",
            "filling",
            "suggest",
            SID,
            "--question",
            "city",
            "--text",
            "Ber",
            "--suggest-id",
            "1,2",
            "--parent-id",
            "de",
        ],
        mcp=(
            "forms_filling_suggest",
            {
                "survey_id": SID,
                "question": "city",
                "text": "Ber",
                "suggest_id": "1,2",
                "parent_id": "de",
            },
        ),
        exchanges=[
            (
                Sent(
                    "GET",
                    f"surveys/{SID}/suggest",
                    {"question": "city", "text": "Ber", "id": "1,2", "parent_id": "de"},
                ),
                Reply(json=[{"id": "b", "text": "Berlin"}]),
            )
        ],
    ),
]
