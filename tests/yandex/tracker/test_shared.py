"""TDD for the tracker per-domain base."""

import requests

from ycli.yandex.tracker.base import TrackerResource


class _Demo(TrackerResource):
    pass


def test_base_url_is_tracker_v3():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.tracker.yandex.net/v3"
