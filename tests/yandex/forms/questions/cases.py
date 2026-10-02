"""Contract cases for Forms ``/surveys/{id}/questions`` (see tests/contract.py)."""

import json
from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.forms.questions.models import (
    BooleanQuestion,
    DateQuestion,
    EnumQuestion,
    IntegerQuestion,
    QuestionCreateAdapter,
    QuestionEnumItem,
    QuestionMove,
    QuestionValidator,
    StringQuestion,
)

SID = "686d0a1b2c3d4e5f00000010"
QUESTIONS = f"surveys/{SID}/questions"
QUESTION = {"id": 17, "slug": "name", "type": "string", "label": "Name"}
MATRIX = Path(__file__).with_name("matrix.json")
STRING_BODY = {
    "label": "Name",
    "slug": "name",
    "comment": "Your name",
    "placeholder": "Ann",
    "hidden": False,
    "type": "string",
    "multiline": True,
    "validators": [{"type": "required"}],
}
ENUM_BODY = {
    "label": "Color",
    "type": "enum",
    "widget": "checkbox",
    "items": [{"label": "Red"}, {"label": "Blue"}],
    "validators": [],
}

CASES = [
    Case(
        "forms.questions.list",
        args=(SID,),
        cli=["forms", "questions", "list", SID],
        mcp=("forms_questions_list", {"survey_id": SID}),
        exchanges=[(Sent("GET", QUESTIONS), Reply(json={"pages": [{"items": [QUESTION]}]}))],
    ),
    Case(
        "forms.questions.get",
        args=(SID, "17"),
        cli=["forms", "questions", "get", SID, "17"],
        mcp=("forms_questions_get", {"survey_id": SID, "question_id": "17"}),
        exchanges=[(Sent("GET", f"{QUESTIONS}/17"), Reply(json=QUESTION))],
    ),
    Case(
        "forms.questions.create",
        args=(
            SID,
            StringQuestion(
                label="Name",
                slug="name",
                comment="Your name",
                placeholder="Ann",
                hidden=False,
                multiline=True,
                validators=[QuestionValidator(type="required")],
            ),
        ),
        cli=[
            "forms",
            "questions",
            "create",
            SID,
            "--type",
            "string",
            "--label",
            "Name",
            "--slug",
            "name",
            "--comment",
            "Your name",
            "--placeholder",
            "Ann",
            "--no-hidden",
            "--multiline",
            "--required",
        ],
        mcp=("forms_questions_create", {"survey_id": SID, "body": STRING_BODY}),
        exchanges=[(Sent("POST", QUESTIONS, json=STRING_BODY), Reply(json=QUESTION, status=201))],
    ),
    Case(
        "forms.questions.create",
        args=(
            SID,
            EnumQuestion(
                label="Color",
                widget="checkbox",
                items=[QuestionEnumItem(label="Red"), QuestionEnumItem(label="Blue")],
                validators=[],
            ),
        ),
        cli=[
            "forms",
            "questions",
            "create",
            SID,
            "--type",
            "enum",
            "--label",
            "Color",
            "--widget",
            "checkbox",
            "--option",
            "Red",
            "--option",
            "Blue",
            "--no-required",
        ],
        mcp=("forms_questions_create", {"survey_id": SID, "body": ENUM_BODY}),
        exchanges=[(Sent("POST", QUESTIONS, json=ENUM_BODY), Reply(json=QUESTION, status=201))],
    ),
    *(
        Case(
            "forms.questions.create",
            args=(SID, model(label=label, hidden=True)),
            cli=["forms", "questions", "create", SID, "--type", kind, "--label", label, "--hidden"],
            mcp=None,
            exchanges=[
                (
                    Sent("POST", QUESTIONS, json={"label": label, "hidden": True, "type": kind}),
                    Reply(json=QUESTION, status=201),
                )
            ],
        )
        for kind, model, label in (
            ("boolean", BooleanQuestion, "Agree?"),
            ("integer", IntegerQuestion, "Age"),
            ("date", DateQuestion, "Birthday"),
        )
    ),
    Case(
        "forms.questions.modify",
        args=(SID, "18", QuestionCreateAdapter.validate_json(MATRIX.read_text())),
        cli=["forms", "questions", "modify", SID, "18", "--body-file", str(MATRIX)],
        mcp=(
            "forms_questions_modify",
            {"survey_id": SID, "question_id": "18", "body": json.loads(MATRIX.read_text())},
        ),
        exchanges=[
            (
                Sent("PATCH", f"{QUESTIONS}/18", json=json.loads(MATRIX.read_text())),
                Reply(json=QUESTION),
            )
        ],
    ),
    Case(
        "forms.questions.delete",
        args=(SID, "19"),
        kwargs={"force": True},
        cli=["forms", "questions", "delete", SID, "19", "--force"],
        mcp=("forms_questions_delete", {"survey_id": SID, "question_id": "19", "force": True}),
        exchanges=[(Sent("DELETE", f"{QUESTIONS}/19", {"force": "true"}), Reply(status=204))],
    ),
    Case(
        "forms.questions.move",
        args=(SID, "20", QuestionMove(page_id=55, position=2, question="q7")),
        cli=[
            "forms",
            "questions",
            "move",
            SID,
            "20",
            "--page-id",
            "55",
            "--position",
            "2",
            "--question",
            "q7",
        ],
        mcp=(
            "forms_questions_move",
            {
                "survey_id": SID,
                "question_id": "20",
                "body": {"question": "q7", "page_id": 55, "position": 2},
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    f"{QUESTIONS}/20/move",
                    json={"question": "q7", "page_id": 55, "position": 2},
                ),
                Reply(json={"id": 20}),
            )
        ],
    ),
    # A bare --position visibly defaults the page to 1: the API ignores a position alone.
    Case(
        "forms.questions.move",
        args=(SID, "21", QuestionMove(page=1, position=3)),
        cli=["forms", "questions", "move", SID, "21", "--position", "3"],
        mcp=None,
        exchanges=[
            (
                Sent("POST", f"{QUESTIONS}/21/move", json={"page": 1, "position": 3}),
                Reply(json={"id": 21}),
            )
        ],
    ),
]
