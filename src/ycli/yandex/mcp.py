"""Shared FastMCP tool annotations + the per-request client/config providers.

Providers run on every tool call (FastMCP ``Depends``), so a rotated token or an edited
``.env`` takes effect on the next call without restarting the server, and nothing is cached
at module level. Building a domain client costs a few milliseconds (TrackerClient ~9 ms),
negligible next to the HTTP round trip it serves.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_access_token, get_http_request
from pydantic import SecretStr, ValidationError

from ycli.settings import AppConfig, Credentials, MCPHTTPConfig, missing_credentials
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


def caller_credentials() -> Credentials:
    """The credentials of one tool call: the caller's own Yandex token over HTTP, else the env.

    Over HTTP the server's OAuth layer has already signed the caller in through Yandex ID and
    holds their Yandex token (the MCP client only ever holds the server's own token, so nothing
    the client sends is passed on). The organization is the server's configured one. An HTTP
    call without a signed-in caller is refused: it never falls back to the environment's token.
    Over stdio the process environment and ``.env`` are read, per call.

    FastMCP hides any other exception behind "Failed to resolve dependency 'client'", which
    tells an agent nothing, so every failure here is a ``ToolError`` naming what is missing.
    """
    caller = get_access_token()
    if caller is not None:
        # The organization the server checked at start (MCPHTTPConfig), so both agree.
        organization_id = MCPHTTPConfig().organization_id  # ty: ignore[missing-argument]
        # The caller's own token only: an IAM token in the server's environment is not theirs.
        return Credentials(
            oauth_token=SecretStr(caller.token), iam_token=None, organization_id=organization_id
        )
    if _over_http():
        raise ToolError("Not signed in: this HTTP request carries no authenticated caller.")
    try:
        return Credentials()  # ty: ignore[missing-argument]  # pydantic-settings reads the env
    except ValidationError as exc:
        missing = missing_credentials(exc)
        if not missing:
            if exc.title != Credentials.__name__:
                raise
            # Two tokens at once: the error says which.
            raise ToolError(f"Invalid configuration: {exc.errors()[0]['msg']}") from exc
        raise ToolError(
            f"Not signed in — {', '.join(missing)} "
            f"{'are' if len(missing) > 1 else 'is'} not set. Set them in the environment the "
            "MCP server runs in (or its .env), or run `ycli auth login` to obtain a token."
        ) from exc


def _over_http() -> bool:
    """Whether the current tool call arrived over HTTP (``False`` over stdio)."""
    try:
        get_http_request()
    except RuntimeError:
        return False
    return True


def app_config() -> AppConfig:
    """The app config for one tool call (read per call, like the credentials)."""
    return AppConfig()


def client_provider[C: DomainClient](
    client_cls: type[C],
) -> Callable[[], AbstractContextManager[C]]:
    """A zero-argument provider for ``Depends`` that builds ``client_cls`` for each call.

    ``Depends`` enters the context manager before the tool runs and exits it after, so the
    client's connection pools close when the call ends.

    Examples:
        >>> from unittest.mock import patch
        >>> from ycli.settings import Credentials
        >>> from ycli.yandex.forms.client import FormsClient
        >>> forms_client = client_provider(FormsClient)
        >>> credentials = Credentials(oauth_token="token", organization_id="org")
        >>> with patch("ycli.yandex.mcp.caller_credentials", return_value=credentials):
        ...     with forms_client() as client:
        ...         [survey.id for survey in client.surveys.list(limit=500).root]
        ['686d0a1b2c3d4e5f00000001']
    """

    @contextmanager
    def provide() -> Iterator[C]:
        with build_client(client_cls, caller_credentials(), app_config()) as client:
            yield client

    return provide
