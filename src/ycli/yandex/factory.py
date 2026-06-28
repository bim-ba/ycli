"""The single client-construction site — maps app config + credentials to raw client args.

Env-free by design (ARCH-7/8): callers at the composition roots (AppContext, the MCP
``_deps`` providers) read the environment and hand instances here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.settings import AppConfig, Credentials


class ClientFactory:
    """Builds a domain client from credentials + app config — no environment access."""

    @staticmethod
    def build(client_cls: type, credentials: Credentials, config: AppConfig) -> object:
        """Construct ``client_cls`` from ``credentials`` + ``config`` — never reads the env."""
        return client_cls(
            oauth_token=credentials.oauth_token,
            organization_id=credentials.organization_id,
            timeout_seconds=int(config.timeout_seconds),
            retries=config.retries,
        )
