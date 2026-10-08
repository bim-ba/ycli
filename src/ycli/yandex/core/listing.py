"""A listing as its caller gets it: the items one by one, and where it stopped.

:class:`Walk` is the walk itself with no I/O in it, so the synchronous and the asynchronous
session page the same way: a session sends ``walk.request``, hands the response to
:meth:`Walk.take` and yields what it returns, until there is no request left.
"""

from collections.abc import AsyncIterator, Callable, Iterator, Sequence
from typing import Any

import httpx2

from ycli.yandex.core import continuation
from ycli.yandex.core.endpoint import Paged
from ycli.yandex.models import Listed


class Walk[P, I]:
    """One listing being walked: the request to send next, and what is known when it ends.

    A listing stops at ``limit`` items. Where a page can be asked for again it is cut in the
    middle and the token passes over what was given; where it cannot (``replayable`` is
    false), only whole pages are given: as many as fit in ``limit``, and never less than one.
    """

    def __init__(
        self,
        paged: Paged[P, I],
        first: httpx2.Request,
        *,
        limit: int | None,
        token: str | None,
        longest_token: int,
    ) -> None:
        self._paged = paged
        self._first = first
        self._limit = limit
        self._produced = 0
        self._last_page = 0
        self.request: httpx2.Request | None = first
        self._skip = 0
        #: The request about to be sent is the first of a continued listing.
        self.resuming = token is not None
        if token is not None:
            self.request, self._skip = continuation.resume(first, token, longest=longest_token)
        self.truncated = False
        self.next: str | None = None
        self.total: int | None = None

    def _is_first(self, request: httpx2.Request) -> bool:
        return request.url == self._first.url and request.content == self._first.content

    def _stop(self, page: httpx2.Request, skip: int) -> None:
        self.truncated = True
        self.next = continuation.encode(self._first, page, skip=skip)
        self.request = None

    def take(self, response: httpx2.Response) -> Sequence[I]:
        """The items of the page just answered that go to the caller; sets what comes next.

        Args:
            response: The answer to :attr:`request`.

        Returns:
            The items to yield.
        """
        request = self.request
        assert request is not None  # a session asks only while there is a request
        paging = self._paged.pagination
        page: Sequence[I] = self._paged.items_of(self._paged.endpoint.parse(response))
        following = paging.next(request, response, page) if page else None
        self.total = paging.total(response) if self.total is None else self.total
        skipped, self._skip, self.resuming = self._skip, 0, False
        items = page[skipped:]
        room = None if self._limit is None else self._limit - self._produced
        if (
            room is not None
            and len(items) > room
            and (paging.replayable or self._is_first(request))
        ):
            # Cut in the middle: this page is asked again and what was given is passed over.
            self._produced += room
            self._stop(request, skipped + room)
            return items[:room]
        self._produced += len(items)
        self._last_page = len(page)
        left = None if self._limit is None else self._limit - self._produced
        if following is None:
            self.request = None
        elif left is not None and (left <= 0 or (not paging.replayable and left < len(page))):
            # At the limit, or a page that cannot be asked twice would not fit in what is left.
            self._stop(following, 0)
        else:
            self.request = following
        return items


class Listing[I]:
    """The items of a listing, fetched page by page as they are asked for.

    Iterate it once. When the iteration ends, ``truncated`` says whether the listing has more,
    ``next`` is what to give the same call to go on, and ``total`` is how many items the whole
    listing has, where the service says.
    """

    def __init__(self, walk: Walk[Any, I], pages: Callable[[], Iterator[I]]) -> None:
        self._walk = walk
        self._items = pages()

    def __iter__(self) -> Iterator[I]:
        return self._items

    def __next__(self) -> I:
        return next(self._items)

    @property
    def truncated(self) -> bool:
        """Whether the listing has more items than were given."""
        return self._walk.truncated

    @property
    def next(self) -> str | None:
        """What to give the same call to go on from here; ``None`` at the end."""
        return self._walk.next

    @property
    def total(self) -> int | None:
        """How many items the whole listing has, where the service says."""
        return self._walk.total

    def collect(self) -> Listed[I]:
        """Fetch everything that is left and return it with where the listing stopped.

        Returns:
            The items, whether there is more, and the token to go on.
        """
        items = list(self._items)
        return Listed(items=items, truncated=self.truncated, next=self.next, total=self.total)


class AsyncListing[I]:
    """:class:`Listing` for an asynchronous session: ``async for`` over it, once."""

    def __init__(self, walk: Walk[Any, I], pages: Callable[[], AsyncIterator[I]]) -> None:
        self._walk = walk
        self._items = pages()

    def __aiter__(self) -> AsyncIterator[I]:
        return self._items

    async def __anext__(self) -> I:
        return await anext(self._items)

    @property
    def truncated(self) -> bool:
        """Whether the listing has more items than were given."""
        return self._walk.truncated

    @property
    def next(self) -> str | None:
        """What to give the same call to go on from here; ``None`` at the end."""
        return self._walk.next

    @property
    def total(self) -> int | None:
        """How many items the whole listing has, where the service says."""
        return self._walk.total

    async def collect(self) -> Listed[I]:
        """Fetch everything that is left and return it with where the listing stopped.

        Returns:
            The items, whether there is more, and the token to go on.
        """
        items = [item async for item in self._items]
        return Listed(items=items, truncated=self.truncated, next=self.next, total=self.total)
