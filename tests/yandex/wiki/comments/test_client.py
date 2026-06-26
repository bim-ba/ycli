import requests
import responses
from ycli.yandex.wiki.comments.client import CommentsClient
from ycli.yandex.wiki.comments.models import CommentsResponse

BASE = "https://api.wiki.yandex.net/v1"

def _client():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return CommentsClient(session=s)

@responses.activate
def test_list_comments_for_page_id():
    responses.add(responses.GET, f"{BASE}/pages/42/comments",
                  json={"results": [{"created_at": "2026-01-01", "content": "hi"}]}, status=200)
    out = _client().list(page_id=42)
    assert isinstance(out, CommentsResponse)
    assert out.results[0].content == "hi"
