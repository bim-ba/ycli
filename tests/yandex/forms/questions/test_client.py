"""TDD for QuestionsClient — reads (get/list) plus writes (create/modify/delete/move)."""

import json

import requests
import responses

from ycli.yandex.forms.questions.client import QuestionsClient
from ycli.yandex.forms.questions.models import (
    EnumQuestion,
    MatrixQuestion,
    Question,
    QuestionActionResult,
    QuestionEnumItem,
    QuestionMatrixRow,
    QuestionMove,
    QuestionMoveResult,
    QuestionsResponse,
    QuestionValidator,
    StringQuestion,
)

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _client() -> QuestionsClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return QuestionsClient(session=s)


@responses.activate
def test_get_returns_single_question():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/questions/17",
        json={
            "id": 17,
            "slug": "answer_short_text_1",
            "type": "string",
            "label": "Name",
            "placeholder": "Type…",
            "multiline": True,
            "has_quiz": False,
        },
        status=200,
    )
    q = _client().get(SID, "17")
    assert isinstance(q, Question)
    assert q.id == 17 and q.slug == "answer_short_text_1"
    assert q.placeholder == "Type…" and q.multiline is True
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/questions/17"


@responses.activate
def test_list_returns_pages_envelope_verbatim():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}/questions",
        json={
            "pages": [
                {"id": 1, "items": [{"id": 11, "slug": "s1", "type": "string", "label": "A"}]},
                {"id": 2, "items": [{"id": 22, "slug": "s2", "type": "enum", "label": "B"}]},
            ]
        },
        status=200,
    )
    out = _client().list(SID)
    assert isinstance(out, QuestionsResponse)
    assert [q.id for page in out.pages for q in page.items] == [11, 22]
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/questions"


@responses.activate
def test_create_posts_typed_body_and_returns_question():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 17, "slug": "s", "type": "string", "label": "Name"},
        status=201,
    )
    question = StringQuestion(
        label="Name", multiline=True, validators=[QuestionValidator(type="required")]
    )
    out = _client().create(SID, question)
    assert isinstance(out, Question) and out.id == 17
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/questions"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "label": "Name",
        "type": "string",
        "multiline": True,
        "validators": [{"type": "required"}],
    }


@responses.activate
def test_create_serializes_nested_enum_items():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/questions",
        json={"id": 18, "type": "enum", "label": "Pick"},
        status=201,
    )
    body = EnumQuestion(
        label="Pick",
        widget="radio",
        items=[QuestionEnumItem(slug="a", label="A"), QuestionEnumItem(slug="b", label="B")],
    )
    _client().create(SID, body)
    sent = json.loads(responses.calls[0].request.body)  # ty: ignore[invalid-argument-type]
    assert sent["type"] == "enum" and sent["widget"] == "radio"
    assert [item["slug"] for item in sent["items"]] == ["a", "b"]


@responses.activate
def test_modify_patches_typed_body_and_returns_question():
    responses.add(
        responses.PATCH,
        f"{BASE}/surveys/{SID}/questions/17",
        json={"id": 17, "type": "matrix", "label": "Grid"},
        status=200,
    )
    body = MatrixQuestion(label="Grid", rows=[QuestionMatrixRow(slug="r1", label="Row 1")])
    out = _client().modify(SID, "17", body)
    assert isinstance(out, Question) and out.id == 17
    assert responses.calls[0].request.method == "PATCH"
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/questions/17"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "label": "Grid",
        "type": "matrix",
        "rows": [{"slug": "r1", "label": "Row 1"}],
    }


@responses.activate
def test_delete_returns_synthesized_result():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/questions/17", status=204)
    out = _client().delete(SID, "17")
    assert isinstance(out, QuestionActionResult)
    assert out.survey_id == SID and out.question_id == "17" and out.action == "delete"
    assert out.ok is True
    assert responses.calls[0].request.method == "DELETE"
    assert "force" not in (responses.calls[0].request.url or "")


@responses.activate
def test_delete_force_sends_query_flag():
    responses.add(responses.DELETE, f"{BASE}/surveys/{SID}/questions/17", status=204)
    _client().delete(SID, "17", force=True)
    assert responses.calls[0].request.params["force"] == "true"  # ty: ignore[unresolved-attribute]


@responses.activate
def test_move_posts_typed_body_and_returns_id():
    responses.add(
        responses.POST, f"{BASE}/surveys/{SID}/questions/17/move", json={"id": 17}, status=200
    )
    out = _client().move(SID, "17", QuestionMove(page=2, position=1))
    assert isinstance(out, QuestionMoveResult) and out.id == 17
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/questions/17/move"
    assert json.loads(responses.calls[0].request.body) == {  # ty: ignore[invalid-argument-type]
        "page": 2,
        "position": 1,
    }
