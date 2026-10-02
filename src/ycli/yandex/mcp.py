"""Shared FastMCP tool annotations + the per-request client/config providers.

Providers run on every tool call (FastMCP ``Depends``), so a rotated token or an edited
``.env`` takes effect on the next call without restarting the server, and nothing is cached
at module level. Building a domain client costs a few milliseconds (TrackerClient ~9 ms),
negligible next to the HTTP round trip it serves.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Protocol

from ycli.settings import AppConfig, Credentials
from ycli.yandex.factory import build_client

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from contextlib import AbstractContextManager

    from ycli.yandex.base import DomainClient

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
# The tail of every listing tool's `limit` description. It names the setting, not its value,
# so the text stays true when HTTPConfig.max_items or the environment changes the cap.
LIMIT_CAP = "0 means the configured cap (YCLI__HTTP__MAX_ITEMS)."


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


def client_provider[C: DomainClient](
    client_cls: type[C], auth_source: AuthSource | None = None
) -> Callable[[], AbstractContextManager[C]]:
    """A zero-argument provider for ``Depends`` that builds ``client_cls`` for each call.

    ``Depends`` enters the context manager before the tool runs and exits it after, so the
    client's connection pools close when the call ends.

    Example:
        >>> forms_client = client_provider(FormsClient)  # doctest: +SKIP
        >>> with forms_client() as client:  # doctest: +SKIP
        ...     client.surveys.list(limit=1)
    """
    source = auth_source or EnvAuthSource()

    @contextmanager
    def provide() -> Iterator[C]:
        with build_client(client_cls, source.resolve(), app_config()) as client:
            yield client

    return provide
