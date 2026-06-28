"""TDD for SurveysClient — list returns flat SurveyCollection; get returns one Survey."""

import requests
import responses

from ycli.yandex.forms.surveys.client import SurveysClient
from ycli.yandex.forms.surveys.models import Survey, SurveyCollection

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _client() -> SurveysClient:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return SurveysClient(session=s)


@responses.activate
def test_list_returns_flat_collection():
    responses.add(
        responses.GET,
        f"{BASE}/surveys",
        json={"links": {}, "result": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]},
        status=200,
    )
    out = _client().list()
    assert isinstance(out, SurveyCollection)
    assert [s.id for s in out.root] == ["a", "b"]


@responses.activate
def test_get_returns_single_survey():
    responses.add(
        responses.GET,
        f"{BASE}/surveys/{SID}",
        json={"id": SID, "name": "Новая Задача", "is_published": True, "language": "ru"},
        status=200,
    )
    s = _client().get(SID)
    assert isinstance(s, Survey)
    assert s.id == SID and s.is_published is True
    assert responses.calls[0].request.url == f"{BASE}/surveys/{SID}"
