"""TDD for build_client — env-free client construction from instances."""

from pydantic import SecretStr

from tests.hosts import TRACKER_BASE
from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import build_client
from ycli.yandex.tracker.client import TrackerClient


def test_build_passes_raw_args_and_does_not_read_env(api, monkeypatch):
    """build_client takes instances (not env) and wires the sub-clients.

    monkeypatch sets the env so Credentials() resolves; build_client must
    forward exactly those values (not silently re-read the env itself).
    """
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "o")
    creds = Credentials()
    cfg = AppConfig(http={"timeout_seconds": 12.0, "retries": 5})  # ty: ignore[invalid-argument-type]
    client = build_client(TrackerClient, creds, cfg)
    assert isinstance(client, TrackerClient)
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice"})
    client.me.get()
    assert api.calls[0].headers["Authorization"] == "OAuth t"
    assert api.calls[0].headers["X-Org-Id"] == "o"
    core = client.me._session
    assert core._client.timeout.read == 12.0
    assert core._attempts == 6  # the first try and 5 retries


def test_build_forwards_fractional_timeout(monkeypatch):
    """A fractional ``timeout_seconds`` reaches the client unrounded: 0.5 must not become 0."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    monkeypatch.setenv("YCLI__HTTP__TIMEOUT_SECONDS", "0.5")
    creds = Credentials()
    cfg = AppConfig()
    client = build_client(TrackerClient, creds, cfg)
    assert isinstance(client, TrackerClient)
    assert client.me._session._client.timeout.read == 0.5


def test_build_forwards_before_send_to_the_core_session(api, monkeypatch):
    """The hook reaches the session: it is called with the effect before the request goes out."""
    seen: list[tuple[str, str]] = []
    client = build_client(
        TrackerClient,
        Credentials(),
        AppConfig(),
        before_send=lambda effect, request: seen.append((effect, request.method)),
    )
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice"})
    client.me.get()
    assert seen == [("read", "GET")]


def test_an_iam_token_is_sent_as_a_bearer(api):
    api.add("GET", "https://api.tracker.yandex.net/v3/myself", json={"login": "ivan"})
    credentials = Credentials(oauth_token=None, iam_token=SecretStr("t1.x"), organization_id="o")
    with build_client(TrackerClient, credentials, AppConfig()) as client:
        client.me.get()
    assert api.calls[0].headers["Authorization"] == "Bearer t1.x"
    assert api.calls[0].headers["X-Org-Id"] == "o"
