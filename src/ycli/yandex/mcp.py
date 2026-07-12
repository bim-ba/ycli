"""Shared FastMCP tool annotations + the cached per-domain client/config providers."""

from __future__ import annotations

from functools import cache

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
    def provider() -> T:
        return ClientFactory.build(client_cls, Credentials(), app_config())  # type: ignore[return-value]  # ty: ignore[missing-argument,invalid-return-type]

    return provider  # type: ignore[return-value]  # ty: ignore[invalid-return-type]
