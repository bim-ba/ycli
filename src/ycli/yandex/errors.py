"""Typed exceptions for Yandex API failures — pure classes, no HTTP imports.

Kept free of any HTTP library so cli/mcp may import it under ARCH-2. The core session
(``core/session.py``) maps a non-2xx response to one of these and raises it.
"""

from __future__ import annotations

import json


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
    """429 — rate limited (after the transport's retries were exhausted).

    ``retry_after`` is the server's ``Retry-After`` in seconds, when it sent one.
    """

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        url: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status=status, url=url)
        self.retry_after = retry_after


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


class YandexConnectionError(YandexError):
    """No HTTP response at all: DNS, connect or read failure, or a network timeout."""


def describe_error_body(body: str) -> str:
    """The human-readable line from a Yandex error body, or a raw snippet as a fallback.

    Tracker answers ``{"errorMessages": [...]}``, Wiki ``{"message": [...] or "...",
    "error_code": ...}``, Forms ``{"detail": ...}``; anything else is cut to 300 characters.

    Example:
        >>> describe_error_body('{"errorMessages": ["Issue does not exist."]}')
        'Issue does not exist.'
        >>> describe_error_body('{"error_code": "NOT_FOUND", "message": ["No page."]}')
        'NOT_FOUND: No page.'
    """
    try:
        data = json.loads(body)
    except ValueError:
        data = None
    if isinstance(data, dict):
        for key in ("errorMessages", "message", "detail"):
            value = data.get(key)
            if isinstance(value, list) and value:
                text = "; ".join(str(item) for item in value)
            elif isinstance(value, str) and value:
                text = value
            else:
                continue
            code = data.get("error_code")
            return f"{code}: {text}" if isinstance(code, str) else text
    return body[:300].replace("\n", " ").strip()


def error_for_status(
    status: int, message: str, *, url: str, retry_after: float | None = None
) -> YandexError:
    """The typed error for a non-2xx ``status`` — the one status-to-exception mapping.

    Example:
        >>> type(error_for_status(404, "gone", url="https://x")).__name__
        'YandexNotFoundError'
    """
    match status:
        case 401 | 403:
            return YandexAuthError(message, status=status, url=url)
        case 404:
            return YandexNotFoundError(message, status=status, url=url)
        case 429:
            return YandexRateLimitError(message, status=status, url=url, retry_after=retry_after)
        case _ if status >= 500:
            return YandexServerError(message, status=status, url=url)
        case _:
            return YandexClientError(message, status=status, url=url)
