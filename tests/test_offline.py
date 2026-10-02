"""No test reaches the network: an unmocked request fails loudly."""

import pytest
from pydantic import SecretStr

from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect


def test_an_unmocked_core_request_never_leaves_the_machine():
    session = connect(ServiceProfile("https://api.test/v3"), auth=OAuthTokenAuth(SecretStr("t")))
    with pytest.raises(AssertionError, match="unmocked core request: GET"):
        session.send(Endpoint("GET", "me"))
