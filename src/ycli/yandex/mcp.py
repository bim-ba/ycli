"""Shared FastMCP tool annotations + the cached per-domain client/config providers."""

from __future__ import annotations

import asyncio
import hashlib
import re
import secrets
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import cache

import httpx
from fastmcp.exceptions import AuthorizationError
from fastmcp.server.auth import AccessToken, TokenVerifier
from fastmcp.server.dependencies import get_access_token

from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import ClientFactory

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}
# Write-tool annotation sets (ARCH-3 annotation honesty). The MCP-spec default for an
# unannotated tool is destructiveHint=true, so every write declares its hints explicitly:
# WRITE = additive create-style call; WRITE_IDEMPOTENT = PATCH-style edit (safe to repeat);
# DESTRUCTIVE = delete/clear/abort (removes data irreversibly).
WRITE: dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": True,
}
WRITE_IDEMPOTENT: dict[str, bool] = {**WRITE, "idempotentHint": True}
DESTRUCTIVE: dict[str, bool] = {**WRITE, "destructiveHint": True}
# Tag carried by every write tool — `ycli mcp start --read-only` disables it wholesale.
WRITE_TAG = "write"
_B64TOKEN = re.compile(r"[A-Za-z0-9\-._~+/]+=*")
MAX_BEARER_LENGTH = 8192
MAX_USERINFO_BODY_BYTES = 64 * 1024

UserInfoValidator = Callable[[str], Awaitable[str | None]]
_USERINFO_URL = "https://auth.yandex.cloud/oauth/userinfo"
_USERINFO_TIMEOUT = httpx.Timeout(connect=2.0, read=3.0, write=3.0, pool=2.0)
_USERINFO_DEADLINE = 6.0
_USERINFO_CONCURRENCY = 16
_POSITIVE_TTL = 60.0
_NEGATIVE_TTL = 5.0
_CACHE_MAX_ENTRIES = 1024
_CACHE_SALT = secrets.token_bytes(32)

_userinfo_client: httpx.AsyncClient | None = None
_userinfo_gate = asyncio.Semaphore(_USERINFO_CONCURRENCY)
_validation_cache: OrderedDict[str, tuple[float, str | None]] = OrderedDict()


@dataclass
class InflightValidation:
    """A digest-keyed shared validation without retaining the raw token."""

    future: asyncio.Future[str | None]
    task: asyncio.Task[None] | None = None
    waiters: int = 0


_inflight_validations: dict[str, InflightValidation] = {}
_validation_workers: set[asyncio.Task[None]] = set()
_validation_generation = 0
_validation_shutting_down = False


def _token_digest(token: str) -> str:
    """Return a salted SHA-256 digest so no cache key can reveal a caller token."""
    return hashlib.sha256(_CACHE_SALT + token.encode()).hexdigest()


async def reset_validation_cache() -> None:
    """Prevent new work, then cancel and join every lifecycle-owned worker."""
    global _validation_generation, _validation_shutting_down
    _validation_shutting_down = True
    _validation_generation += 1
    current = asyncio.current_task()
    for validation in list(_inflight_validations.values()):
        validation.future.cancel()
    while True:
        tasks = [task for task in _validation_workers if task is not current and not task.done()]
        if not tasks:
            break
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    _inflight_validations.clear()
    _validation_workers.clear()
    _validation_cache.clear()


async def start_userinfo_client() -> None:
    """Create the pooled userinfo client for one clean HTTP server lifespan."""
    global _userinfo_client, _userinfo_gate, _validation_shutting_down
    await reset_validation_cache()
    if _userinfo_client is not None:
        await _userinfo_client.aclose()
    _userinfo_client = httpx.AsyncClient(timeout=_USERINFO_TIMEOUT, follow_redirects=False)
    _userinfo_gate = asyncio.Semaphore(_USERINFO_CONCURRENCY)
    _validation_shutting_down = False


async def close_userinfo_client() -> None:
    """Join validation workers, then close the pooled client at HTTP shutdown."""
    global _userinfo_client
    client = _userinfo_client
    _userinfo_client = None
    await reset_validation_cache()
    if client is not None:
        await client.aclose()


def _cache_get(digest: str, now: float) -> tuple[bool, str | None]:
    entry = _validation_cache.get(digest)
    if entry is None:
        return False, None
    expires_at, subject = entry
    if expires_at <= now:
        del _validation_cache[digest]
        return False, None
    _validation_cache.move_to_end(digest)
    return True, subject


def _cache_put(digest: str, subject: str | None, now: float) -> None:
    ttl = _POSITIVE_TTL if subject is not None else _NEGATIVE_TTL
    _validation_cache[digest] = (now + ttl, subject)
    _validation_cache.move_to_end(digest)
    while len(_validation_cache) > _CACHE_MAX_ENTRIES:
        _validation_cache.popitem(last=False)


async def _fetch_subject(token: str) -> str | None:
    client = _userinfo_client
    if client is None:
        return None
    async with client.stream(
        "GET",
        _USERINFO_URL,
        headers={"Authorization": f"Bearer {token}"},
    ) as response:
        if not response.is_success:
            return None
        content_length = response.headers.get("Content-Length")
        if content_length is not None:
            try:
                if int(content_length) > MAX_USERINFO_BODY_BYTES:
                    return None
            except ValueError:
                return None
        body_bytes = bytearray()
        async for chunk in response.aiter_bytes():
            remaining = MAX_USERINFO_BODY_BYTES + 1 - len(body_bytes)
            body_bytes.extend(chunk[:remaining])
            if len(body_bytes) > MAX_USERINFO_BODY_BYTES:
                return None
        body = httpx.Response(200, content=bytes(body_bytes)).json()
    if not isinstance(body, dict):
        return None
    subject = body.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        return None
    return subject


