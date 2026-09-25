import asyncio
import contextlib
import json
import time

import httpx

from ycli.mcp import server
from ycli.yandex import mcp


async def install_userinfo(monkeypatch, handler):
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        timeout=mcp._USERINFO_TIMEOUT,
        follow_redirects=False,
    )
    monkeypatch.setattr(mcp, "_userinfo_client", client)
    monkeypatch.setattr(mcp, "_validation_shutting_down", False)
    return client


async def test_validation_fails_closed_while_shutdown_is_active(monkeypatch):
    monkeypatch.setattr(mcp, "_validation_shutting_down", True)
    assert await mcp.validate_identity_hub_token("shutdown-active") is None
    assert mcp._inflight_validations == {}
    assert mcp._validation_workers == set()


async def test_reset_cache_cancels_inflight_validation():
    future = asyncio.get_running_loop().create_future()
    task = asyncio.create_task(asyncio.sleep(10))
    validation = mcp.InflightValidation(future=future, task=task)
    mcp._inflight_validations["digest"] = validation
    mcp._validation_workers.add(task)
    await mcp.reset_validation_cache()
    await asyncio.sleep(0)
    assert task.cancelled()
    assert future.cancelled()
    assert mcp._inflight_validations == {}
    assert mcp._validation_workers == set()


async def test_start_replaces_existing_userinfo_client(monkeypatch):
    existing = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    monkeypatch.setattr(mcp, "_userinfo_client", existing)
    await mcp.start_userinfo_client()
    assert existing.is_closed
    assert mcp._userinfo_client is not None
    assert mcp._userinfo_client is not existing


async def test_fetch_without_started_client_fails_closed():
    await mcp.close_userinfo_client()
    assert await mcp._fetch_subject("no-client") is None


async def test_invalid_content_length_fails_closed(monkeypatch):
    async def handler(request):
        return httpx.Response(200, headers={"Content-Length": "invalid"}, content=b"{}")

    await install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token("invalid-length") is None


async def test_deadline_includes_semaphore_queue_and_never_enters_handler(monkeypatch):
    monkeypatch.setattr(mcp, "_USERINFO_DEADLINE", 0.1)
    monkeypatch.setattr(mcp, "_userinfo_gate", asyncio.Semaphore(1))
    calls: list[str] = []

    async def handler(request):
        calls.append(request.headers["Authorization"])
        return httpx.Response(200, json={"sub": "subject"})

    await install_userinfo(monkeypatch, handler)
    await mcp._userinfo_gate.acquire()
    started = time.monotonic()
    try:
        assert await mcp.validate_identity_hub_token("queued-token") is None
    finally:
        mcp._userinfo_gate.release()
    assert time.monotonic() - started < 1
    await asyncio.sleep(0)
    assert calls == []
    digest = mcp._token_digest("queued-token")
    assert digest not in mcp._validation_cache
    assert digest not in mcp._inflight_validations


async def test_same_digest_positive_singleflight(monkeypatch):
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.02)
        return httpx.Response(200, json={"sub": "subject"})

    await install_userinfo(monkeypatch, handler)
    results = await asyncio.gather(
        *(mcp.validate_identity_hub_token("same-positive") for _ in range(12))
    )
    assert results == ["subject"] * 12
    assert calls == 1
    assert mcp._inflight_validations == {}


async def test_same_digest_negative_singleflight(monkeypatch):
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.02)
        return httpx.Response(401)

    await install_userinfo(monkeypatch, handler)
    results = await asyncio.gather(
        *(mcp.validate_identity_hub_token("same-negative") for _ in range(12))
    )
    assert results == [None] * 12
    assert calls == 1
    assert mcp._inflight_validations == {}


async def test_waiter_cancellation_does_not_cancel_shared_validation(monkeypatch):
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        entered.set()
        await release.wait()
        return httpx.Response(200, json={"sub": "subject"})

    await install_userinfo(monkeypatch, handler)
    leader = asyncio.create_task(mcp.validate_identity_hub_token("cancel-one"))
    waiter = asyncio.create_task(mcp.validate_identity_hub_token("cancel-one"))
    await asyncio.wait_for(entered.wait(), timeout=2)
    leader.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await leader
    release.set()
    assert await asyncio.wait_for(waiter, timeout=2) == "subject"
    assert calls == 1
    assert mcp._inflight_validations == {}


