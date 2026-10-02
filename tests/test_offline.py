"""No test reaches the network: an unmocked request fails loudly on either HTTP stack."""

import pytest
from pydantic import SecretStr

from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect
from ycli.yandex.transport import Transport


def test_an_unmocked_legacy_request_never_leaves_the_machine():
    session = Transport.session(
        oauth_token="t", organization_id="o", timeout_seconds=1.0, retries=0
    )
    with pytest.raises(AssertionError, match="unmocked legacy request: GET"):
        session.get("https://api.test/v3/me")


def test_an_unmocked_core_request_never_leaves_the_machine():
    session = connect(ServiceProfile("https://api.test/v3"), auth=OAuthTokenAuth(SecretStr("t")))
    with pytest.raises(AssertionError, match="unmocked core request: GET"):
        session.send(Endpoint("GET", "me"))
