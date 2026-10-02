"""DomainClient: one core session per domain client, closed with it; no empty credential."""

import pytest

from ycli.yandex.tracker.client import TrackerClient


@pytest.mark.parametrize(("token", "organization"), [("", "o"), ("t", "")])
def test_an_empty_credential_is_refused_before_any_request(token, organization):
    with pytest.raises(ValueError, match="both required"):
        TrackerClient(oauth_token=token, organization_id=organization)


def test_leaving_the_with_block_closes_the_session():
    with TrackerClient(oauth_token="t", organization_id="o") as client:
        core = client.issues._session._client
        assert not core.is_closed
        assert client.queues._session is client.issues._session
    assert core.is_closed