async def test_cancelled_only_waiter_cleans_inflight(monkeypatch):
    entered = asyncio.Event()

    async def handler(request):
        entered.set()
        await asyncio.sleep(10)
        return httpx.Response(200, json={"sub": "never"})

    await install_userinfo(monkeypatch, handler)
    leader = asyncio.create_task(mcp.validate_identity_hub_token("leader-cancel"))
    await asyncio.wait_for(entered.wait(), timeout=2)
    leader.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await leader
    await asyncio.sleep(0)
    digest = mcp._token_digest("leader-cancel")
    assert digest not in mcp._validation_cache
    assert digest not in mcp._inflight_validations


async def test_shutdown_waits_for_blocked_worker_cancellation(monkeypatch):
    entered = asyncio.Event()
    cancelled = asyncio.Event()

    async def handler(request):
        entered.set()
        try:
            await asyncio.sleep(10)
        finally:
            cancelled.set()
        return httpx.Response(200, json={"sub": "never"})

    client = await install_userinfo(monkeypatch, handler)
    waiter = asyncio.create_task(mcp.validate_identity_hub_token("shutdown-blocked"))
    await asyncio.wait_for(entered.wait(), timeout=2)
    await asyncio.wait_for(mcp.close_userinfo_client(), timeout=2)
    assert cancelled.is_set()
    assert mcp._validation_cache == {}
    assert mcp._inflight_validations == {}
    assert client.is_closed
    with contextlib.suppress(asyncio.CancelledError):
        await asyncio.wait_for(waiter, timeout=2)


async def test_second_lifecycle_same_token_ignores_old_cancelled_worker(monkeypatch):
    entered = asyncio.Event()
    old_cancelled = asyncio.Event()
    old_release = asyncio.Event()

    async def old_handler(request):
        entered.set()
        try:
            await old_release.wait()
        finally:
            old_cancelled.set()
        return httpx.Response(401)

    old_client = await install_userinfo(monkeypatch, old_handler)
    old_waiter = asyncio.create_task(mcp.validate_identity_hub_token("same-lifecycle-token"))
    await asyncio.wait_for(entered.wait(), timeout=2)
    await asyncio.wait_for(mcp.close_userinfo_client(), timeout=2)
    assert old_cancelled.is_set()
    assert old_client.is_closed
    with contextlib.suppress(asyncio.CancelledError):
        await asyncio.wait_for(old_waiter, timeout=2)

    calls = 0

    async def fresh_handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"sub": "fresh-subject"})

    fresh_client = await install_userinfo(monkeypatch, fresh_handler)
    assert await mcp.validate_identity_hub_token("same-lifecycle-token") == "fresh-subject"
    assert calls == 1
    await asyncio.sleep(0)
    assert mcp._validation_cache[mcp._token_digest("same-lifecycle-token")][1] == "fresh-subject"
    assert mcp._inflight_validations == {}
    await mcp.close_userinfo_client()
    assert fresh_client.is_closed


async def test_content_length_oversize_short_circuits_body(monkeypatch):
    reads = 0

    async def stream_body():
        nonlocal reads
        reads += 1
        yield b"should-not-be-read"

    async def handler(request):
        return httpx.Response(
            200,
            headers={"Content-Length": str(mcp.MAX_USERINFO_BODY_BYTES + 1)},
            stream=httpx.AsyncByteStream(),
        )

    class CountingStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            async for chunk in stream_body():
                yield chunk

    async def proper_handler(request):
        return httpx.Response(
            200,
            headers={"Content-Length": str(mcp.MAX_USERINFO_BODY_BYTES + 1)},
            stream=CountingStream(),
        )

    await install_userinfo(monkeypatch, proper_handler)
    assert await mcp.validate_identity_hub_token("length-oversize") is None
    assert reads == 0


async def test_chunked_oversize_stops_at_bound(monkeypatch):
    yielded = 0

    class ChunkedStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            nonlocal yielded
            for _ in range(1000):
                yielded += 1
                yield b"x" * 1024

    async def handler(request):
        return httpx.Response(200, stream=ChunkedStream())

    await install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token("chunked-oversize") is None
    assert yielded <= mcp.MAX_USERINFO_BODY_BYTES // 1024 + 1


async def test_streamed_normal_json_works(monkeypatch):
    payload = json.dumps({"sub": "stream-subject"}).encode()

    class JSONStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield payload[:5]
            yield payload[5:]

    async def handler(request):
        return httpx.Response(200, stream=JSONStream())

    await install_userinfo(monkeypatch, handler)
    assert await mcp.validate_identity_hub_token("stream-normal") == "stream-subject"


