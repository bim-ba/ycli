"""Every auth kind as an httpx2.Auth; the service-account flow mints, reuses and refreshes."""

import json
import time

import httpx2
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretStr

from ycli.yandex.core.auth import (
    IAM_TOKEN_URL,
    APIKeyAuth,
    BotTokenAuth,
    IAMTokenAuth,
    OAuthTokenAuth,
    ServiceAccountAuth,
)
from ycli.yandex.errors import YandexAuthError

API = "https://api.test/v1/me"
# A throwaway key generated for the test run, not a credential.
_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PEM = _KEY.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
).decode()


def _echo(request: httpx2.Request) -> httpx2.Response:
    return httpx2.Response(200, json={"auth": request.headers.get("Authorization")})


@pytest.mark.parametrize(
    ("auth", "header"),
    [
        (OAuthTokenAuth(SecretStr("y0")), "OAuth y0"),
        (BotTokenAuth(SecretStr("bot")), "OAuth bot"),
        (IAMTokenAuth(SecretStr("t1")), "Bearer t1"),
        (APIKeyAuth(SecretStr("k1")), "Api-Key k1"),
    ],
)
def test_header_auth(auth, header):
    client = httpx2.Client(auth=auth, transport=httpx2.MockTransport(_echo))
    assert client.get(API).json() == {"auth": header}


def test_api_key_as_a_query_parameter():
    seen = []
    transport = httpx2.MockTransport(lambda request: seen.append(request) or httpx2.Response(200))
    httpx2.Client(auth=APIKeyAuth(SecretStr("k1"), query_param="apikey"), transport=transport).get(
        API
    )
    assert seen[0].url.params["apikey"] == "k1"
    assert "Authorization" not in seen[0].headers


