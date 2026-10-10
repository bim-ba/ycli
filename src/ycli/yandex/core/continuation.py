"""Where a listing stopped, as a token the caller hands back to go on.

A token carries its listing: the whole request of the page to ask next, its query and its
body, and how many of its items were already given. Of the call that goes on, only ``limit``
counts, so a page whose size the limit shapes goes on under another limit. What such a call
cannot go without (a required argument) is given again, and has to be what the token holds:
an argument that differs is refused by its name, never passed over.

A token is no credential: the request it resumes goes out with the caller's own, and its
method, host and path are the operation's, which a token cannot change. What
ties a token to its operation is the fingerprint of that method and path, and the way the
operation pages: a token of one operation, or of one object's listing, cannot continue
another, and where two operations share a path (a search by pages and the same search by a
scroll) the way tells them apart. The way is written in the token as it is, so a client that
serves both reads which one a token is of (:func:`way_of`).

Examples:
    >>> import httpx2
    >>> first = httpx2.Request("GET", "https://x/v3/boards?perPage=2")
    >>> page = httpx2.Request("GET", "https://x/v3/boards?perPage=2&id=7")
    >>> token = encode(first, page, way="RelativeIDPagination", skip=1, seen=3)
    >>> asked = httpx2.Request("GET", "https://x/v3/boards")
    >>> resumed, state = resume(asked, first, token, way="RelativeIDPagination", longest=1000)
    >>> (str(resumed.url), state.skip, state.seen)
    ('https://x/v3/boards?perPage=2&id=7', 1, 3)
    >>> way_of(token, longest=1000)
    'RelativeIDPagination'
"""

import base64
import binascii
import hashlib
import json
from typing import Any, Literal

import httpx2
from pydantic import ConfigDict, Field, ValidationError

from ycli.yandex.errors import YandexInvalidRequestError
from ycli.yandex.models import RequestBody

NOT_A_TOKEN = "this is not a token a listing gave: start again without it"
#: A token given to another operation, or to the same one at another address (another issue,
#: another page): the address the call asks at is named, the token holds none to compare.
OF_ANOTHER = (
    "this token is of another listing than {} {}: give it to the call that returned it, "
    "with what that call named in its address"
)
#: What a call that goes on is answered when an argument it repeats is not the token's.
DIFFERS = "with `next`, what is given again must be what the token holds; it differs in: {}"
#: The one rule of going on, in the words of every place that says it: the help of `--next`,
#: the description of a tool's `next`, the docstring of an SDK method, and the refusal.
RULE = "the token carries its listing; give what is required again, and nothing else but the limit"
#: What the CLI and the MCP server both answer a call that goes on and changes its listing.
NOTHING_ELSE = f"with `next`, {RULE}"
#: The handles of a listing: what a call that goes on may still give.
HANDLES = frozenset({"limit", "all", "next"})