async def test_http_lifespan_closes_client_and_second_start_is_fresh(monkeypatch):
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud-org")
    server.configure_http_auth(mcp.YandexBearerVerifier(lambda token: _subject(token)))
    app = server.mcp.http_app(stateless_http=True, json_response=True)
    async with app.router.lifespan_context(app):
        first = mcp._userinfo_client
        assert first is not None and not first.is_closed
    assert first.is_closed
    assert mcp._userinfo_client is None

    server.configure_http_auth(mcp.YandexBearerVerifier(lambda token: _subject(token)))
    app = server.mcp.http_app(stateless_http=True, json_response=True)
    async with app.router.lifespan_context(app):
        second = mcp._userinfo_client
        assert second is not None and not second.is_closed
        assert second is not first
    assert second.is_closed
    assert mcp._userinfo_client is None


async def _subject(token):
    return f"subject-{token}"


async def test_detached_worker_is_joined_before_new_lifecycle(monkeypatch):
    token = "combined-race-token"
    digest = mcp._token_digest(token)
    entered = asyncio.Event()
    cancellation_seen = asyncio.Event()
    cleanup_release = asyncio.Event()
    cleanup_finished = asyncio.Event()

    async def resistant_handler(request):
        entered.set()
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError as cancellation:
            cancellation_seen.set()
            while not cleanup_release.is_set():
                current = asyncio.current_task()
                if current is not None:
                    current.uncancel()
                try:
                    await cleanup_release.wait()
                except asyncio.CancelledError:
                    continue
            cleanup_finished.set()
            raise cancellation
        return httpx.Response(401)

    old_client = await install_userinfo(monkeypatch, resistant_handler)
    sole_waiter = asyncio.create_task(mcp.validate_identity_hub_token(token))
    await asyncio.wait_for(entered.wait(), timeout=2)
    sole_waiter.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await sole_waiter
    await asyncio.wait_for(cancellation_seen.wait(), timeout=2)
    assert digest not in mcp._inflight_validations
    assert mcp._validation_workers

    shutdown = asyncio.create_task(mcp.close_userinfo_client())
    await asyncio.sleep(0.05)
    assert not shutdown.done()
    assert not cleanup_finished.is_set()
    cleanup_release.set()
    await asyncio.wait_for(shutdown, timeout=2)
    assert cleanup_finished.is_set()
    assert old_client.is_closed
    assert mcp._validation_workers == set()
    assert mcp._inflight_validations == {}
    assert digest not in mcp._validation_cache

    calls = 0

    async def fresh_handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(200, json={"sub": "fresh-race-subject"})

    fresh_client = await install_userinfo(monkeypatch, fresh_handler)
    assert await mcp.validate_identity_hub_token(token) == "fresh-race-subject"
    assert calls == 1
    assert mcp._validation_cache[digest][1] == "fresh-race-subject"
    await asyncio.sleep(0)
    assert mcp._validation_cache[digest][1] == "fresh-race-subject"
    assert mcp._validation_workers == set()
    await mcp.close_userinfo_client()
    assert fresh_client.is_closed


async def test_retired_worker_cannot_overwrite_same_lifecycle_fresh_result(monkeypatch):
    token = "same-lifecycle-retired-token"
    digest = mcp._token_digest(token)
    first_entered = asyncio.Event()
    first_cancelled = asyncio.Event()
    release_first = asyncio.Event()
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            first_entered.set()
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                first_cancelled.set()
                while not release_first.is_set():
                    current = asyncio.current_task()
                    if current is not None:
                        current.uncancel()
                    try:
                        await release_first.wait()
                    except asyncio.CancelledError:
                        continue
                return httpx.Response(200, json={"sub": "stale-subject"})
        return httpx.Response(200, json={"sub": "fresh-subject"})

    await install_userinfo(monkeypatch, handler)
    sole_waiter = asyncio.create_task(mcp.validate_identity_hub_token(token))
    await asyncio.wait_for(first_entered.wait(), timeout=2)
    sole_waiter.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await sole_waiter
    await asyncio.wait_for(first_cancelled.wait(), timeout=2)
    assert digest not in mcp._inflight_validations
    assert len(mcp._validation_workers) == 1

    assert (
        await asyncio.wait_for(mcp.validate_identity_hub_token(token), timeout=2) == "fresh-subject"
    )
    assert calls == 2
    assert mcp._validation_cache[digest][1] == "fresh-subject"

    release_first.set()
    for _ in range(100):
        if not mcp._validation_workers:
            break
        await asyncio.sleep(0.01)
    assert mcp._validation_workers == set()
    assert mcp._inflight_validations == {}
    assert mcp._validation_cache[digest][1] == "fresh-subject"
