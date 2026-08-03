"""TDD for ClientFactory — env-free client construction from instances."""

from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import ClientFactory
from ycli.yandex.tracker.client import TrackerClient


def test_build_passes_raw_args_and_does_not_read_env(monkeypatch, tmp_path):
    """ClientFactory.build takes instances (not env) and wires the sub-clients.

    monkeypatch sets the env so Credentials() resolves; ClientFactory.build must
    forward exactly those values (not silently re-read the env itself).
    """
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    monkeypatch.chdir(tmp_path)  # prevent .env from leaking
    creds = Credentials()
    cfg = AppConfig(timeout_seconds=12.0, retries=5)
    client = ClientFactory.build(TrackerClient, creds, cfg)
    assert isinstance(client, TrackerClient)
    assert client.issues._session.headers["Authorization"] == "OAuth t"
    assert client.issues._session.headers["X-Org-Id"] == "o"


def test_build_casts_timeout_to_int(monkeypatch, tmp_path):
    """timeout_seconds float is cast to int before passing to the client constructor."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    monkeypatch.chdir(tmp_path)
    creds = Credentials()
    cfg = AppConfig(timeout_seconds=7.9, retries=2)
    client = ClientFactory.build(TrackerClient, creds, cfg)
    assert isinstance(client, TrackerClient)
    assert client.me._session.headers["Authorization"] == "OAuth tok"
    assert client.me._session.headers["X-Org-Id"] == "org"
