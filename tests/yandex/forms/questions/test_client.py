"""TDD for QuestionsClient — returns the {pages} envelope verbatim (no flattening)."""

import requests
import responses

from ycli.yandex.forms.questions.client import QuestionsClient
from ycli.yandex.forms.questions.models import Question, QuestionsResponse

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
