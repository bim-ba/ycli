"""The single client-construction site — maps app config + credentials to raw client args.

Env-free by design (ARCH-5, ARCH-7): callers at the composition roots (AppContext, the MCP
``dependencies`` providers) read the environment and hand instances here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.settings import CredentialKind

if TYPE_CHECKING:
    import httpx2

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
        credentials: The way to sign in and the organization of either kind.
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
    from ycli.yandex.core.auth import IAMTokenAuth, OAuthTokenAuth, ServiceAccountAuth

    auth: httpx2.Auth
    if credentials.service_account_key_file is not None:
        auth = ServiceAccountAuth.from_key_file(credentials.service_account_key_file)
    elif credentials.service_account_key is not None:
        auth = ServiceAccountAuth.from_key(credentials.service_account_key.get_secret_value())
    elif credentials.kind is CredentialKind.IAM:
        auth = IAMTokenAuth(credentials.token)
    else:
        auth = OAuthTokenAuth(credentials.token)
    return client_cls(
        auth=auth,
        organization_id=credentials.organization_id,
        cloud_organization_id=credentials.cloud_organization_id,
        http=config.http,
        before_send=before_send,
    )
