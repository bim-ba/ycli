"""Where a listing stopped, as a token the caller hands back to go on.

A token carries its listing: the whole request of the page to ask next, its query and its
body, how many of its items were already given, the organization it was asked in, and what
its way of paging kept from the replies (a scroll: its id and its own token, which release
it). A token of another organization is refused: run as it is under another account, it
would go on with the other's listing. Of the call that goes on, only ``limit``
counts, so a page whose size the limit shapes goes on under another limit. What such a call
cannot go without (a required argument) is given again, and has to be what the token holds:
an argument that differs is refused by its name, never passed over.

A token is no credential: the request it resumes goes out with the caller's own, and its
method, host and path are the operation's, which a token cannot change. What
ties a token to its operation is the fingerprint of that method and path, and the way the
operation pages: a token of one operation, or of one object's listing, cannot continue
another, and where two operations share a path (a search by pages and the same search by a
scroll) the way tells them apart. The address the listing was asked at is written in the token
too, for one use: to name what differs when a token is given at another address. It never
builds a request. The way is written in the token as it is, so a client that
serves both reads which one a token is of (:func:`way_of`).

Examples:
    >>> import httpx2
    >>> first = httpx2.Request("GET", "https://x/v3/boards?perPage=2")
    >>> page = httpx2.Request("GET", "https://x/v3/boards?perPage=2&id=7")
    >>> token = encode(
    ...     first, page, way="RelativeIDPagination", skip=1, seen=3, organization="Org: 7"
    ... )
    >>> asked = httpx2.Request("GET", "https://x/v3/boards")
    >>> resumed, state = resume(
    ...     asked,
    ...     first,
    ...     token,
    ...     way="RelativeIDPagination",
    ...     longest=1000,
    ...     organization="Org: 7",
    ... )
    >>> (str(resumed.url), state.skip, state.seen)
    ('https://x/v3/boards?perPage=2&id=7', 1, 3)
    >>> way_of(token, longest=1000)
    'RelativeIDPagination'
"""

import base64
import binascii
import hashlib
import json
import re
from typing import Any, Literal
from urllib.parse import quote, unquote

import httpx2
from pydantic import ConfigDict, Field, ValidationError

from ycli.yandex.core.pagination import Pagination
from ycli.yandex.errors import YandexInvalidRequestError
from ycli.yandex.models import RequestBody

NOT_A_TOKEN = "this is not a token a listing gave: start again without it"
#: A token of the first format, which names no organization: it is not guessed at.
FROM_BEFORE = (
    "this token was given by an earlier version of ycli: start the listing again without it"
)
OF_ANOTHER_ORGANIZATION = (
    "this token is of another organization ({}) than this call ({}): "
    "run it under the account that returned it"
)
#: A token given to another operation, or to the same one at another address (another issue,
#: another page): the address the call asks at is named, the token holds none to compare.
OF_ANOTHER = (
    "this token is of another listing than {} {}: give it to the call that returned it, "
    "with what that call named in its address"
)
#: The same address, taken another way: a search by pages given the token of one by a scroll.
OF_ANOTHER_WAY = (
    "this token is of the same listing taken another way ({}, where this call takes it by {}): "
    "give it to the call that returned it"
)
#: What a call that goes on is answered when an argument it repeats is not the token's.
DIFFERS = "with `next`, what is given again must be what the token holds; it differs in: {}"
#: The same, where the argument is a part of the address: both values are named.
DIFFERS_AT = (
    "with `next`, what is given again must be what the token holds; it differs in the address: {}"
)
#: The one rule of going on, in the words of every place that says it: the help of `--next`,
#: the description of a tool's `next`, the docstring of an SDK method, and the refusal.
RULE = "the token carries its listing; give what is required again, and nothing else but the limit"
#: What the CLI and the MCP server both answer a call that goes on and changes its listing.
NOTHING_ELSE = f"with `next`, {RULE}"
#: The handles of a listing: what a call that goes on may still give.
HANDLES = frozenset({"limit", "all", "next"})


