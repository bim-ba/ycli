"""A service account's key and a Yandex Cloud organization, from the settings to the request."""

import json

import pytest
from pydantic import SecretStr, ValidationError

from tests.hosts import TRACKER_BASE
from ycli.settings import (
    AppConfig,
    CredentialKind,
    Credentials,
    OrganizationKind,
    credential_sources,
    missing_credentials,
)
from ycli.yandex.core.auth import ServiceAccountAuth
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.factory import build_client
from ycli.yandex.tracker.client import TrackerClient

EITHER = ServiceProfile("https://api.example.net/v1")
CLOUD_ONLY = ServiceProfile(
    "https://api.example.net/rpc", org_header=None, cloud_org_header="x-dl-org-id"
)
KEY = {"id": "key-1", "service_account_id": "sa-1", "private_key": "-----BEGIN PRIVATE KEY-----"}


@pytest.mark.parametrize(
    ("profile", "organization_id", "cloud_organization_id", "headers"),
    [
        (EITHER, "360-1", None, {"X-Org-Id": "360-1"}),
        (EITHER, None, "cloud-1", {"X-Cloud-Org-Id": "cloud-1"}),
        (EITHER, "360-1", "cloud-1", {"X-Org-Id": "360-1"}),
        (EITHER, None, None, {}),
        (CLOUD_ONLY, "360-1", None, {}),
        (CLOUD_ONLY, None, "cloud-1", {"x-dl-org-id": "cloud-1"}),
        (CLOUD_ONLY, "360-1", "cloud-1", {"x-dl-org-id": "cloud-1"}),
        (CLOUD_ONLY, None, None, {}),
    ],
)
def test_a_service_gets_the_one_organization_of_the_kind_it_takes(
    profile, organization_id, cloud_organization_id, headers
):
    assert profile.headers_for(organization_id, cloud_organization_id) == headers


@pytest.mark.parametrize(
    ("profile", "given", "variables"),
    [
        (EITHER, {}, "YANDEX_ID_ORGANIZATION_ID or YANDEX_CLOUD_ORGANIZATION_ID"),
        (CLOUD_ONLY, {"organization_id": "360-1"}, "YANDEX_CLOUD_ORGANIZATION_ID"),
    ],
)
def test_a_client_without_an_organization_it_can_use_names_the_variable(
    monkeypatch, profile, given, variables
):
    monkeypatch.setattr(TrackerClient, "profile", profile)
    with pytest.raises(ValueError, match=f"needs an organization: set {variables}$"):
        TrackerClient(oauth_token="t", **given)


def test_a_cloud_organization_alone_is_sent_under_its_own_header(api):
    credentials = Credentials(
        oauth_token=None,
        iam_token=SecretStr("t1.x"),
        organization_id=None,
        cloud_organization_id="cloud-1",
    )
    api.add("GET", f"{TRACKER_BASE}/myself", json={"login": "alice"})
    with build_client(TrackerClient, credentials, AppConfig()) as client:
        client.me.get()
    headers = api.calls[0].headers
    assert (headers["X-Cloud-Org-Id"], "X-Org-Id" in headers) == ("cloud-1", False)
    assert credentials.organization == ("cloud-1", OrganizationKind.CLOUD)


@pytest.mark.parametrize("from_file", [True, False], ids=["a file", "its text"])
def test_a_service_account_key_signs_in_from_a_file_or_from_its_text(tmp_path, from_file):
    key_file = tmp_path / "key.json"
    key_file.write_text(json.dumps(KEY))
    credentials = Credentials(
        oauth_token=None,
        organization_id="1",
        service_account_key_file=key_file if from_file else None,
        service_account_key=None if from_file else SecretStr(json.dumps(KEY)),
    )
    assert credentials.kind is CredentialKind.SERVICE_ACCOUNT
    with build_client(TrackerClient, credentials, AppConfig()) as client:
        auth = client.me._session._client.auth
    assert isinstance(auth, ServiceAccountAuth)
    assert (auth._service_account_id, auth._key_id) == ("sa-1", "key-1")


def test_two_ways_to_sign_in_are_refused_by_name():
    with pytest.raises(ValidationError) as caught:
        Credentials(
            oauth_token=SecretStr("t"), service_account_key=SecretStr("{}"), organization_id="1"
        )
    message = caught.value.errors()[0]["msg"]
    assert message == (
        "YANDEX_ID_OAUTH_TOKEN and YANDEX_CLOUD_SERVICE_ACCOUNT_KEY are both set: keep one of them"
    )


def test_no_organization_of_either_kind_is_reported_as_the_missing_variable(monkeypatch):
    for name in ("YANDEX_ID_ORGANIZATION_ID", "YCLI__AUTH__ORGANIZATION_ID"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("YANDEX_CLOUD_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("YANDEX_ID_OAUTH_TOKEN", "t")
    with pytest.raises(ValidationError) as caught:
        Credentials()
    assert missing_credentials(caught.value) == ["YANDEX_ID_ORGANIZATION_ID"]


def test_the_sources_name_only_what_is_set_of_each_group(monkeypatch):
    for name in ("YANDEX_ID_OAUTH_TOKEN", "YANDEX_CLOUD_IAM_TOKEN", "YANDEX_ID_ORGANIZATION_ID"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_FILE", "key.json")
    monkeypatch.setenv("YANDEX_CLOUD_ORGANIZATION_ID", "cloud-1")
    assert credential_sources() == {
        "YANDEX_CLOUD_SERVICE_ACCOUNT_KEY_FILE": "environment",
        "YANDEX_CLOUD_ORGANIZATION_ID": "environment",
    }
