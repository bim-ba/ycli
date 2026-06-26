"""TDD for the forms per-domain base + shared sub-model."""
import requests

from ycli.yandex.forms._base import FormsResource
from ycli.yandex.forms._models import _Lenient


class _Demo(FormsResource):
    pass


def test_base_url_is_forms_v1():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.forms.yandex.net/v1"


def test_lenient_ignores_extra_and_populates_by_name():
    m = _Lenient.model_validate({"unknown": 1})  # extra ignored, no error
    assert m.model_config["extra"] == "ignore"
    assert m.model_config["populate_by_name"] is True
