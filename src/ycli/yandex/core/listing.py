"""A listing as its caller gets it: the items one by one, and where it stopped.

:class:`Walk` is the walk itself with no I/O in it, so the synchronous and the asynchronous
session page the same way: a session sends ``walk.request``, hands the response to
:meth:`Walk.take` and yields what it returns, until there is no request left.
"""

from collections.abc import AsyncIterator, Callable, Iterable, Iterator, Sequence
from typing import Any

import httpx2

from ycli.yandex.core import continuation
from ycli.yandex.core.endpoint import Paged
from ycli.yandex.errors import YandexInvalidRequestError
from ycli.yandex.models import Listed


class Walk[P, I]:
    """One listing being walked: the request to send next, and what is known when it ends.

    A listing stops at ``limit`` items. Where a page can be asked for again it is cut in the
    middle and the token passes over what was given; where it cannot (``replayable`` is
    false), only whole pages are given: as many as fit in ``limit``, and never less than one.

    ``truncated`` says the walk stopped at the limit before the listing was known to end:
    there may be more, and ``next`` goes on. Where the service says how many items the listing
    has and that many were given, over this call and the ones before it, the listing ended.
    """

    def __init__(
        self,
        paged: Paged[P, I],
        asked: httpx2.Request,
        first: httpx2.Request,
        *,
        limit: int | None,
        token: str | None,
        longest_token: int,
    ) -> None:
        self._paged = paged
        self._way = type(paged.pagination).__name__
        self._first = first
        self._limit = limit
        self._produced = 0
        #: Given by the calls before this one, as the token says.
        self._before = 0
        self.request: httpx2.Request | None = first
        self._skip = 0
        #: The request about to be sent is the first of a continued listing.
        self.resuming = token is not None
        if token is not None:
            self.request, state = continuation.resume(
                asked, first, token, way=self._way, longest=longest_token
            )
            self._skip, self._before = state.skip, state.seen
        self.truncated = False
        self.next: str | None = None
        self.total: int | None = None

    @property
    def seen(self) -> int:
        """How many items of the listing were given so far, by this call and the ones before."""
        return self._before + self._produced

    def _is_first(self, request: httpx2.Request) -> bool:
        return request.url == self._first.url and request.content == self._first.content

    def _stop(self, page: httpx2.Request, skip: int) -> None:
        self.request = None
        if self.total is not None and self.seen >= self.total:
            return  # the service said how many there are, and that many were given
        self.truncated = True
        self.next = continuation.encode(self._first, page, way=self._way, skip=skip, seen=self.seen)

    def cut(self) -> None:
        """Stop before the request about to be sent: the listing is truncated and goes on there."""
        request = self.request
        assert request is not None  # a session cuts only a walk that would ask again
        self._stop(request, 0)

    def _following(
        self,
        request: httpx2.Request,
        response: httpx2.Response,
        page: Sequence[I],
        *,
        resumed: bool,
    ) -> httpx2.Request | None:
        """The request of the page after ``page``; a token's unreadable state is told as such."""
        if not page:
            return None
        try:
            return self._paged.pagination.next(request, response, page)
        except (KeyError, ValueError, TypeError) as unread:
            if not resumed:
                raise
            # The token named a request this way of paging cannot go on from.
            raise YandexInvalidRequestError(continuation.NOT_A_TOKEN) from unread

    def take(self, response: httpx2.Response) -> Sequence[I]:
        """The items of the page just answered that go to the caller; sets what comes next.

        Args:
            response: The answer to :attr:`request`.

        Returns:
            The items to yield.

        A walk that went on from a token whose state its way of paging cannot read is refused
        as "not a token" (``YandexInvalidRequestError``).
        """
        request = self.request
        assert request is not None  # a session asks only while there is a request
        paging = self._paged.pagination
        page: Sequence[I] = self._paged.items_of(self._paged.endpoint.parse(response))
        skipped, self._skip, resumed, self.resuming = self._skip, 0, self.resuming, False
        following = self._following(request, response, page, resumed=resumed)
        self.total = paging.total(response) if self.total is None else self.total
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
        left = None if self._limit is None else self._limit - self._produced
        if following is None:
            self.request = None
        elif left is not None and (left <= 0 or (not paging.replayable and left < len(page))):
            # At the limit, or a page that cannot be asked twice would not fit in what is left.
            self._stop(following, 0)
        else:
            self.request = following
        return items


