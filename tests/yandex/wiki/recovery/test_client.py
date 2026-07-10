import requests
import responses

from ycli.yandex.wiki.recovery.client import RecoveryClient
from ycli.yandex.wiki.recovery.models import RecoveredPage

BASE = "https://api.wiki.yandex.net/v1"


def _client():
    s = requests.Session()
    s.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return RecoveryClient(session=s)


@responses.activate
def test_restore_posts_to_recover_and_returns_page():
    responses.add(
        responses.POST,
        f"{BASE}/recovery_tokens/tok-uuid/recover",
        json={"id": 42, "slug": "data/x"},
        status=200,
    )
    out = _client().restore(token="tok-uuid")
    assert isinstance(out, RecoveredPage)
    assert out.id == 42 and out.slug == "data/x"
    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url.endswith("/recovery_tokens/tok-uuid/recover")  # ty: ignore[unresolved-attribute]
