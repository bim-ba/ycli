"""TDD for BaseYandex — base_url classvar + session DI, no from_env."""
import pytest
import requests

from ycli.yandex.base import BaseYandex


class _Demo(BaseYandex):
    base_url = "https://api.example.net/v1"


def test_base_url_classvar_is_used_and_normalized():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.example.net/v1"


def test_init_requires_keyword_session():
    with pytest.raises(TypeError):
        _Demo()  # type: ignore[call-arg]
