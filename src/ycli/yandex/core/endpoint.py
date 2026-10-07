"""``Endpoint[T]`` — one API operation declared once, as plain data, for sync and async alike.

An endpoint knows its HTTP method and path, its query and body, the type its response parses
into, and its *effect*: what calling it does to the server. The effect follows from the
method (``GET`` reads, ``PATCH``/``PUT`` edit, ``DELETE`` destroys, ``POST`` writes) unless the
endpoint states otherwise, as a ``POST …/_search`` does. Where the method says nothing, in an
RPC API whose every operation is a ``POST``, :func:`RPC` writes the endpoint and the effect is
always named. Retries follow that one value, and the MCP tool annotations must agree with it.

Nothing here does I/O: :meth:`Endpoint.request` builds a native ``httpx2.Request`` through the
client (so its base URL and default headers apply) and :meth:`Endpoint.parse` reads a response.

Examples:
    >>> Endpoint(HTTPMethod.GET, "issues/TEST-1").effect
    <Effect.READ: 'read'>
    >>> Endpoint(HTTPMethod.POST, "issues/_search", effect=Effect.READ).idempotent
    True
"""

from __future__ import annotations

import enum
from dataclasses import KW_ONLY, dataclass, field
from functools import cache
from http import HTTPMethod
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote, unquote

from pydantic import TypeAdapter, ValidationError
from pydantic_core import to_jsonable_python

from ycli.yandex.errors import YandexClientError, YandexUnexpectedReplyError
from ycli.yandex.models import WIRE

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    import httpx2

    from ycli.yandex.core.pagination import Pagination


class Effect(enum.StrEnum):
    """What a call does to the server; the retry policy and the MCP hints read it."""

    READ = "read"
    WRITE = "write"
    IDEMPOTENT_WRITE = "idempotent_write"
    DESTRUCTIVE = "destructive"


# A request carries the endpoint it was built from, and every page of a listing the listing.
ENDPOINT_EXTENSION = "ycli.endpoint"
PAGED_EXTENSION = "ycli.paged"
_EFFECT_BY_METHOD: dict[HTTPMethod, Effect] = {
    HTTPMethod.GET: Effect.READ,
    HTTPMethod.HEAD: Effect.READ,
    HTTPMethod.OPTIONS: Effect.READ,
    HTTPMethod.PUT: Effect.IDEMPOTENT_WRITE,
    HTTPMethod.PATCH: Effect.IDEMPOTENT_WRITE,
    HTTPMethod.DELETE: Effect.DESTRUCTIVE,
    HTTPMethod.POST: Effect.WRITE,
}


def segment(value: object) -> str:
    """One URL path segment from a caller's value, percent-escaped.

    Escaping alone does not keep a value in its place: Yandex servers decode ``%2F`` before
    routing, so :func:`check_path` rejects the request that such a value produces.

    Args:
        value: The caller's value.

    Returns:
        The percent-escaped segment.

    Examples:
        >>> segment("TEST 1")
        'TEST%201'
    """
    return quote(str(value), safe="")