class Continuation(RequestBody):
    """What a token holds: the page to ask next, and the listing it belongs to.

    Closed and strict: a key a token does not have, or text where a number goes, is no token.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    v: Literal[1] = Field(description="The version of the format.")
    of: str = Field(description="The fingerprint of the operation: its method and its path.")
    way: str = Field(description="How the operation pages: the name of its pagination.")
    query: str = Field(description="The query of the request of the page to ask next.")
    body: str = Field(description="The body of that request; empty where it has none.")
    skip: int = Field(ge=0, description="How many items of that page were given already.")
    seen: int = Field(ge=0, description="How many items of the listing were given so far.")


def _fingerprint(first: httpx2.Request) -> str:
    """What makes two calls the same operation: the method, the host and the path.

    Not the query and not the body: a client narrows the page to the limit, so the first
    request of the same listing differs from one limit to another.
    """
    held = "\n".join([first.method, first.url.host, first.url.path])
    return hashlib.sha256(held.encode()).hexdigest()[:32]


def encode(first: httpx2.Request, page: httpx2.Request, *, way: str, skip: int, seen: int) -> str:
    """The token that goes on from ``page``, past its first ``skip`` items.

    Args:
        first: The first request of the listing, which ties the token to it.
        page: The request of the page to ask next.
        way: How the operation pages: the name of its pagination.
        skip: How many items of that page were given already.
        seen: How many items of the listing were given so far, over every call.

    Returns:
        The token, safe in a URL and on a command line.

    Raises:
        YandexInvalidRequestError: The page lies at another path than its listing: a token
            has no path to give, so such a listing cannot be continued.
    """
    # Every way of paging keeps the path of its listing (the two that follow a link of the
    # service carry only its query over). A token that could name a path could aim a request.
    if page.url.path != first.url.path:
        raise YandexInvalidRequestError("a page at another path than its listing has no token")
    state = Continuation(
        v=1,
        of=_fingerprint(first),
        way=way,
        query=page.url.query.decode(),
        body=page.content.decode(),
        skip=skip,
        seen=seen,
    )
    return base64.urlsafe_b64encode(state.model_dump_json().encode()).rstrip(b"=").decode()


def _read(token: str, longest: int) -> Continuation:
    """What ``token`` holds; anything that is not a token is refused in one way."""
    if len(token) > longest:
        raise YandexInvalidRequestError(NOT_A_TOKEN)
    try:
        packed = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        return Continuation.model_validate_json(packed)
    except (binascii.Error, ValueError, ValidationError) as error:
        raise YandexInvalidRequestError(NOT_A_TOKEN) from error


def way_of(token: str, *, longest: int) -> str:
    """How the operation that gave ``token`` pages: the name of its pagination.

    For a client method that serves two operations of one path and must go on with the one
    the token is of.

    Args:
        token: What an earlier call returned as ``next``.
        longest: The longest token read.

    Returns:
        The name of the pagination.
    """
    return _read(token, longest).way


def _held(given: Any, held: Any) -> bool:
    """Whether ``held`` has ``given`` in it: nothing is in anything, an object key by key.

    Args:
        given: A value of the request the call that goes on builds.
        held: The value at the same place of the request the token holds.

    Returns:
        Whether the two say the same, as far as ``given`` says anything.

    Examples:
        >>> _held({"filter": {}, "expand": None}, {"filter": {"queue": "DE"}, "page": 2})
        True
        >>> _held({"query": "a"}, {"query": "b"})
        False
    """
    if given is None:
        return True
    if isinstance(given, dict):
        mapping = held if isinstance(held, dict) else {}
        return all(_held(value, mapping.get(key)) for key, value in given.items())
    return given == held


def _differing(asked: httpx2.Request, state: Continuation) -> list[str]:
    """The names of what ``asked`` gives that the token's request does not hold the same."""
    held_query = httpx2.QueryParams(state.query)
    names = [
        name
        for name in dict.fromkeys(asked.url.params.keys())
        if asked.url.params.get_list(name) != held_query.get_list(name)
    ]
    if asked.content:
        given, held = json.loads(asked.content), json.loads(state.body or "null")
        whole = given if isinstance(given, dict) else {"the body": given}
        mapping = held if isinstance(held, dict) else {"the body": held}
        names += [name for name, value in whole.items() if not _held(value, mapping.get(name))]
    return names


def resume(
    asked: httpx2.Request, first: httpx2.Request, token: str, *, way: str, longest: int
) -> tuple[httpx2.Request, Continuation]:
    """The request ``token`` goes on from, built on the listing's own first request.

    The query and the body are the token's, whole: the arguments of the call that goes on
    shape nothing but the method and the path, and what they give has to be in the token.

    Args:
        asked: The request of the operation before its pagination shaped it: what the
            arguments of the call that goes on give, and nothing of the page.
        first: The first request of the listing, as the call's arguments build it.
        token: What an earlier call of the same listing returned.
        way: How the operation pages: the name of its pagination.
        longest: The longest token read (``HTTPConfig.max_token_length``): a caller far away
            sends it, so it is bounded before it is decoded.

    Returns:
        The request of the page to ask, and what the token holds beside it.

    Raises:
        YandexInvalidRequestError: The token is not one, is of another listing, or an
            argument given again is not what the token holds.
    """
    state = _read(token, longest)
    if state.of != _fingerprint(first) or state.way != way:
        raise YandexInvalidRequestError(OF_ANOTHER.format(first.method, first.url.path))
    try:
        differing = _differing(asked, state)
    except ValueError as unread:
        raise YandexInvalidRequestError(NOT_A_TOKEN) from unread
    if differing:
        raise YandexInvalidRequestError(DIFFERS.format(", ".join(differing)))
    headers = {
        name: value
        for name, value in first.headers.items()
        if name.lower() not in {"host", "content-length"}
    }
    resumed = httpx2.Request(
        first.method,
        first.url.copy_with(query=state.query.encode()),
        headers=headers,
        content=state.body.encode(),
        extensions=first.extensions,
    )
    return resumed, state
