"""TDD for BaseYandex — base_url classvar + env resolution, no ApiKind."""
import pytest
import requests
from ycli.yandex.base import BaseYandex, session_from_env


class _Demo(BaseYandex):
    base_url = "https://api.example.net/v1"


def test_base_url_classvar_is_used_and_normalized():
    c = _Demo(session=requests.Session())
    assert str(c.session.base_url).rstrip("/") == "https://api.example.net/v1"


def test_init_requires_keyword_session():
    with pytest.raises(TypeError):
        _Demo()  # type: ignore[call-arg]


def test_session_from_env_reads_both_vars(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    s = session_from_env()
    assert s.headers["Authorization"] == "OAuth tok"
    assert s.headers["X-Org-Id"] == "org"


def test_session_from_env_missing_token_raises(monkeypatch):
    monkeypatch.delenv("YANDEX_ID_OAUTH_TOKEN", raising=False)
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    with pytest.raises(ValueError, match="YANDEX_ID_OAUTH_TOKEN"):
        session_from_env()


def test_session_from_env_missing_org_raises(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.delenv("YANDEX_ID_ORGANIZATION_ID", raising=False)
    with pytest.raises(ValueError, match="YANDEX_ID_ORGANIZATION_ID"):
        session_from_env()


def test_from_env_builds_authed_instance(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    c = _Demo.from_env()
    assert c._session.headers["Authorization"] == "OAuth tok"
