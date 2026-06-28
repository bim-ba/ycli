"""Typed SDK errors: the transport raises the right class on each non-2xx status."""

from __future__ import annotations

import pytest
import responses

from ycli.yandex.errors import (
    YandexAuthError,
    YandexClientError,
    YandexError,
    YandexNotFoundError,
    YandexRateLimitError,
    YandexServerError,
)
from ycli.yandex.transport import Transport


def _get(status: int):
    """Fire one GET through a transport session at a stubbed URL of the given status."""
    url = "https://api.tracker.yandex.net/v3/probe"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=status, json={"errorMessages": ["boom"]})
        session = Transport.session(
            oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3
        )
        return session.get(url)


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
    url = "https://api.tracker.yandex.net/v3/ok"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=200, json={"ok": True})
        session = Transport.session(
            oauth_token="t", organization_id="o", timeout_seconds=30.0, retries=3
        )
        assert session.get(url).json() == {"ok": True}