#: What reading ``next`` or ``truncated`` of a listing that was not read to its end is told.
NOT_READ = "the listing is not read to its end: iterate it, or call collect(), and then ask"


class _Whole:
    """What a listing that was given whole knows of itself: it ended, and nothing goes on."""

    truncated = False
    next: str | None = None
    total: int | None = None
    seen = 0


class Listing[I]:
    """The items of a listing, fetched page by page as they are asked for.

    Iterate it once. When the iteration ends, ``truncated`` says whether the listing has more,
    ``next`` is what to give the same call to go on, and ``total`` is how many items the whole
    listing has, where the service says. Before it ends neither of the first two is known, and
    asking for one is a mistake (``RuntimeError``): "nothing yet" must not read as "it ended".
    """

    def __init__(self, walk: Walk[Any, I] | _Whole, pages: Callable[[], Iterator[I]]) -> None:
        self._walk = walk
        self._ended = False
        self._items = self._read(pages())

    def _read(self, items: Iterator[I]) -> Iterator[I]:
        yield from items
        self._ended = True

    def _stopped(self) -> Walk[Any, I] | _Whole:
        if not self._ended:
            raise RuntimeError(NOT_READ)
        return self._walk

    @classmethod
    def whole(cls, items: Iterable[I]) -> "Listing[I]":
        """A listing that is all there already: one reply of a service that does not page it.

        Args:
            items: Every item of the listing.

        Returns:
            The listing; it is not truncated and has nothing to go on from.

        Examples:
            >>> listing = Listing.whole(["a", "b"])
            >>> (list(listing), listing.truncated, listing.next)
            (['a', 'b'], False, None)
        """
        return cls(_Whole(), lambda: iter(items))

    def __iter__(self) -> Iterator[I]:
        return self._items

    def __next__(self) -> I:
        return next(self._items)

    @property
    def truncated(self) -> bool:
        """Whether the listing has more items than were given."""
        return self._stopped().truncated

    @property
    def next(self) -> str | None:
        """What to give the same call to go on from here; ``None`` at the end."""
        return self._stopped().next

    @property
    def total(self) -> int | None:
        """How many items the whole listing has, where the service says."""
        return self._walk.total

    @property
    def seen(self) -> int:
        """How many items were given so far, by this call and the ones it went on from."""
        return self._walk.seen

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
        self._ended = False
        self._items = self._read(pages())

    async def _read(self, items: AsyncIterator[I]) -> AsyncIterator[I]:
        async for item in items:
            yield item
        self._ended = True

    def _stopped(self) -> Walk[Any, I]:
        if not self._ended:
            raise RuntimeError(NOT_READ)
        return self._walk

    def __aiter__(self) -> AsyncIterator[I]:
        return self._items

    async def __anext__(self) -> I:
        return await anext(self._items)

    @property
    def truncated(self) -> bool:
        """Whether the listing has more items than were given."""
        return self._stopped().truncated

    @property
    def next(self) -> str | None:
        """What to give the same call to go on from here; ``None`` at the end."""
        return self._stopped().next

    @property
    def total(self) -> int | None:
        """How many items the whole listing has, where the service says."""
        return self._walk.total

    @property
    def seen(self) -> int:
        """How many items were given so far, by this call and the ones it went on from."""
        return self._walk.seen

    async def collect(self) -> Listed[I]:
        """Fetch everything that is left and return it with where the listing stopped.

        Returns:
            The items, whether there is more, and the token to go on.
        """
        items = [item async for item in self._items]
        return Listed(items=items, truncated=self.truncated, next=self.next, total=self.total)
