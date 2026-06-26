import requests
import responses
from ycli.yandex.wiki.attachments.client import AttachmentsClient
from ycli.yandex.wiki.attachments.models import AttachmentsResponse

BASE = "https://api.wiki.yandex.net/v1"

def _client():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return AttachmentsClient(session=s)

@responses.activate
def test_list_attachments_for_page_id():
    responses.add(responses.GET, f"{BASE}/pages/42/attachments",
                  json={"results": [{"name": "f.pdf", "size": 1, "mime_type": "application/pdf"}]}, status=200)
    out = _client().list(page_id=42)
    assert isinstance(out, AttachmentsResponse)
    assert out.results[0].name == "f.pdf"