class _IAM:
    """A stand-in IAM endpoint plus an API that accepts only the newest token."""

    def __init__(self, lifetime_seconds: int = 3600, reject_first_api_call: bool = False) -> None:
        self.issued = 0
        self.lifetime_seconds = lifetime_seconds
        self.reject_first_api_call = reject_first_api_call
        self.api_calls = 0

    def __call__(self, request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == IAM_TOKEN_URL:
            assertion = json.loads(request.content)["jwt"]
            claims = jwt.decode(
                assertion, _KEY.public_key(), algorithms=["PS256"], audience=IAM_TOKEN_URL
            )
            assert jwt.get_unverified_header(assertion)["kid"] == "key-1"
            assert claims["iss"] == "sa-1"
            self.issued += 1
            expires = time.gmtime(time.time() + self.lifetime_seconds)
            return httpx2.Response(
                200,
                json={
                    "iamToken": f"iam-{self.issued}",
                    "expiresAt": time.strftime("%Y-%m-%dT%H:%M:%S.123456789Z", expires),
                },
            )
        self.api_calls += 1
        if self.reject_first_api_call and self.api_calls == 1:
            return httpx2.Response(401)
        return _echo(request)


def _auth() -> ServiceAccountAuth:
    return ServiceAccountAuth(
        service_account_id="sa-1", key_id="key-1", private_key=SecretStr(_PEM)
    )


def test_service_account_mints_once_and_reuses_the_token():
    iam = _IAM()
    client = httpx2.Client(auth=_auth(), transport=httpx2.MockTransport(iam))
    assert client.get(API).json() == {"auth": "Bearer iam-1"}
    assert client.get(API).json() == {"auth": "Bearer iam-1"}
    assert iam.issued == 1


def test_service_account_refreshes_a_token_close_to_expiry():
    iam = _IAM(lifetime_seconds=60)  # inside the 5-minute refresh margin
    client = httpx2.Client(auth=_auth(), transport=httpx2.MockTransport(iam))
    client.get(API)
    assert client.get(API).json() == {"auth": "Bearer iam-2"}


def test_service_account_refreshes_once_on_401():
    iam = _IAM(reject_first_api_call=True)
    client = httpx2.Client(auth=_auth(), transport=httpx2.MockTransport(iam))
    assert client.get(API).json() == {"auth": "Bearer iam-2"}


def test_a_custom_token_url_is_also_the_jwt_audience():
    """The JWT names the endpoint it is sent to, so a non-default IAM endpoint accepts it."""
    token_url = "https://iam.example.test/iam/v1/tokens"
    audiences: list[str] = []

    def iam(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) != token_url:
            return _echo(request)
        assertion = json.loads(request.content)["jwt"]
        audiences.append(jwt.decode(assertion, options={"verify_signature": False})["aud"])
        return httpx2.Response(200, json={"iamToken": "iam-1", "expiresAt": "2099-01-01T00:00:00Z"})

    auth = ServiceAccountAuth(
        service_account_id="sa-1", key_id="key-1", private_key=SecretStr(_PEM), token_url=token_url
    )
    client = httpx2.Client(auth=auth, transport=httpx2.MockTransport(iam))
    assert client.get(API).json() == {"auth": "Bearer iam-1"}
    assert audiences == [token_url]


def test_a_failed_exchange_raises_a_typed_error():
    def deny(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(401, json={"message": "bad key"})

    client = httpx2.Client(auth=_auth(), transport=httpx2.MockTransport(deny))
    with pytest.raises(YandexAuthError, match="IAM token exchange failed: bad key"):
        client.get(API)


def test_the_key_file_from_yc_loads_despite_its_comment_line(tmp_path):
    key_file = tmp_path / "key.json"
    key_file.write_text(
        json.dumps(
            {
                "id": "key-1",
                "service_account_id": "sa-1",
                "private_key": "PLEASE DO NOT REMOVE THIS LINE! Yandex.Cloud SA Key ID <key-1>\n"
                + _PEM,
            }
        )
    )
    iam = _IAM()
    auth = ServiceAccountAuth.from_key_file(key_file)
    client = httpx2.Client(auth=auth, transport=httpx2.MockTransport(iam))
    assert client.get(API).json() == {"auth": "Bearer iam-1"}
    assert "BEGIN" not in repr(vars(auth))


async def test_service_account_async_flow():
    iam = _IAM(reject_first_api_call=True)
    client = httpx2.AsyncClient(auth=_auth(), transport=httpx2.MockTransport(iam))
    assert (await client.get(API)).json() == {"auth": "Bearer iam-2"}
    assert (await client.get(API)).json() == {"auth": "Bearer iam-2"}
    assert iam.issued == 2


def test_concurrent_401s_refresh_the_token_once():
    import threading

    iam = _IAM()
    revoked = threading.Event()
    all_sent = threading.Barrier(5)

    def api(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == IAM_TOKEN_URL:
            return iam(request)
        if revoked.is_set() and request.headers["Authorization"] == "Bearer iam-1":
            all_sent.wait(timeout=5)  # every thread has sent with the revoked token
            return httpx2.Response(401)
        return _echo(request)

    client = httpx2.Client(auth=_auth(), transport=httpx2.MockTransport(api))
    client.get(API)  # mints iam-1
    revoked.set()
    threads = [threading.Thread(target=client.get, args=(API,)) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert iam.issued == 2  # five 401s, one refresh


def test_the_async_lock_works_across_event_loops():
    import asyncio

    iam = _IAM()
    auth = _auth()

    async def burst() -> list[str]:
        client = httpx2.AsyncClient(auth=auth, transport=httpx2.MockTransport(iam))
        responses = await asyncio.gather(*(client.get(API) for _ in range(3)))
        return [response.json()["auth"] for response in responses]

    assert asyncio.run(burst()) == ["Bearer iam-1"] * 3
    assert asyncio.run(burst()) == ["Bearer iam-1"] * 3


async def test_concurrent_async_401s_refresh_the_token_once():
    import asyncio

    iam = _IAM()
    revoked = asyncio.Event()
    waiting: list[asyncio.Future] = []

    async def api(request: httpx2.Request) -> httpx2.Response:
        if str(request.url) == IAM_TOKEN_URL:
            return iam(request)
        if revoked.is_set() and request.headers["Authorization"] == "Bearer iam-1":
            gate = asyncio.get_running_loop().create_future()
            waiting.append(gate)
            if len(waiting) == 3:  # all three were sent with the revoked token
                for pending in waiting:
                    pending.set_result(None)
            await gate
            return httpx2.Response(401)
        return _echo(request)

    client = httpx2.AsyncClient(auth=_auth(), transport=httpx2.MockTransport(api))
    await client.get(API)  # mints iam-1
    revoked.set()
    responses = await asyncio.gather(*(client.get(API) for _ in range(3)))
    assert {response.json()["auth"] for response in responses} == {"Bearer iam-2"}
    assert iam.issued == 2