# A path and a query as they go on the wire, escaped: visible ASCII and nothing else. A path
# begins with `/` and has no `?` and no `#`; a query has no `#`. A token is made of what the
# request holds in that form, so no argument and no link of a service can break the making;
# what is read back is held to the same, so nothing made of it can be anything else.
_PATH = r"^/[!-\"$->@-~]*$"
_QUERY = r"^[!-\"$-~]*$"
# The organization: the name of its header, and its id escaped the same way.
_ORGANIZATION = r"^([A-Za-z][A-Za-z0-9-]{0,39}: [A-Za-z0-9._%-]{1,400})?$"
# Text of a token that a refusal may repeat: short and plain. Anything else is not quoted,
# because a refusal is read on a terminal and by a model, and a token is written far away.
_PLAIN = re.compile(r"[A-Za-z0-9._-]{1,64}")


class Continuation(RequestBody):
    """What a token holds: the page to ask next, and the listing it belongs to.

    Closed and strict: a key a token does not have, or text where a number goes, is no token.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    v: Literal[2] = Field(description="The version of the format.")
    of: str = Field(description="The fingerprint of the operation: its method and its path.")
    # Text a caller far away wrote: held to the characters of a path and of a query here,
    # where it is read, so that nothing made of it can be anything else.
    at: str = Field(
        pattern=_PATH, description="The path the listing was asked at: for a message, no more."
    )
    org: str = Field(
        pattern=_ORGANIZATION,
        description="The organization the listing was asked in; empty for none.",
    )
    way: str = Field(description="How the operation pages: the name of its pagination.")
    query: str = Field(
        pattern=_QUERY, description="The query of the request of the page to ask next."
    )
    body: str = Field(description="The body of that request; empty where it has none.")
    skip: int = Field(ge=0, description="How many items of that page were given already.")
    seen: int = Field(ge=0, description="How many items of the listing were given so far.")
    kept: dict[str, str] = Field(
        repr=False, description="What the way of paging kept from the replies; mostly nothing."
    )


def _fingerprint(first: httpx2.Request) -> str:
    """What makes two calls the same operation: the method, the host and the path.

    Not the query and not the body: a client narrows the page to the limit, so the first
    request of the same listing differs from one limit to another.
    """
    return _print(first.method, first.url.host, _escaped(first))


def _escaped(request: httpx2.Request) -> str:
    """The path of ``request`` as it goes on the wire: every character an argument gave, escaped."""
    return request.url.raw_path.partition(b"?")[0].decode("ascii")


def _named(organization: str) -> str:
    """``Name: id`` with the id escaped: any id a configuration holds fits the token."""
    name, colon, identifier = organization.partition(": ")
    return f"{name}{colon}{quote(identifier, safe='._-')}"


def _quoted(held: str) -> str:
    """Text of a token as a refusal may say it: itself when short and plain, else unquoted."""
    return held if _PLAIN.fullmatch(held) else "another"


def _print(method: str, host: str, path: str) -> str:
    return hashlib.sha256("\n".join([method, host, path]).encode()).hexdigest()[:32]


def encode(
    first: httpx2.Request,
    page: httpx2.Request,
    *,
    way: str,
    skip: int,
    seen: int,
    organization: str = "",
    kept: dict[str, str] | None = None,
) -> str:
    """The token that goes on from ``page``, past its first ``skip`` items.

    Args:
        first: The first request of the listing, which ties the token to it.
        page: The request of the page to ask next.
        way: How the operation pages: the name of its pagination.
        skip: How many items of that page were given already.
        seen: How many items of the listing were given so far, over every call.
        organization: The organization the listing is asked in; empty where none is named.
        kept: What the way of paging kept from the replies (:meth:`Pagination.kept`).

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
        v=2,
        of=_fingerprint(first),
        at=_escaped(first),
        org=_named(organization),
        way=way,
        query=page.url.query.decode(),
        body=page.content.decode(),
        skip=skip,
        seen=seen,
        kept=kept or {},
    )
    return base64.urlsafe_b64encode(state.model_dump_json().encode()).rstrip(b"=").decode()


