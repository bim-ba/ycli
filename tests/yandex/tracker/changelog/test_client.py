"""TDD for ChangelogClient."""
import requests
import responses

from ycli.yandex.tracker.changelog.client import ChangelogClient
from ycli.yandex.tracker.changelog.models import ChangelogList

BASE = "https://api.tracker.yandex.net/v3"


@responses.activate
def test_list_passes_perpage_and_parses_polymorphic_fields():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    responses.add(responses.GET, f"{BASE}/issues/DE-1/changelog",
                  json=[{"id": "ch1", "updatedBy": {"display": "Сава"}, "type": "IssueUpdated",
                         "fields": [{"field": {"id": "status"}, "from": None,
                                     "to": {"key": "done", "display": "Готово"}}]}], status=200)
    out = ChangelogClient(session=s).list("DE-1", per_page=50)
    assert isinstance(out, ChangelogList)
    e = out.root[0]
    assert e.author_display == "Сава"
    assert e.fields[0].to == {"key": "done", "display": "Готово"}  # polymorphic passthrough
    assert responses.calls[0].request.params["perPage"] == "50"
