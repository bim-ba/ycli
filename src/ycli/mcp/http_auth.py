"""Sign-in for the MCP server over HTTP: fastmcp's ``OAuthProxy`` in front of Yandex ID.

The MCP authorization spec forbids passing the client's token through to an upstream API, and
Yandex ID has no dynamic client registration, so the server is the OAuth client of Yandex: an
MCP client registers with the server and signs the user in through Yandex ID, then holds only a
token the server issued. The user's Yandex token stays on the server, and
:func:`ycli.yandex.mcp.caller_credentials` hands it to each tool call.

A Yandex token is accepted only if Yandex ID says it was issued to this server's own Yandex
OAuth app (``client_id``), which binds it to this server.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastmcp.server.auth import AccessToken, OAuthProxy, TokenVerifier
from fastmcp.utilities.token_cache import TokenCache
from pydantic import SecretStr

from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.session import connect_async
from ycli.yandex.errors import YandexError
from ycli.yandex.status.client import OAuthClient
from ycli.yandex.status.token_client import GET_IDENTITY, YANDEX_ID

if TYPE_CHECKING:
    from ycli.settings import HTTPConfig, MCPHTTPConfig

logger = logging.getLogger("ycli.mcp")

# Where Yandex redirects back after sign-in; register ``<base_url>/auth/callback`` in the app.
CALLBACK_PATH = "/auth/callback"


class YandexTokenVerifier(TokenVerifier):
    """Accepts a Yandex OAuth token that Yandex ID says was issued to ``client_id``.

    A token for another app, a revoked or an unknown one gives ``None`` (the request is
    refused); a verified token is remembered for ``cache_seconds``.
    """

    def __init__(self, *, client_id: str, http: HTTPConfig, cache_seconds: int) -> None:
        super().__init__()
        self._client_id = client_id
        self._http = http
        self._cache = TokenCache(ttl_seconds=cache_seconds)

    async def verify_token(self, token: str) -> AccessToken | None:
        """The access token when Yandex ID issued ``token`` to this app, else ``None``."""
        cached, access = self._cache.get(token)
        if cached:
            return access
        session = connect_async(YANDEX_ID, auth=OAuthTokenAuth(SecretStr(token)), http=self._http)
        try:
            identity = await session.send(GET_IDENTITY)
        except YandexError as exc:
            logger.info("refused a Yandex token: %s", exc)
            return None
        finally:
            await session.aclose()
        if identity.client_id != self._client_id:
            logger.info("refused a Yandex token issued to another OAuth app")
            return None
        access = AccessToken(
            token=token,
            client_id=self._client_id,
            scopes=[],
            subject=identity.id,
            claims={"login": identity.login},
        )
        self._cache.set(token, access)
        return access


def yandex_oauth(
    server: MCPHTTPConfig, app_id: str, app_secret: SecretStr, http: HTTPConfig
) -> OAuthProxy:
    """The ``OAuthProxy`` that signs MCP clients in through the Yandex OAuth app ``app_id``.

    The ``resource`` parameter is not forwarded: Yandex does not know it, and the server's own
    token already carries its audience.
    """
    return OAuthProxy(
        upstream_authorization_endpoint=f"{OAuthClient.OAUTH_BASE_URL}/authorize",
        upstream_token_endpoint=f"{OAuthClient.OAUTH_BASE_URL}/token",
        upstream_client_id=app_id,
        upstream_client_secret=app_secret.get_secret_value(),
        token_verifier=YandexTokenVerifier(
            client_id=app_id, http=http, cache_seconds=server.token_cache_seconds
        ),
        base_url=str(server.base_url),
        redirect_path=CALLBACK_PATH,
        forward_resource=False,
        jwt_signing_key=(
            server.jwt_signing_key.get_secret_value() if server.jwt_signing_key else None
        ),
    )
