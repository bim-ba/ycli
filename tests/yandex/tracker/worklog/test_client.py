"""TDD for WorklogClient."""
import requests
import responses

from ycli.yandex.tracker.worklog.client import WorklogClient
from ycli.yandex.tracker.worklog.models import WorklogList

BASE = "https://api.tracker.yandex.net/v3"


@responses.activate
def test_list_returns_workloglist():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    responses.add(responses.GET, f"{BASE}/issues/DE-1/worklog",
                  json=[{"id": 5, "createdBy": {"display": "X"}, "duration": "PT2H"}], status=200)
    out = WorklogClient(session=s).list("DE-1")
    assert isinstance(out, WorklogList)
    assert out.root[0].duration == "PT2H" and out.root[0].author_display == "X"
