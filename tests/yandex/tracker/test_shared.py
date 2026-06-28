"""TDD for the tracker per-domain base + shared sub-models."""
import requests

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker._models import _DisplayRef, _IdRef, _KeyRef


class _Demo(TrackerResource):
    pass


def test_base_url_is_tracker_v3():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.tracker.yandex.net/v3"


def test_shared_refs_extract_scalar():
    assert _KeyRef.model_validate({"key": "task", "x": 1}).key == "task"
    assert _IdRef.model_validate({"id": "relates"}).id == "relates"
    assert _DisplayRef.model_validate({"display": "Сава"}).display == "Сава"
