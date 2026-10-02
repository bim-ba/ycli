import httpx2
import pytest
import stamina

from tests.mock_api import MockAPI


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    """Shared Yandex 360 credentials for every test.

    autouse so tests that never request it explicitly (registration-only / annotation-only
    tests) still get valid env, matching the ~47 files that previously relied on a local
    autouse fixture. Tests that need NO credentials always delete these env vars themselves
    (in their own body, or a file-local autouse fixture that runs after this one, since
    conftest.py autouse fixtures execute before module-level ones of the same scope) — which
    correctly overrides this fixture regardless of the values it pre-set.
    """
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")


def _unmocked(request: httpx2.Request) -> httpx2.Response:
    raise AssertionError(f"unmocked core request: {request.method} {request.url}")


@pytest.fixture(autouse=True)
def _offline_core(monkeypatch):
    """No test reaches the network through the httpx2 core; ``api`` answers instead."""
    monkeypatch.setattr(
        "ycli.yandex.core.session.default_transport", lambda: httpx2.MockTransport(_unmocked)
    )


@pytest.fixture
def api(monkeypatch) -> MockAPI:
    """Canned answers for every request the httpx2 core sends."""
    mock = MockAPI()
    monkeypatch.setattr("ycli.yandex.core.session.default_transport", mock.transport)
    return mock


@pytest.fixture(autouse=True)
def _instant_retries():
    """Retries keep their attempt count but never sleep (stamina's testing mode)."""
    with stamina.set_testing(True, attempts=10, cap=True):
        yield
