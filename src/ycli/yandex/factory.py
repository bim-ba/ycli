"""The single client-construction site — maps app config + credentials to raw client args.

Env-free by design (ARCH-5, ARCH-7): callers at the composition roots (AppContext, the MCP
``dependencies`` providers) read the environment and hand instances here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ycli.settings import AppConfig, Credentials
    from ycli.yandex.base import DomainClient
    from ycli.yandex.core.session import BeforeSend


def build_client[C: DomainClient](
    client_cls: type[C],
    credentials: Credentials,
    config: AppConfig,
    before_send: BeforeSend | None = None,
) -> C:
    """Construct ``client_cls`` from ``credentials`` + ``config`` — never reads the env.

    ``before_send`` is the client's per-endpoint hook (see :class:`~ycli.yandex.base.DomainClient`).

    Args:
        client_cls: The domain client class to build.
        credentials: The token (OAuth or IAM) and the organization id.
        config: The HTTP settings.
        before_send: The client's per-endpoint hook.

    Returns:
        The ready client.

    Examples:
        >>> from ycli.settings import AppConfig, Credentials
        >>> from ycli.yandex.tracker.client import TrackerClient
        >>> credentials = Credentials(oauth_token="token", organization_id="org")
        >>> with build_client(TrackerClient, credentials, AppConfig()) as client:
        ...     client.me.get().login
        'alice'
    """
    # Imported here: httpx2 costs ~0.2 s, paid only once a client is built.
    from ycli.yandex.core.auth import IAMTokenAuth, OAuthTokenAuth

    scheme = IAMTokenAuth if credentials.kind == "iam" else OAuthTokenAuth
    return client_cls(
        auth=scheme(credentials.token),
        organization_id=credentials.organization_id,
        http=config.http,
        before_send=before_send,
    )
