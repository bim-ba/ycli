"""TDD for AnswersClient — returns the {columns, answers, next} envelope verbatim."""
import requests
import responses

from ycli.yandex.forms.answers.client import AnswersClient
from ycli.yandex.forms.answers.models import AnswersResponse

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _client() -> AnswersClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return AnswersClient(session=s)


@responses.activate
def test_list_returns_envelope_verbatim():
    responses.add(responses.GET, f"{BASE}/surveys/{SID}/answers",
                  json={"columns": [{"id": 1, "slug": "s1", "type": "string", "text": "T"}],
                        "answers": [{"id": 99, "created": "2026-01-01", "data": [{"value": "x"}]}],
                        "next": None}, status=200)
    ar = _client().list(SID)
    assert isinstance(ar, AnswersResponse)
    assert ar.columns[0].text == "T"
    assert ar.answers[0].id == 99 and ar.answers[0].data == [{"value": "x"}]
    assert ar.next is None
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}/answers"
