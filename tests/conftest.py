import httpx2
import pytest
import stamina
import typer.rich_utils

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


@pytest.fixture(autouse=True)
def profiles_directory(monkeypatch, tmp_path):
    """An empty profiles directory of the test's own, and no profile named by the environment.

    The developer's own profiles never leak into a test; the path is where a test saves one.
    """
    monkeypatch.delenv("YCLI_PROFILE", raising=False)
    monkeypatch.setattr("ycli.settings.user_config_path", lambda name: tmp_path / "config" / name)
    return tmp_path / "config" / "ycli" / "profiles"


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
def _plain_help(monkeypatch):
    """Help and usage errors in plain text, as on a developer's machine.

    Typer forces a rich terminal when ``GITHUB_ACTIONS`` is set (read once, at import), so in
    CI the captured output carries style codes that split option names; ``None`` lets rich
    detect the captured stream, which is not a terminal.
    """
    monkeypatch.setattr(typer.rich_utils, "FORCE_TERMINAL", None)


@pytest.fixture(autouse=True)
def _instant_retries():
    """Retries keep their attempt count but never sleep (stamina's testing mode)."""
    with stamina.set_testing(True, attempts=10, cap=True):
        yield
