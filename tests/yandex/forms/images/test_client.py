"""TDD for ImagesClient — a single multipart image upload (field ``image``)."""

import requests
import responses

from ycli.yandex.forms.images.client import ImagesClient
from ycli.yandex.forms.images.models import Image

BASE = "https://api.forms.yandex.net/v1"
SID = "6818ceffe010db4f59d11329"


def _client() -> ImagesClient:
    session = requests.Session()
    session.headers.update({"Authorization": "OAuth t", "X-Org-Id": "o"})
    return ImagesClient(session=session)


@responses.activate
def test_upload_sends_multipart_image_field():
    responses.add(
        responses.POST,
        f"{BASE}/surveys/{SID}/images",
        json={"id": 7, "links": {"orig": "https://x"}, "name": "logo.png", "check_status": "check"},
        status=201,
    )
    out = _client().upload(SID, filename="logo.png", data=b"\x89PNGdata")
    assert isinstance(out, Image)
    assert out.id == 7 and out.name == "logo.png" and out.links == {"orig": "https://x"}
    request = responses.calls[0].request
    assert str(request.headers["Content-Type"]).startswith("multipart/form-data")
    body = request.body
    assert isinstance(body, bytes)
    assert b'name="image"' in body  # the multipart field is named "image"
    assert b'filename="logo.png"' in body
    assert b"\x89PNGdata" in body  # the raw image bytes
