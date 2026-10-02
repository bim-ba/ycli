"""TokenClient — the token's owner from Yandex ID and its organizations from API 360."""

import pytest

from ycli.yandex.errors import YandexAuthError, YandexServerError
from ycli.yandex.status.token_client import TokenClient

ID_URL = "https://login.yandex.ru/info"
ORG_URL = "https://api360.yandex.net/directory/v1/org"


def test_identity_reads_the_owner_with_the_oauth_header_and_no_org_header(api):
    api.add(
        "GET",
        ID_URL,
        json={"id": "1000034426", "login": "ivan", "client_id": "app", "psuid": "1.A"},
    )
    with TokenClient(oauth_token="tok") as client:
        identity = client.identity()
    assert (identity.id, identity.login) == ("1000034426", "ivan")
    assert identity.display_name is None  # the login:info scope is not granted
    [call] = api.calls
    assert call.headers["Authorization"] == "OAuth tok"
    assert "X-Org-Id" not in call.headers
    assert call.url.params["format"] == "json"


def test_identity_keeps_the_names_and_the_email_the_scopes_return(api):
    api.add(
        "GET",
        ID_URL,
        json={
            "id": "7",
            "login": "ivan",
            "display_name": "Ivan",
            "real_name": "Ivan Ivanov",
            "default_email": "ivan@yandex.ru",
        },
    )
    with TokenClient(oauth_token="tok") as client:
        identity = client.identity()
    assert (identity.display_name, identity.real_name, identity.default_email) == (
        "Ivan",
        "Ivan Ivanov",
        "ivan@yandex.ru",
    )


def test_a_rejected_token_raises_a_typed_error(api):
    api.add("GET", ID_URL, json={"error": "bad token"}, status=401)
    with TokenClient(oauth_token="tok") as client, pytest.raises(YandexAuthError):
        client.identity()


def test_organizations_walks_every_page_without_an_org_header(api):
    api.add(
        "GET",
        ORG_URL,
        json={"organizations": [{"id": 1, "name": "Acme"}], "nextPageToken": "page-2"},
    )
    api.add("GET", ORG_URL, json={"organizations": [{"id": 2, "name": "Beta"}]})
    with TokenClient(oauth_token="tok") as client:
        organizations = client.organizations()
    assert [(org.id, org.name) for org in organizations] == [(1, "Acme"), (2, "Beta")]
    first, second = api.calls
    assert first.headers["Authorization"] == "OAuth tok"
    assert "X-Org-Id" not in first.headers
    assert first.url.params["pageSize"] == "100"
    assert "pageToken" not in first.url.params
    assert second.url.params["pageToken"] == "page-2"


@pytest.mark.parametrize("status", [401, 403])
def test_organizations_without_the_directory_scope_raise_an_auth_error(api, status):
    api.add("GET", ORG_URL, json={"code": 7, "message": "No required scope"}, status=status)
    with TokenClient(oauth_token="tok") as client, pytest.raises(YandexAuthError):
        client.organizations()


def test_organizations_raise_other_failures_as_they_are(api):
    api.add("GET", ORG_URL, content=b"<html>Service Unavailable</html>", status=503)
    with TokenClient(oauth_token="tok") as client, pytest.raises(YandexServerError):
        client.organizations()


def test_closing_the_client_closes_both_connection_pools():
    with TokenClient(oauth_token="tok") as client:
        pools = [client._identity._client, client._directory._client]
        assert not any(pool.is_closed for pool in pools)
    assert all(pool.is_closed for pool in pools)
