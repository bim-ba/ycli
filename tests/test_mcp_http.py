import asyncio
import contextlib
import json
import threading

import httpx
import pytest

from ycli.mcp import server
from ycli.yandex import mcp as yandex_mcp


def make_app(monkeypatch, rejected=frozenset()):
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud-org")

    async def validate(token):
        if token in rejected:
            return None
        return f"subject-{token}"

    server.configure_http_auth(yandex_mcp.YandexBearerVerifier(validate))
    return server.mcp.http_app(stateless_http=True, json_response=True)


def request(method: str, request_id: int = 1) -> dict[str, object]:
    params: dict[str, object] = {}
    if method == "initialize":
        params = {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        }
    elif method == "tools/call":
        params = {"name": "tracker_priorities_list", "arguments": {}}
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}


async def post(app, method, authorization=None):
    headers = {"Accept": "application/json, text/event-stream"}
    if authorization is not None:
        headers["Authorization"] = authorization
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        return await client.post("/mcp", headers=headers, json=request(method))


def test_loguru_sink_positive_control(loguru_sink):
    """Positive control: the capture fixture really records loguru output."""
    from loguru import logger

    logger.info("capture-control-sentinel")
    assert "capture-control-sentinel" in loguru_sink.getvalue()


def test_caplog_does_not_capture_loguru(caplog):
    """Documents why secrecy assertions must not rely on caplog."""
    from loguru import logger

    logger.info("caplog-control-sentinel")
    assert "caplog-control-sentinel" not in caplog.text


@pytest.mark.parametrize("method", ["initialize", "tools/list", "ping", "tools/call"])
async def test_http_boundary_rejects_missing_bearer(monkeypatch, method):
    response = await post(make_app(monkeypatch), method)
    assert response.status_code == 401


async def test_tool_call_fails_closed_when_mode_flag_unset(monkeypatch):
    app = make_app(monkeypatch)
    yandex_mcp.set_request_auth(None)
    built: list[object] = []
    monkeypatch.setattr(
        yandex_mcp,
        "Credentials",
        lambda *a, **k: built.append(object()),
    )
    async with app.router.lifespan_context(app):
        response = await post(app, "tools/call", "Bearer mode-unset-sentinel")
    assert response.status_code == 200
    assert "error" in response.text.lower()
    assert built == []
    assert "mode-unset-sentinel" not in response.text


@pytest.mark.parametrize(
    "authorization",
    [
        "Basic token",
        "Bearer",
        "Bearer  token",
        "Bearer token token",
        "Bearer token,other",
        "Bearer token\tother",
        "Bearer token=middle",
    ],
)
async def test_http_boundary_rejects_malformed_bearer(monkeypatch, authorization, loguru_sink):
    response = await post(make_app(monkeypatch), "initialize", authorization)
    assert response.status_code == 401
    assert authorization not in response.text
    assert authorization not in loguru_sink.getvalue()


async def test_userinfo_rejected_token_is_unauthorized_and_redacted(monkeypatch, loguru_sink):
    token = "userinfo-rejected-sentinel"
    response = await post(make_app(monkeypatch, {token}), "initialize", f"Bearer {token}")
    assert response.status_code == 401
    assert token not in response.text
    assert token not in loguru_sink.getvalue()


async def test_http_boundary_accepts_valid_bearer(monkeypatch):
    app = make_app(monkeypatch)
    async with app.router.lifespan_context(app):
        response = await post(app, "initialize", "Bearer valid-token_1+/==")
    assert response.status_code == 200
    assert response.json()["result"]["serverInfo"]["name"] == "yandex"


async def test_overlapping_tool_requests_keep_tokens_isolated(monkeypatch):
    app = make_app(monkeypatch)
    barrier = threading.Barrier(2)
    seen: list[tuple[str, str]] = []

    def list_priorities(self):
        barrier.wait(timeout=2)
        seen.append(
            (
                self._session.headers["Authorization"],
                self._session.headers["X-Cloud-Org-Id"],
            )
        )
        return []

    monkeypatch.setattr(
        "ycli.yandex.tracker.priorities.client.PrioritiesClient.list", list_priorities
    )
    async with app.router.lifespan_context(app):
        first, second = await asyncio.gather(
            post(app, "tools/call", "Bearer first-token"),
            post(app, "tools/call", "Bearer second-token"),
        )
    assert first.status_code == second.status_code == 200
    assert sorted(seen) == [
        ("Bearer first-token", "cloud-org"),
        ("Bearer second-token", "cloud-org"),
    ]


