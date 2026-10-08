"""Where a listing stopped, as a token the caller hands back to go on.

A token carries its listing: the whole request of the page to ask next, its query and its
body, and how many of its items were already given. Of the call that goes on, only ``limit``
counts; its other arguments take no part, so a page whose size the limit shapes goes on under
another limit. A token is no credential: the request it resumes goes out with the caller's
own, and its method, host and path are the operation's, which a token cannot change. What
ties a token to its operation is the fingerprint of that method and path: a token of one
operation, or of one object's listing, cannot continue another.

Examples:
    >>> import httpx2
    >>> first = httpx2.Request("GET", "https://x/v3/boards?perPage=2")
    >>> page = httpx2.Request("GET", "https://x/v3/boards?perPage=2&id=7")
    >>> token = encode(first, page, skip=1)
    >>> resumed, skip = resume(first, token, longest=1000)
    >>> (str(resumed.url), skip)
    ('https://x/v3/boards?perPage=2&id=7', 1)
"""

import base64
import binascii
import hashlib
from typing import Literal

import httpx2
from pydantic import ConfigDict, Field, ValidationError

from ycli.yandex.errors import YandexInvalidRequestError
from ycli.yandex.models import RequestBody

NOT_A_TOKEN = "this is not a token a listing gave: start again without it"
OF_ANOTHER = "this token is of another listing: give it to the operation that returned it"


class Continuation(RequestBody):
    """What a token holds: the page to ask next, and the listing it belongs to.

    Closed and strict: a key a token does not have, or text where a number goes, is no token.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    v: Literal[1] = Field(description="The version of the format.")
    of: str = Field(description="The fingerprint of the operation: its method and its path.")
    query: str = Field(description="The query of the request of the page to ask next.")
    body: str = Field(description="The body of that request; empty where it has none.")
    skip: int = Field(ge=0, description="How many items of that page were given already.")


def _fingerprint(first: httpx2.Request) -> str:
    """What makes two calls the same operation: the method, the host and the path.

    Not the query and not the body: a client narrows the page to the limit, so the first
    request of the same listing differs from one limit to another.
    """
    held = "\n".join([first.method, first.url.host, first.url.path])
    return hashlib.sha256(held.encode()).hexdigest()[:32]


def encode(first: httpx2.Request, page: httpx2.Request, *, skip: int) -> str:
    """The token that goes on from ``page``, past its first ``skip`` items.

    Args:
        first: The first request of the listing, which ties the token to it.
        page: The request of the page to ask next.
        skip: How many items of that page were given already.

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
        query=page.url.query.decode(),
        body=page.content.decode(),
        skip=skip,
    )
    return base64.urlsafe_b64encode(state.model_dump_json().encode()).rstrip(b"=").decode()


def resume(first: httpx2.Request, token: str, *, longest: int) -> tuple[httpx2.Request, int]:
    """The request ``token`` goes on from, built on the listing's own first request.

    The query and the body are the token's, whole: the arguments of the call that goes on
    shape nothing but the method and the path.

    Args:
        first: The first request of the listing, as the call's arguments build it.
        token: What an earlier call of the same listing returned.
        longest: The longest token read (``HTTPConfig.max_token_length``): a caller far away
            sends it, so it is bounded before it is decoded.

    Returns:
        The request of the page to ask, and how many of its items to pass over.

    Raises:
        YandexInvalidRequestError: The token is not one, or is of another listing.
    """
    if len(token) > longest:
        raise YandexInvalidRequestError(NOT_A_TOKEN)
    try:
        packed = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        state = Continuation.model_validate_json(packed)
    except (binascii.Error, ValueError, ValidationError) as error:
        raise YandexInvalidRequestError(NOT_A_TOKEN) from error
    if state.of != _fingerprint(first):
        raise YandexInvalidRequestError(OF_ANOTHER)
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
    return resumed, state.skip
