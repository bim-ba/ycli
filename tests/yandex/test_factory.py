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
    creds = Credentials()  # ty: ignore[missing-argument]
    cfg = AppConfig(http={"timeout_seconds": 12.0, "retries": 5})  # ty: ignore[invalid-argument-type]
    client = ClientFactory.build(TrackerClient, creds, cfg)
    assert isinstance(client, TrackerClient)
    assert client.me._session.headers["Authorization"] == "OAuth t"
    assert client.me._session.headers["X-Org-Id"] == "o"
    adapter = client.me._session.get_adapter("https://")
    assert adapter._timeout == 12.0
    assert adapter.max_retries.total == 5


def test_build_forwards_fractional_timeout(monkeypatch, tmp_path):
    """A fractional ``timeout_seconds`` reaches the adapter unrounded: 0.5 must not become 0."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    monkeypatch.setenv("YCLI__HTTP__TIMEOUT_SECONDS", "0.5")
    monkeypatch.chdir(tmp_path)
    creds = Credentials()  # ty: ignore[missing-argument]
    cfg = AppConfig()
    client = ClientFactory.build(TrackerClient, creds, cfg)
    assert isinstance(client, TrackerClient)
    assert client.me._session.get_adapter("https://")._timeout == 0.5
