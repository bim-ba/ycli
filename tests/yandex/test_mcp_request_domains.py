from types import SimpleNamespace
from typing import Any, cast

import pytest

from ycli.yandex import mcp
from ycli.yandex.forms.dependencies import forms_client
from ycli.yandex.status import mcp as status_mcp
from ycli.yandex.tracker.dependencies import tracker_client
from ycli.yandex.wiki.dependencies import wiki_client


@pytest.fixture
def request_auth(monkeypatch):
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud-org")
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "env-token")
    from fastmcp.server.auth import AccessToken

    monkeypatch.setattr(
        mcp,
        "get_access_token",
        lambda: AccessToken(token="request-token", client_id="identity-hub", scopes=[]),
    )
    mcp.set_request_auth(mcp.RequestAuth("cloud-org"))


@pytest.mark.parametrize(
    ("provider", "resource"),
    [
        (tracker_client, "priorities"),
        (wiki_client, "me"),
        (forms_client, "me"),
    ],
)
def test_domain_clients_use_request_bearer_and_cloud_org(request_auth, provider, resource):
    client = provider()
    session = getattr(client, resource)._session
    assert session.headers["Authorization"] == "Bearer request-token"
    assert session.headers["X-Cloud-Org-Id"] == "cloud-org"
    assert "env-token" not in repr(session.headers)


def test_status_uses_request_credentials_for_all_domains(request_auth, monkeypatch):
    seen: list[tuple[str, str]] = []

    def build(client_cls, credentials, config):
        assert credentials.oauth_token is None
        assert credentials.iam_token == "request-token"
        assert credentials.cloud_organization_id == "cloud-org"
        seen.append((client_cls.__name__, credentials.iam_token))
        return SimpleNamespace(me=object())

    monkeypatch.setattr(status_mcp.ClientFactory, "build", build)
    monkeypatch.setattr(
        status_mcp.StatusReporter,
        "__init__",
        lambda self, clients: setattr(self, "clients", clients),
    )
    monkeypatch.setattr(
        status_mcp.StatusReporter,
        "report",
        lambda self, **kwargs: {"clients": sorted(self.clients), **kwargs},
    )
    credentials = mcp.credentials()
    assert "request-token" not in repr(credentials)
    result = status_mcp.get(credentials=credentials, config=mcp.app_config())
    assert sorted(seen) == [
        ("FormsClient", "request-token"),
        ("TrackerClient", "request-token"),
        ("WikiClient", "request-token"),
    ]
    assert cast("Any", result)["clients"] == ["forms", "tracker", "wiki"]