async def _perform_validation(
    token: str,
    digest: str,
    validation: InflightValidation,
    generation: int,
) -> None:
    try:
        try:
            async with _userinfo_gate:
                subject = await _fetch_subject(token)
        except asyncio.CancelledError:
            raise
        except (httpx.HTTPError, ValueError):
            subject = None
        if (
            generation == _validation_generation
            and not _validation_shutting_down
            and _inflight_validations.get(digest) is validation
        ):
            _cache_put(digest, subject, time.monotonic())
            if not validation.future.done():
                validation.future.set_result(subject)
    finally:
        if _inflight_validations.get(digest) is validation:
            del _inflight_validations[digest]


def _worker_done(task: asyncio.Task[None]) -> None:
    """Release lifecycle ownership and consume every worker outcome."""
    _validation_workers.discard(task)
    if not task.cancelled():
        task.exception()


async def validate_identity_hub_token(token: str) -> str | None:
    """Validate an Identity Hub token within one queue-plus-network deadline."""

    async def validate() -> str | None:
        if _validation_shutting_down:
            return None
        digest = _token_digest(token)
        cached, subject = _cache_get(digest, time.monotonic())
        if cached:
            return subject
        validation = _inflight_validations.get(digest)
        if validation is None:
            validation = InflightValidation(asyncio.get_running_loop().create_future())
            _inflight_validations[digest] = validation
            validation.task = asyncio.create_task(
                _perform_validation(token, digest, validation, _validation_generation)
            )
            _validation_workers.add(validation.task)
            validation.task.add_done_callback(_worker_done)
        validation.waiters += 1
        try:
            return await asyncio.shield(validation.future)
        finally:
            validation.waiters -= 1
            if validation.waiters == 0 and not validation.future.done():
                if validation.task is not None:
                    validation.task.cancel()
                if _inflight_validations.get(digest) is validation:
                    del _inflight_validations[digest]

    try:
        async with asyncio.timeout(_USERINFO_DEADLINE):
            return await validate()
    except TimeoutError:
        return None


class YandexBearerVerifier(TokenVerifier):
    """Validate Identity Hub OAuth access tokens through Yandex userinfo."""

    def __init__(self, validator: UserInfoValidator = validate_identity_hub_token) -> None:
        super().__init__()
        self._validator = validator

    async def verify_token(self, token: str) -> AccessToken | None:
        if len(token) > MAX_BEARER_LENGTH or not _B64TOKEN.fullmatch(token):
            return None
        subject = await self._validator(token)
        if subject is None:
            return None
        return AccessToken(
            token=token,
            client_id="yandex-identity-hub",
            scopes=[],
            subject=subject,
            claims={"sub": subject},
        )


_request_auth: RequestAuth | None = None


class RequestAuth:
    """Process-level request-auth state resolved once at HTTP startup."""

    def __init__(self, cloud_organization_id: str) -> None:
        self.cloud_organization_id = cloud_organization_id

    def credentials(self) -> Credentials:
        access_token = get_access_token()
        if access_token is None:
            raise AuthorizationError("authenticated access token is required")
        return Credentials.model_construct(
            oauth_token=None,
            organization_id=None,
            iam_token=access_token.token,
            cloud_organization_id=self.cloud_organization_id,
            service_account_key_id=None,
            service_account_id=None,
            service_account_private_key=None,
        )


def set_request_auth(request_auth: RequestAuth | None) -> None:
    """Install (or clear) the process-level request-auth mode."""
    global _request_auth
    _request_auth = request_auth


def get_request_auth() -> RequestAuth | None:
    """Return the installed process-level request-auth mode."""
    return _request_auth


def http_auth_installed() -> bool:
    """True when the MCP HTTP endpoint is protected by a token verifier."""
    from ycli.mcp.server import mcp as root_mcp

    return root_mcp.auth is not None


def request_credentials() -> Credentials:
    """Resolve credentials only from FastMCP's verifier-approved access token."""
    request_auth = _request_auth
    if request_auth is None:
        raise AuthorizationError("request-auth mode is not active")
    return request_auth.credentials()


def credentials() -> Credentials:
    """Return request credentials in HTTP mode; never fall back when auth is installed."""
    if _request_auth is not None:
        return _request_auth.credentials()
    if http_auth_installed():
        raise AuthorizationError("request-auth mode is not active")
    return Credentials()


class CachedProvider[T]:
    """Typed zero-arg provider wrapping ``functools.cache`` — exposes ``cache_clear()``."""

    def __call__(self) -> T: ...  # ty: ignore[empty-body]

    def cache_clear(self) -> None: ...


@cache
def app_config() -> AppConfig:
    """Build (once) the process-wide app config for MCP tools."""
    return AppConfig()


def make_cached_client[T](client_cls: type[T]) -> CachedProvider[T]:
    """Return a ``@cache``d zero-arg provider building ``client_cls`` from the env."""

    @cache
    def cached_provider() -> T:
        return ClientFactory.build(client_cls, Credentials(), app_config())

    def provider() -> T:
        if _request_auth is not None or http_auth_installed():
            return ClientFactory.build(client_cls, credentials(), app_config())
        return cached_provider()

    provider.cache_clear = cached_provider.cache_clear  # ty: ignore[unresolved-attribute]
    return provider  # ty: ignore[invalid-return-type]
