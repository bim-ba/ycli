"""Typed exceptions for Yandex API failures — pure classes, no HTTP imports.

Kept free of ``requests``/``uplink`` so cli/mcp may import it under ARCH-2. The
transport (``transport.py``) maps a non-2xx response to one of these and raises it.
"""

from __future__ import annotations


class YandexError(Exception):
    """Base for every Yandex API error. Carries the HTTP status and request URL."""

    def __init__(self, message: str, *, status: int | None = None, url: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.url = url


class YandexAuthError(YandexError):
    """401/403 — missing, invalid, or insufficient credentials."""


class YandexNotFoundError(YandexError):
    """404 — the resource does not exist (or is not visible to this token)."""


class YandexRateLimitError(YandexError):
    """429 — rate limited (after the transport's retries were exhausted)."""


class YandexServerError(YandexError):
    """5xx — upstream Yandex error (after retries were exhausted)."""


class YandexClientError(YandexError):
    """Other 4xx — a client-side problem not covered by the specific classes."""


class YandexTimeoutError(YandexError):
    """A client-side deadline elapsed — e.g. an async operation polled past its attempt budget.

    Not raised by the transport (there is no HTTP status): the ``polling.poll`` helper raises
    it when ``is_done`` never becomes true within the allotted attempts, so callers can catch a
    single ``YandexError`` hierarchy for both transport failures and local timeouts.
    """
