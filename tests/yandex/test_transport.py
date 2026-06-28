"""TDD for the Yandex Transport — the single auth boundary.

Transport.session(*, oauth_token, organization_id, timeout_seconds, retries, base) is PURE:
it never reads os.environ. It returns a requests.Session with OAuth + a single canonical org
header (X-Org-Id; header names are case-insensitive per RFC 9110, so one casing serves
Wiki/Tracker/Forms), a urllib3 Retry adapter on idempotent methods only, and a default
timeout. Empty args raise. When base is supplied, that session is configured in place and
returned instead of a fresh one.
"""

import pytest
import requests
import responses

from ycli.yandex.transport import Transport


def test_session_sets_auth_and_org_headers():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    assert s.headers["Authorization"] == "OAuth t"
    assert s.headers["X-Org-Id"] == "o"


def test_session_applies_configured_timeout_and_retries():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=12.5, retries=7)
    adapter = s.get_adapter("https://example.com")
    assert adapter._timeout == 12.5
    assert adapter.max_retries.total == 7


def test_session_rejects_empty_credentials():
    with pytest.raises(ValueError, match="token"):
        Transport.session(oauth_token="", organization_id="o", timeout_seconds=30.0, retries=3)


def test_empty_org_raises():
    with pytest.raises(ValueError, match="organization_id"):
        Transport.session(oauth_token="t", organization_id="", timeout_seconds=30.0, retries=3)


def test_session_carries_auth_and_org_headers():
    s = Transport.session(oauth_token="tok", organization_id="org", timeout_seconds=30.0, retries=3)
    assert isinstance(s, requests.Session)
    assert s.headers["Authorization"] == "OAuth tok"
    assert s.headers["X-Org-Id"] == "org"


def test_session_mounts_retry_adapter_on_https():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    adapter = s.get_adapter("https://api.wiki.yandex.net/v1/pages")
    assert adapter.max_retries.total == 3
    assert 429 in adapter.max_retries.status_forcelist
    assert 500 in adapter.max_retries.status_forcelist


def test_post_not_retried_only_idempotent_methods():
    s = Transport.session(oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3)
    adapter = s.get_adapter("https://api.wiki.yandex.net/v1/pages")
    methods = adapter.max_retries.allowed_methods
    assert "POST" not in methods
    assert "GET" in methods


def test_session_does_not_read_environment(monkeypatch):
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "should-be-ignored")
    s = Transport.session(oauth_token="explicit", organization_id="o", timeout_seconds=30.0, retries=3)
    assert s.headers["Authorization"] == "OAuth explicit"


def test_timeout_adapter_injects_default_when_none(monkeypatch):
    # responses mounts its own adapter and bypasses _TimeoutAdapter.send, so unit-test send() directly.
    from ycli.yandex.transport import _TimeoutAdapter

    captured: dict[str, object] = {}

    def fake_send(self, request, **kwargs):
        captured.update(kwargs)
        return requests.Response()

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", fake_send)
    adapter = _TimeoutAdapter(timeout=12.5)
    prepared = requests.Request("GET", "https://example.com").prepare()

    adapter.send(prepared)
    assert captured["timeout"] == 12.5


def test_timeout_adapter_passes_explicit_timeout_through(monkeypatch):
    from ycli.yandex.transport import _TimeoutAdapter

    captured: dict[str, object] = {}

    def fake_send(self, request, **kwargs):
        captured.update(kwargs)
        return requests.Response()

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", fake_send)
    adapter = _TimeoutAdapter(timeout=12.5)
    prepared = requests.Request("GET", "https://example.com").prepare()

    adapter.send(prepared, timeout=3.0)
    assert captured["timeout"] == 3.0


from pathlib import Path


def test_no_hardcoded_uplink_timeout_in_clients():
    src = Path(__file__).resolve().parents[2] / "src" / "ycli" / "yandex"
    offenders = [str(p) for p in src.rglob("client.py") if "@uplink.timeout" in p.read_text()]
    assert not offenders, offenders


def test_session_configures_a_supplied_bare_base():
    from ycli.yandex.transport import _raise_typed, _TimeoutAdapter
    bare = requests.Session()
    out = Transport.session(oauth_token="t", organization_id="o", base=bare)
    assert out is bare  # configured in place, not replaced
    assert out.headers["Authorization"] == "OAuth t"
    assert out.headers["X-Org-Id"] == "o"
    assert _raise_typed in out.hooks["response"]
    assert isinstance(out.get_adapter("https://example.com"), _TimeoutAdapter)


@responses.activate
def test_client_honors_configured_timeout_not_hardcoded(monkeypatch):
    """Timeout from _TimeoutAdapter reaches the request; no per-method override interferes."""
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "tok")
    monkeypatch.setenv("YANDEX_ID_ORGANIZATION_ID", "org")
    monkeypatch.setenv("YCLI_TIMEOUT_SECONDS", "99")
    import requests.adapters
    from ycli.yandex.transport import _TimeoutAdapter
    from ycli.yandex.tracker.client import TrackerClient
    seen: dict = {}
    real_send = _TimeoutAdapter.send
    def spy(self, request, **kw):
        seen["incoming_timeout"] = kw.get("timeout")
        seen["adapter_timeout"] = self._timeout
        return real_send(self, request, **kw)
    monkeypatch.setattr(_TimeoutAdapter, "send", spy)
    responses.add(responses.GET, "https://api.tracker.yandex.net/v3/priorities", json=[], status=200)
    from ycli.yandex.tracker._deps import tracker_client
    tracker_client().priorities.list()
    assert seen["incoming_timeout"] is None, f"Expected None but got {seen['incoming_timeout']}"
    assert seen["adapter_timeout"] == 99.0, f"Expected 99.0 but got {seen['adapter_timeout']}"
