"""``Endpoint[T]`` — one API operation declared once, as plain data, for sync and async alike.

An endpoint knows its HTTP method and path, its query and body, the type its response parses
into, and its *effect*: what calling it does to the server. The effect follows from the
method (``GET`` reads, ``PATCH``/``PUT`` edit, ``DELETE`` destroys, ``POST`` writes) unless the
endpoint states otherwise, as a ``POST …/_search`` does. Retries follow that one value, and the
MCP tool annotations must agree with it.

Nothing here does I/O: :meth:`Endpoint.request` builds a native ``httpx2.Request`` through the
client (so its base URL and default headers apply) and :meth:`Endpoint.parse` reads a response.

Example:
    >>> Endpoint("GET", "issues/TEST-1").effect
    'read'
    >>> Endpoint("POST", "issues/_search", effect="read").idempotent
    True
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, Any, Literal, cast
from urllib.parse import quote, unquote

from pydantic import TypeAdapter

from ycli.yandex.errors import YandexClientError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    import httpx2

    from ycli.yandex.core.pagination import Pagination

type Effect = Literal["read", "write", "idempotent_write", "destructive"]

EFFECT_EXTENSION = "ycli.effect"
_EFFECT_BY_METHOD: dict[str, Effect] = {
    "GET": "read",
    "HEAD": "read",
    "OPTIONS": "read",
    "PUT": "idempotent_write",
    "PATCH": "idempotent_write",
    "DELETE": "destructive",
    "POST": "write",
}


def segment(value: object) -> str:
    """One URL path segment from a caller's value, percent-escaped.

    Escaping alone does not keep a value in its place: Yandex servers decode ``%2F`` before
    routing, so :func:`check_path` rejects the request that such a value produces.

    Example:
        >>> segment("TEST 1")
        'TEST%201'
    """
    return quote(str(value), safe="")


def check_path(raw_path: str) -> None:
    """Refuse a percent-encoded URL path that the server would route to another endpoint.

    The server decodes ``%2F`` and ``%5C`` and then resolves ``.``/``..``, so an issue key such
    as ``../queues/DE`` turns ``PATCH issues/{key}`` into ``PATCH queues/DE``. No Yandex path
    needs an escaped separator, an empty segment or a dot segment, so all three are refused.

    Example:
        >>> check_path("/v3/issues/TEST-1/")
        >>> check_path("/v3/issues/..%2Fqueues%2FDE")
        Traceback (most recent call last):
        ...
        ycli.yandex.errors.YandexClientError: refusing a path that leaves its endpoint: ...
    """
    lowered = raw_path.lower()
    segments = unquote(raw_path).split("/")
    if (
        "%2f" in lowered
        or "%5c" in lowered
        or "//" in raw_path
        or any(part in {".", ".."} for part in segments)
    ):
        raise YandexClientError(f"refusing a path that leaves its endpoint: {raw_path}")


@cache
def _adapter(response_type: Any) -> TypeAdapter[Any]:
    """One TypeAdapter per response type: building it is the expensive part of parsing."""
    return TypeAdapter(response_type)


@dataclass(frozen=True, slots=True, init=False)
class Endpoint[T]:
    """An API operation: ``method`` + ``path`` (relative to the service's base URL) and its I/O.

    ``params`` with a ``None`` value are dropped, so optional query parameters can be passed
    through unconditionally. ``response_type=None`` means the response body is ignored.
    """

    method: str
    path: str
    response_type: type[T] | None
    params: Mapping[str, Any]
    json: Any
    content: bytes | None
    headers: Mapping[str, str]
    effect_override: Effect | None

    def __init__(
        self,
        method: str,
        path: str,
        response_type: type[T] | None = None,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        content: bytes | None = None,
        headers: Mapping[str, str] | None = None,
        effect: Effect | None = None,
    ) -> None:
        object.__setattr__(self, "method", method.upper())
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "response_type", response_type)
        object.__setattr__(self, "params", dict(params or {}))
        object.__setattr__(self, "json", json)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "headers", dict(headers or {}))
        object.__setattr__(self, "effect_override", effect)

    @property
    def effect(self) -> Effect:
        """What the call does to the server: stated explicitly, or implied by the method."""
        return self.effect_override or _EFFECT_BY_METHOD[self.method]

    @property
    def idempotent(self) -> bool:
        """Safe to send twice — the retry policy re-sends only these after a 5xx or lost link."""
        return self.effect in {"read", "idempotent_write"}

    def request(self, client: httpx2.Client | httpx2.AsyncClient) -> httpx2.Request:
        """A native request built by ``client``: its base URL and default headers apply."""
        params = {name: value for name, value in self.params.items() if value is not None}
        return client.build_request(
            self.method,
            self.path,
            params=params or None,
            json=self.json,
            content=self.content,
            headers=dict(self.headers) or None,
            extensions={EFFECT_EXTENSION: self.effect},
        )

    def parse(self, response: httpx2.Response) -> T:
        """The response body as ``response_type`` (``None`` when the endpoint ignores it)."""
        if self.response_type is None:
            return cast("T", None)
        return _adapter(self.response_type).validate_json(response.content)


@dataclass(frozen=True, slots=True)
class Paged[P, I]:
    """A paginated listing: the first-page endpoint, how to page it, and how to read a page.

    ``P`` is the page type the endpoint parses into; ``items_of`` pulls the ``I`` items out of it.
    """

    endpoint: Endpoint[P]
    pagination: Pagination
    items_of: Callable[[P], Sequence[I]]
