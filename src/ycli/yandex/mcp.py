"""Shared FastMCP tool annotations + the cached per-domain client/config providers."""

from __future__ import annotations

from functools import cache

from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import ClientFactory

RO: dict[str, bool] = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": True}


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
