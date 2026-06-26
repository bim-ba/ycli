"""TDD for the three Tracker lookup clients."""
import requests
import responses

from ycli.yandex.tracker.issuetypes.client import IssueTypesClient
from ycli.yandex.tracker.issuetypes.models import IssueTypeList
from ycli.yandex.tracker.linktypes.client import LinkTypesClient
from ycli.yandex.tracker.linktypes.models import LinkTypeList
from ycli.yandex.tracker.priorities.client import PrioritiesClient
from ycli.yandex.tracker.priorities.models import PriorityList

BASE = "https://api.tracker.yandex.net/v3"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return s


@responses.activate
def test_priorities_list():
    responses.add(responses.GET, f"{BASE}/priorities",
                  json=[{"key": "critical", "display": "Critical"}], status=200)
    out = PrioritiesClient(session=_session()).list()
    assert isinstance(out, PriorityList) and out.root[0].key == "critical"


@responses.activate
def test_issuetypes_list():
    responses.add(responses.GET, f"{BASE}/issuetypes",
                  json=[{"key": "task", "display": "Task"}], status=200)
    out = IssueTypesClient(session=_session()).list()
    assert isinstance(out, IssueTypeList) and out.root[0].key == "task"


@responses.activate
def test_linktypes_list():
    responses.add(responses.GET, f"{BASE}/linktypes",
                  json=[{"id": "relates", "inward": "related to", "outward": "related to"}], status=200)
    out = LinkTypesClient(session=_session()).list()
    assert isinstance(out, LinkTypeList) and out.root[0].id == "relates"
