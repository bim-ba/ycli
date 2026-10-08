"""The single client-construction site — maps app config + credentials to raw client args.

Env-free by design (ARCH-5, ARCH-7): callers at the composition roots (AppContext, the MCP
``dependencies`` providers) read the environment and hand instances here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.settings import (
    CLOUD_ORGANIZATION_ID_ENV,
    IAM_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    SERVICE_ACCOUNT_KEY_FILE_ENV,
    CredentialKind,
)
from ycli.yandex.errors import YandexNotConfiguredError

if TYPE_CHECKING:
    import httpx2

    from ycli.settings import AppConfig, Credentials
    from ycli.yandex.base import DomainClient
    from ycli.yandex.core.guard import Guard
    from ycli.yandex.core.profile import ServiceProfile
    from ycli.yandex.core.session import BeforeSend


def not_configured(profile: ServiceProfile, credentials: Credentials) -> str | None:
    """Why ``credentials`` cannot reach the service of ``profile``; ``None`` when they can.

    Args:
        profile: Where the service lives and what it takes.
        credentials: The way to sign in and the organization of either kind.

    Returns:
        What the service needs and which variable sets it.

    Examples:
        >>> from ycli.settings import Credentials
        >>> from ycli.yandex.datalens import SERVICE
        >>> credentials = Credentials(oauth_token="token", organization_id="org")
        >>> not_configured(SERVICE.profile, credentials)
        'needs a Yandex Cloud organization: set YANDEX_CLOUD_ORGANIZATION_ID'
    """
    kinds = (
        (profile.org_header, credentials.organization_id, "Yandex 360", ORGANIZATION_ID_ENV),
        (
            profile.cloud_org_header,
            credentials.cloud_organization_id,
            "Yandex Cloud",
            CLOUD_ORGANIZATION_ID_ENV,
        ),
    )
    taken = [(kind, variable) for header, _, kind, variable in kinds if header]
    if taken and not any(header and value for header, value, _, _ in kinds):
        names = " or a ".join(kind for kind, _ in taken)
        variables = " or ".join(variable for _, variable in taken)
        return f"needs a {names} organization: set {variables}"
    if not profile.oauth_token and credentials.kind is CredentialKind.OAUTH:
        return (
            "takes an IAM token or a service account's key, not an OAuth token: sign in with "
            f"{IAM_TOKEN_ENV} or {SERVICE_ACCOUNT_KEY_FILE_ENV}"
        )
    return None


def build_client[C: DomainClient](
    client_cls: type[C],
    credentials: Credentials,
    config: AppConfig,
    before_send: BeforeSend | None = None,
    guard: Guard | None = None,
) -> C:
    """Construct ``client_cls`` from ``credentials`` + ``config`` — never reads the env.

    ``before_send`` and ``guard`` are the client's own (see
    :class:`~ycli.yandex.base.DomainClient`).

    Args:
        client_cls: The domain client class to build.
        credentials: The way to sign in and the organization of either kind.
        config: The HTTP settings.
        before_send: The client's per-endpoint hook.
        guard: What shows or confirms a write before it is sent.

    Returns:
        The ready client.

    Raises:
        YandexNotConfiguredError: The credentials cannot reach this service
            (:func:`not_configured` says why).

    Examples:
        >>> from ycli.settings import AppConfig, Credentials
        >>> from ycli.yandex.tracker.client import TrackerClient
        >>> credentials = Credentials(oauth_token="token", organization_id="org")
        >>> with build_client(TrackerClient, credentials, AppConfig()) as client:
        ...     client.me.get().login
        'alice'
    """
    reason = not_configured(client_cls.profile, credentials)
    if reason:
        name = client_cls.__name__.removesuffix("Client")
        raise YandexNotConfiguredError(f"{name} is not configured: it {reason}")
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
        guard=guard,
    )
