"""Typed SDK errors: a core session raises the right class on each non-2xx status."""

from http import HTTPMethod

import pytest
from pydantic import SecretStr

from tests.mock_api import MockAPI
from ycli.settings import HTTPConfig
from ycli.yandex.core.auth import OAuthTokenAuth
from ycli.yandex.core.endpoint import Endpoint
from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.core.session import connect
from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
)

BASE = "https://api.tracker.yandex.net/v3"


def _get_with(status: int, path: str = "detail", **answer):
    """Send one GET through a core session at a stubbed URL answering ``status``."""
    api = MockAPI()
    api.add("GET", f"{BASE}/{path}", status=status, **answer)
    session = connect(
        ServiceProfile(BASE),
        auth=OAuthTokenAuth(SecretStr("t")),
        organization_id="o",
        http=HTTPConfig(retries=0),
        transport=api.transport(),
    )
    return session.send(Endpoint(HTTPMethod.GET, path, dict))


def _get(status: int):
    return _get_with(status, "probe", json={"errorMessages": ["boom"]})


@pytest.mark.parametrize(
    ("status", "exc"),
    [
        (401, YandexAuthError),
        (403, YandexAuthError),
        (404, YandexNotFoundError),
        (429, YandexRateLimitError),
        (503, YandexServerError),
        (418, YandexClientError),
    ],
)
def test_status_maps_to_typed_error(status, exc):
    with pytest.raises(exc) as info:
        _get(status)
    assert isinstance(info.value, YandexError)
    assert info.value.status == status
    assert str(status) in str(info.value)


def test_success_does_not_raise():
    assert _get_with(200, "ok", json={"ok": True}) == {"ok": True}


def test_error_message_surfaces_yandex_error_messages():
    with pytest.raises(YandexNotFoundError) as info:
        _get_with(404, json={"errorMessages": ["Задача не существует."]})
    assert "Задача не существует." in str(info.value)
    assert "errorMessages" not in str(info.value)  # raw JSON is not surfaced


def test_error_message_falls_back_to_snippet_without_error_messages():
    with pytest.raises(YandexClientError) as info:
        _get_with(400, json={"foo": "bar"})
    assert "foo" in str(info.value)  # raw-body snippet fallback


def test_error_message_falls_back_on_non_json_body():
    with pytest.raises(YandexServerError) as info:
        _get_with(503, content=b"upstream exploded")
    assert "upstream exploded" in str(info.value)


@pytest.mark.parametrize(
    ("body", "line"),
    [
        (
            '[{"loc": [], "error_code": "disabled", "msg": "Функция заблокирована"}]',
            "disabled: Функция заблокирована",
        ),
        (
            '{"detail": [{"loc": ["body"], "type": "missing", "msg": "Field required"}]}',
            "missing: Field required",
        ),
        ('{"detail": [{"msg": "Bad"}]}', "Bad"),
    ],
)
def test_forms_validation_errors_read_as_text(body, line):
    """Forms answers a list of ``{loc, error_code, msg}``: the message, not escaped JSON."""
    from ycli.yandex.errors import describe_error_body

    assert describe_error_body(body) == line
