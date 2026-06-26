"""TDD for the tracker per-domain base + shared sub-models."""
import requests

from ycli.yandex.tracker._base import TrackerResource
from ycli.yandex.tracker._models import _DisplayRef, _IdRef, _KeyRef, _Lenient


class _Demo(TrackerResource):
    pass


def test_base_url_is_tracker_v3():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.tracker.yandex.net/v3"


def test_shared_refs_extract_scalar():
    assert _KeyRef.model_validate({"key": "task", "x": 1}).key == "task"
    assert _IdRef.model_validate({"id": "relates"}).id == "relates"
    assert _DisplayRef.model_validate({"display": "Сава"}).display == "Сава"


def test_lenient_ignores_extra_and_populates_by_name():
    m = _Lenient.model_validate({"unknown": 1})  # extra ignored, no error
    assert m.model_config["extra"] == "ignore"
    assert m.model_config["populate_by_name"] is True