def check_path(raw_path: str) -> None:
    """Refuse a percent-encoded URL path that the server would route to another endpoint.

    The server decodes ``%2F`` and ``%5C`` and then resolves ``.``/``..``, so an issue key such
    as ``../queues/DE`` turns ``PATCH issues/{key}`` into ``PATCH queues/DE``. No Yandex path
    needs a backslash, an escaped separator, an empty segment or a dot segment, so all are
    refused.

    Args:
        raw_path: The percent-encoded URL path.

    Raises:
        YandexClientError: The path would be routed to another endpoint.

    Examples:
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
        or "\\" in raw_path
        or "//" in raw_path
        or any(part in {".", ".."} for part in segments)
    ):
        # violation(arch-8): refuses a path before any request is sent
        raise YandexClientError(f"refusing a path that leaves its endpoint: {raw_path}")


type _Scalar = str | int | float | bool | None
#: What a query parameter may be; ``None`` is dropped, a list repeats the name.
type QueryValue = _Scalar | Sequence[_Scalar]


@cache
def _adapter(response_type: Any) -> TypeAdapter[Any]:
    """One TypeAdapter per response type: building it is the expensive part of parsing."""
    return TypeAdapter(response_type)


@dataclass(frozen=True, slots=True)
class Endpoint[T]:
    """An API operation: ``method`` + ``path`` (relative to the service's base URL) and its I/O.

    ``params`` with a ``None`` value are dropped, so optional query parameters can be passed
    through unconditionally; a value that is not a string, a number, a boolean or a list of
    them (a dict, a set, bytes) fails here, at construction. ``json`` is the request body: a
    request model, dumped here and nowhere else (API field names, unset fields left out), or
    plain JSON data.
    ``files`` sends a ``multipart/form-data`` body (field name →
    ``(filename, bytes)``). ``response_type=None`` means the response body is ignored and
    ``bytes`` returns it raw; ``parser`` reads a response that is not one JSON type.
    ``follow_redirects=False`` hands a redirect to ``parser`` instead of following it (a status
    read that redirects to the finished file). ``effect`` is what the call does to the server:
    stated explicitly, or implied by the method when left out. An unknown method fails here, at
    construction.
    """

    method: HTTPMethod
    path: str
    response_type: type[T] | None = None
    _: KW_ONLY
    params: Mapping[str, QueryValue] = field(default_factory=dict)
    json: Any = None
    content: bytes | None = None
    files: Mapping[str, tuple[str, bytes]] | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    effect: Effect | None = None
    parser: Callable[[httpx2.Response], T] | None = None
    follow_redirects: bool = True

    def __post_init__(self) -> None:
        implied = _EFFECT_BY_METHOD.get(self.method)
        if implied is None:
            known = ", ".join(_EFFECT_BY_METHOD)
            raise ValueError(f"unknown HTTP method {self.method!r}; expected one of {known}")
        if self.effect is None:
            # A frozen dataclass can fill a derived field only this way (the documented idiom).
            object.__setattr__(self, "effect", implied)
        for name, value in self.params.items():
            items = value if isinstance(value, list | tuple) else [value]
            if not all(item is None or isinstance(item, str | int | float) for item in items):
                # httpx would send the text of the Python object (``%7B%27k%27…``).
                raise TypeError(
                    f"the query parameter {name!r} of {self.method} {self.path} is a "
                    f"{type(value).__name__}; a query takes a string, a number, a boolean or a "
                    "list of them"
                )

    @property
    def idempotent(self) -> bool:
        """Safe to send twice — the retry policy re-sends only these after a 5xx or lost link."""
        return self.effect in {Effect.READ, Effect.IDEMPOTENT_WRITE}

    @property
    def body(self) -> Any:
        """The JSON the request carries: ``json`` itself, or the dump of a request model.

        A model is dumped as a request body (``ycli.yandex.models.WIRE``): under the API's field
        names, without the optional fields left unset.

        Examples:
            >>> from ycli.yandex.models import RequestBody
            >>> class Rename(RequestBody):
            ...     name: str
            ...     note: str | None = None
            >>> Endpoint(HTTPMethod.PATCH, "boards/7", json=Rename(name="Sprint")).body
            {'name': 'Sprint'}
        """
        return to_jsonable_python(self.json, context=WIRE)

    def request(self, client: httpx2.Client | httpx2.AsyncClient) -> httpx2.Request:
        """A native request built by ``client``: its base URL and default headers apply."""
        params = {name: value for name, value in self.params.items() if value is not None}
        return client.build_request(
            self.method,
            self.path,
            params=params or None,
            json=self.body,
            content=self.content,
            files=self.files,
            headers=dict(self.headers) or None,
            extensions={ENDPOINT_EXTENSION: self},
        )

    def parse(self, response: httpx2.Response) -> T:
        """The response body as ``response_type`` (``None`` when the endpoint ignores it)."""
        if self.parser is None and self.response_type is None:
            return cast("T", None)
        if self.parser is None and self.response_type is bytes:
            return cast("T", response.content)
        try:
            if self.parser is not None:
                return self.parser(response)
            return _adapter(self.response_type).validate_json(response.content)
        except ValidationError as exc:
            fields = "; ".join(
                f"{'.'.join(str(part) for part in error['loc']) or 'reply'}: {error['msg']}"
                for error in exc.errors()
            )
            raise YandexUnexpectedReplyError(
                f"the reply to {self.method} {self.path} does not fit what ycli expects ({fields})",
                url=str(response.url),
            ) from exc


def RPC[T](  # noqa: N802 - reads as the kind of call it writes, beside ``Endpoint``
    name: str,
    response_type: type[T] | None = None,
    *,
    json: Any = None,
    effect: Effect,
    parser: Callable[[httpx2.Response], T] | None = None,
) -> Endpoint[T]:
    """An operation of an RPC API: ``POST rpc/<name>`` with its arguments in the body.

    It is one more way to write an :class:`Endpoint`, not another kind of request. Every
    operation of such an API is a ``POST``, so the method says nothing about what the call does:
    ``effect`` has no default here and is always named.

    Args:
        name: The operation's own name (``getDashboard``).
        response_type: The type the reply parses into; ``None`` ignores the reply.
        json: The request body: a request model or plain JSON data.
        effect: What the call does to the server.
        parser: Reads a reply that is not one JSON type.

    Returns:
        The endpoint that sends the call.

    Examples:
        >>> get = RPC("getDashboard", json={"dashboardId": "d1"}, effect=Effect.READ)
        >>> (get.method.value, get.path, get.idempotent)
        ('POST', 'rpc/getDashboard', True)
    """
    return Endpoint(
        HTTPMethod.POST,
        f"rpc/{segment(name)}",
        response_type,
        json=json,
        effect=effect,
        parser=parser,
    )


@dataclass(frozen=True, slots=True)
class Paged[P, I]:
    """A paginated listing: the first-page endpoint, how to page it, and how to read a page.

    ``P`` is the page type the endpoint parses into; ``items_of`` pulls the ``I`` items out of it.
    """

    endpoint: Endpoint[P]
    pagination: Pagination
    items_of: Callable[[P], Sequence[I]]
