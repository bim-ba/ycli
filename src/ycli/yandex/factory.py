"""The single client-construction site — maps app config + credentials to raw client args.

Env-free by design (ARCH-7/8): callers at the composition roots (AppContext, the MCP
``dependencies`` providers) read the environment and hand instances here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.settings import AppConfig, Credentials


class ClientFactory:
    """Builds a domain client from credentials + app config — no environment access."""

    @staticmethod
    def build[T](client_cls: type[T], credentials: Credentials, config: AppConfig) -> T:
        """Construct ``client_cls`` from ``credentials`` + ``config`` — never reads the env."""
        return client_cls(
            oauth_token=credentials.oauth_token,
            iam_token=credentials.iam_token,
            service_account=credentials.service_account,
            organization_id=credentials.organization_id,
            cloud_organization_id=credentials.cloud_organization_id,
            timeout_seconds=int(config.timeout_seconds),
            retries=config.retries,
        )