async def test_failed_request_does_not_contaminate_next_request(monkeypatch, loguru_sink):
    app = make_app(monkeypatch)
    calls = 0

    def list_priorities(self):
        nonlocal calls
        calls += 1
        authorization = self._session.headers["Authorization"]
        if calls == 1:
            raise RuntimeError("mock upstream failure")
        from ycli.yandex.tracker.priorities.models import Priority

        return [Priority(key=authorization)]

    monkeypatch.setattr(
        "ycli.yandex.tracker.priorities.client.PrioritiesClient.list", list_priorities
    )
    async with app.router.lifespan_context(app):
        failed = await post(app, "tools/call", "Bearer failed-sentinel")
        succeeded = await post(app, "tools/call", "Bearer next-sentinel")
    assert failed.status_code == succeeded.status_code == 200
    assert "failed-sentinel" not in failed.text
    assert "failed-sentinel" not in loguru_sink.getvalue()
    assert "Bearer next-sentinel" in succeeded.text
    assert "failed-sentinel" not in succeeded.text


async def test_cancelled_request_does_not_contaminate_next_request(monkeypatch, loguru_sink):
    app = make_app(monkeypatch)
    started = threading.Event()
    release = threading.Event()
    seen: list[str] = []

    def list_priorities(self):
        authorization = self._session.headers["Authorization"]
        seen.append(authorization)
        if authorization == "Bearer cancelled-sentinel":
            started.set()
            assert release.wait(timeout=2)
        return []

    monkeypatch.setattr(
        "ycli.yandex.tracker.priorities.client.PrioritiesClient.list", list_priorities
    )
    async with app.router.lifespan_context(app):
        cancelled = asyncio.create_task(post(app, "tools/call", "Bearer cancelled-sentinel"))
        assert await asyncio.wait_for(asyncio.to_thread(started.wait, 2), timeout=3)
        cancelled.cancel()
        release.set()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.wait_for(cancelled, timeout=3)
        succeeded = await asyncio.wait_for(
            post(app, "tools/call", "Bearer after-cancel-sentinel"), timeout=3
        )
    assert succeeded.status_code == 200
    assert seen == ["Bearer cancelled-sentinel", "Bearer after-cancel-sentinel"]
    assert "cancelled-sentinel" not in succeeded.text
    assert "cancelled-sentinel" not in loguru_sink.getvalue()


async def test_asgi_disconnect_does_not_leak_credentials(monkeypatch, loguru_sink):
    app = make_app(monkeypatch)
    seen: list[str] = []

    def list_priorities(self):
        seen.append(self._session.headers["Authorization"])
        return []

    monkeypatch.setattr(
        "ycli.yandex.tracker.priorities.client.PrioritiesClient.list", list_priorities
    )
    body = json.dumps(request("tools/call")).encode()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/mcp",
        "raw_path": b"/mcp",
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"host", b"test"),
            (b"content-type", b"application/json"),
            (b"accept", b"application/json, text/event-stream"),
            (b"authorization", b"Bearer disconnect-sentinel"),
            (b"content-length", str(len(body)).encode()),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("test", 80),
    }
    events = [
        {"type": "http.request", "body": body, "more_body": False},
        {"type": "http.disconnect"},
    ]

    async def receive():
        if events:
            return events.pop(0)
        return {"type": "http.disconnect"}

    async def send(message):
        return None

    async with app.router.lifespan_context(app):
        with contextlib.suppress(Exception):
            await asyncio.wait_for(app(scope, receive, send), timeout=3)
        succeeded = await asyncio.wait_for(
            post(app, "tools/call", "Bearer after-disconnect-sentinel"), timeout=3
        )
    assert succeeded.status_code == 200
    assert seen[-1] == "Bearer after-disconnect-sentinel"
    assert "disconnect-sentinel" not in succeeded.text
    assert "disconnect-sentinel" not in loguru_sink.getvalue()
