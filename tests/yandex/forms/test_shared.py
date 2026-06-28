"""TDD for the forms per-domain base."""

import requests

from ycli.yandex.forms._base import FormsResource


class _Demo(FormsResource):
    pass


def test_base_url_is_forms_v1():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.forms.yandex.net/v1"