def _read(token: str, longest: int) -> Continuation:
    """What ``token`` holds; anything that is not a token is refused in one way."""
    if len(token) > longest:
        raise YandexInvalidRequestError(NOT_A_TOKEN)
    try:
        packed = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        written = json.loads(packed)
    except (binascii.Error, ValueError) as error:
        raise YandexInvalidRequestError(NOT_A_TOKEN) from error
    version = written.get("v") if isinstance(written, dict) else None
    if type(version) is not int:  # `2.0` and `True` equal a version and are none
        raise YandexInvalidRequestError(NOT_A_TOKEN)
    if version == 1:
        raise YandexInvalidRequestError(FROM_BEFORE)
    try:
        state = Continuation.model_validate(written)
    except ValidationError as error:
        raise YandexInvalidRequestError(NOT_A_TOKEN) from error
    if state.way not in _ways(Pagination):
        raise YandexInvalidRequestError(NOT_A_TOKEN)
    return state


def _ways(kind: type[Pagination]) -> set[str]:
    """The names of the ways of paging there are: ``kind`` and every kind made of it."""
    return {kind.__name__}.union(*(_ways(made) for made in kind.__subclasses__()))


def _of(state: Continuation, organization: str) -> Continuation:
    """``state``, of a token given in the organization it was returned in; else refused."""
    if state.org != _named(organization):
        name, _, identifier = state.org.partition(": ")
        theirs = f"{name}: {_quoted(identifier)}" if state.org else "none"
        told = OF_ANOTHER_ORGANIZATION.format(theirs, organization or "none")
        raise YandexInvalidRequestError(told)
    return state


def kept_of(token: str, *, longest: int, organization: str = "") -> dict[str, str]:
    """What the way of paging of ``token`` kept from the replies of its listing.

    Args:
        token: What an earlier call returned as ``next``.
        longest: The longest token read.
        organization: The organization of the call; the token has to be of the same.

    Returns:
        What was kept; empty for every way of paging that keeps nothing.
    """
    return _of(_read(token, longest), organization).kept


def _elsewhere(state: Continuation, first: httpx2.Request) -> str:
    """What to tell a token whose fingerprint is not of ``first``: by its address, where it can.

    The address written in the token is believed only when the fingerprint is its own, and is
    compared as text, never asked at and never made a URL of.

    The core does not know which parts of an address an argument filled. One part that
    differs is taken for an argument given again and named; more than one is another
    operation, and is told as that.
    """
    theirs, ours = state.at.split("/"), _escaped(first).split("/")
    own = state.of == _print(first.method, first.url.host, state.at)
    differing = (
        [(held, here) for held, here in zip(theirs, ours, strict=True) if held != here]
        if own and len(theirs) == len(ours)
        else []
    )
    if len(differing) != 1 or not all(differing[0]):
        return OF_ANOTHER.format(first.method, first.url.path)
    pairs = [f"{unquote(here)} (the token holds {_quoted(held)})" for held, here in differing]
    return DIFFERS_AT.format(", ".join(pairs))


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
    asked: httpx2.Request,
    first: httpx2.Request,
    token: str,
    *,
    way: str,
    longest: int,
    organization: str = "",
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
        organization: The organization of the call; the token has to be of the same.

    Returns:
        The request of the page to ask, and what the token holds beside it.

    Raises:
        YandexInvalidRequestError: The token is not one, is of another organization or of
            another listing, or an argument given again is not what the token holds.
    """
    state = _of(_read(token, longest), organization)
    if state.of != _fingerprint(first):
        raise YandexInvalidRequestError(_elsewhere(state, first))
    if state.way != way:
        raise YandexInvalidRequestError(OF_ANOTHER_WAY.format(state.way, way))
    try:
        differing = _differing(asked, state)
    except ValueError as unread:
        raise YandexInvalidRequestError(NOT_A_TOKEN) from unread
    if differing:
        raise YandexInvalidRequestError(DIFFERS.format(", ".join(differing)))
    if state.at != _escaped(first):
        # The fingerprint is of this path, so a token that says another was written over.
        raise YandexInvalidRequestError(NOT_A_TOKEN)
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
