"""Typed exceptions for Yandex API failures — pure classes, no HTTP imports.

Kept free of any HTTP library so cli/mcp may import it under ARCH-2. The core session
(``core/session.py``) maps a non-2xx response to one of these and raises it.
"""

import json
from http import HTTPStatus


class YandexError(Exception):
    """Base for every Yandex API error. Carries the HTTP status and request URL."""

    def __init__(self, message: str, *, status: int | None = None, url: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.url = url


class YandexInvalidRequestError(YandexError):
    """A request refused before it is sent, for a limit of ycli's own.

    What the API can check itself is not checked here (ARCH-9): the request goes out as given
    and the API's answer comes back as it is.
    """


class YandexUnexpectedReplyError(YandexError):
    """The API answered, but its reply does not fit the model ycli reads it into.

    The request was sent and may have taken effect; what failed is reading the answer. It is
    told apart from a request that the arguments given cannot build, which is never sent.
    """


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


def _error_item(item: object) -> str:
    """One item of an error list: ``code: msg`` for a validation-style object, else as text."""
    if not isinstance(item, dict) or "msg" not in item:
        return str(item)
    code = item.get("error_code") or item.get("type")
    return f"{code}: {item.get('msg')}" if code else str(item.get("msg"))


def describe_error_body(body: str) -> str:
    """The human-readable line from a Yandex error body, or a raw snippet as a fallback.

    Tracker answers ``{"errorMessages": [...]}``, Wiki ``{"message": [...] or "...",
    "error_code": ...}``, Forms ``{"detail": ...}`` or a bare list of ``{"loc", "error_code",
    "msg"}`` items; anything else is cut to 300 characters.

    Args:
        body: The response body text.

    Returns:
        The readable line, or the body cut to 300 characters.

    Examples:
        >>> describe_error_body('{"errorMessages": ["Issue does not exist."]}')
        'Issue does not exist.'
        >>> describe_error_body('{"error_code": "NOT_FOUND", "message": ["No page."]}')
        'NOT_FOUND: No page.'
        >>> describe_error_body('[{"loc": [], "error_code": "disabled", "msg": "Blocked"}]')
        'disabled: Blocked'
    """
    try:
        data = json.loads(body)
    except ValueError:
        data = None
    if isinstance(data, list) and data:
        return "; ".join(_error_item(item) for item in data)
    if isinstance(data, dict):
        for key in ("errorMessages", "message", "detail"):
            value = data.get(key)
            if isinstance(value, list) and value:
                text = "; ".join(_error_item(item) for item in value)
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

    Args:
        status: The non-2xx HTTP status.
        message: The error message.
        url: The request URL.
        retry_after: The server's ``Retry-After`` in seconds, if it sent one.

    Returns:
        The error ``status`` maps to.

    Examples:
        >>> type(error_for_status(404, "gone", url="https://x")).__name__
        'YandexNotFoundError'
    """
    match status:
        case HTTPStatus.UNAUTHORIZED | HTTPStatus.FORBIDDEN:
            return YandexAuthError(message, status=status, url=url)
        case HTTPStatus.NOT_FOUND:
            return YandexNotFoundError(message, status=status, url=url)
        case HTTPStatus.TOO_MANY_REQUESTS:
            return YandexRateLimitError(message, status=status, url=url, retry_after=retry_after)
        case _ if status >= HTTPStatus.INTERNAL_SERVER_ERROR:
            return YandexServerError(message, status=status, url=url)
        case _:
            return YandexClientError(message, status=status, url=url)
