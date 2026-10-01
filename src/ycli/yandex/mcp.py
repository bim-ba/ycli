"""Shared FastMCP tool annotations + the per-request client/config providers.

Providers run on every tool call (FastMCP ``Depends``), so a rotated token or an edited
``.env`` takes effect on the next call without restarting the server, and nothing is cached
at module level. Building a domain client costs a few milliseconds (TrackerClient ~9 ms),
negligible next to the HTTP round trip it serves.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import ClientFactory

if TYPE_CHECKING:
    from collections.abc import Callable

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


class AuthSource(Protocol):
    """Where a tool call's credentials come from.

    Kill-criterion: if MCP over HTTP (#108) ships without a second source (credentials taken
    from the request), fold this back into a plain ``Credentials()`` call.
    """

    def resolve(self) -> Credentials: ...


class EnvAuthSource:
    """The stdio server's source: the process environment and ``.env``, re-read per call."""

    def resolve(self) -> Credentials:
        return Credentials()  # ty: ignore[missing-argument]  # pydantic-settings reads the env


def app_config() -> AppConfig:
    """The app config for one tool call (read per call, like the credentials)."""
    return AppConfig()


def client_provider[T](
    client_cls: type[T], auth_source: AuthSource | None = None
) -> Callable[[], T]:
    """A zero-argument provider for ``Depends`` that builds ``client_cls`` for each call.

    Example:
        >>> forms_client = client_provider(FormsClient)  # doctest: +SKIP
        >>> forms_client().surveys.list(limit=1)  # doctest: +SKIP
    """
    source = auth_source or EnvAuthSource()

    def provide() -> T:
        return ClientFactory.build(client_cls, source.resolve(), app_config())  # ty: ignore[invalid-return-type]

    return provide
