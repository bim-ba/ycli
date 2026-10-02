"""The single client-construction site — maps app config + credentials to raw client args.

Env-free by design (ARCH-5, ARCH-7): callers at the composition roots (AppContext, the MCP
``dependencies`` providers) read the environment and hand instances here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.settings import AppConfig, Credentials
    from ycli.yandex.base import DomainClient


def build_client[C: DomainClient](
    client_cls: type[C], credentials: Credentials, config: AppConfig
) -> C:
    """Construct ``client_cls`` from ``credentials`` + ``config`` — never reads the env.

    Example:
        >>> build_client(TrackerClient, Credentials(), AppConfig()).issues  # doctest: +SKIP
    """
    return client_cls(
        oauth_token=credentials.oauth_token.get_secret_value(),
        organization_id=credentials.organization_id,
        http=config.http,
    )
