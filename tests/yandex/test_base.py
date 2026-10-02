"""TDD for BaseYandex — base_url classvar + session DI, no from_env."""

import pytest
import requests

from ycli.yandex.base import BaseYandex
from ycli.yandex.tracker.client import TrackerClient


class _Demo(BaseYandex):
    base_url = "https://api.example.net/v1"


def test_base_url_classvar_is_used_and_normalized():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.example.net/v1"


def test_init_requires_keyword_session():
    with pytest.raises(TypeError):
        _Demo()  # type: ignore[call-arg]  # ty: ignore[missing-argument]


def test_a_domain_client_closes_both_of_its_transports(monkeypatch):
    """Leaving the ``with`` block closes the httpx2 core client and the requests session."""
    session = requests.Session()
    closed: list[str] = []
    monkeypatch.setattr(session, "close", lambda: closed.append("requests"))
    with TrackerClient(oauth_token="t", organization_id="o", session=session) as client:
        core = client.issues._session._client
        assert not core.is_closed
    assert core.is_closed
    assert closed == ["requests"]
