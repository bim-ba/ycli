"""Pydantic models for Tracker /issues (Issue + ItemList[Issue] root model)."""

from typing import Any, Literal

from pydantic import ConfigDict, Field, RootModel

from ycli.yandex.models import (  # pydantic resolves field types via get_type_hints() at runtime
    APIModel,
    RequestBody,
)

# ``Issue`` lives with the models several resources share: a checklist change returns one too.
from ycli.yandex.tracker.models import Issue as Issue

#: How a scrolled search orders its results.
ScrollType = Literal["sorted", "unsorted"] | str


class IssueCreate(APIModel):
    """Typed request body for ``POST /issues/`` (create an issue).

    Covers the common fields; ``extra="allow"`` lets any custom (global or queue-local) field
    pass through unvalidated.
    ``type``/``priority`` accept either a bare key string or a ``{"key": ...}`` object (both are
    valid per the Tracker API); the CLI sends the object form.

    Examples:
        >>> IssueCreate(queue="TEST", summary="Do it").model_dump(exclude_none=True)
        {'queue': 'TEST', 'summary': 'Do it'}
    """

    model_config = ConfigDict(extra="allow")

    queue: str = Field(description="Key of the target queue.")
    summary: str = Field(description="Issue title.")
    type: dict[str, str] | str | None = Field(
        default=None, description="Issue type — {'key': ...} object or a bare type key."
    )
    priority: dict[str, str] | str | None = Field(
        default=None, description="Priority — {'key': ...} object or a bare priority key."
    )
    parent: str | None = Field(default=None, description="Parent issue key.")
    description: str | None = Field(default=None, description="Issue description (YFM markdown).")
    tags: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="Tags — a replace list, or an {'add'|'set'|'remove': [...]} operator edit.",
    )


class IssueUpdate(APIModel):
    """Typed request body for ``PATCH /issues/{key}`` (update an issue; only sent fields change).

    ``extra="allow"`` lets any custom field pass through unvalidated. Status is NOT changed
    here — use ``transitions_execute``.

    Examples:
        >>> IssueUpdate(summary="New title").model_dump(exclude_none=True)
        {'summary': 'New title'}
    """

    model_config = ConfigDict(extra="allow")

    summary: str | None = Field(default=None, description="New summary (title).")
    type: dict[str, str] | str | None = Field(
        default=None, description="New issue type — {'key': ...} object or a bare type key."
    )
    priority: dict[str, str] | str | None = Field(
        default=None, description="New priority — {'key': ...} object or a bare priority key."
    )
    parent: str | None = Field(default=None, description="New parent issue key.")
    description: str | None = Field(
        default=None, description="New issue description (YFM markdown)."
    )
    tags: list[str] | dict[str, list[str]] | None = Field(
        default=None,
        description="New tags — a replace list, or an {'add'|'set'|'remove': [...]} operator edit.",
    )


class ScrollClear(RootModel[dict[str, str]]):
    """A bare ``{scrollId: scrollToken}`` mapping — body for ``POST …/scroll/_clear``.

    Each entry releases the server resources of one scrolled ``issues.search`` response.

    Examples:
        >>> ScrollClear({"3ce1-...": "eyJvZmZzZXQi..."}).model_dump()
        {'3ce1-...': 'eyJvZmZzZXQi...'}
    """


class IssueSearch(APIModel):
    """Typed request body for ``POST /issues/_search`` and ``POST /issues/_count``.

    Give ``query`` (the query language) or ``filter`` (field name → value); a body with neither
    matches every issue the caller can see. ``extra="allow"`` passes the API's other keys
    (``keys``, ``queue``, ``order``) through.

    Examples:
        >>> IssueSearch(filter={"queue": "DE"}).filter
        {'queue': 'DE'}
    """

    model_config = ConfigDict(extra="allow")

    query: str | None = Field(default=None, description="A query-language string.")
    filter: dict[str, Any] | None = Field(
        default=None, description="Field name → value the issues must have."
    )


def count_body(
    query: str | None = None, queue: str | None = None, status: str | None = None
) -> IssueSearch:
    """Build the request body for ``POST /issues/_count``.

    When ``query`` is provided it takes precedence and the body is ``{"query": …}``.
    Otherwise a ``{"filter": {…}}`` body is built from the given ``queue``/``status``
    values (an empty filter counts every issue in the org).

    Args:
        query: A query-language string; takes precedence over the filter.
        queue: A queue key to filter by.
        status: A status key to filter by.

    Returns:
        The request body.

    Examples:
        >>> count_body(query="Queue: DE").query
        'Queue: DE'
        >>> count_body(queue="DE", status="open").filter
        {'queue': 'DE', 'status': 'open'}
        >>> count_body().filter
        {}
    """
    if query is not None:
        return IssueSearch(query=query)
    given = (("queue", queue), ("status", status))
    return IssueSearch(filter={name: value for name, value in given if value is not None})


def filter_body(
    *,
    queue: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
    epic: str | None = None,
    type_: str | None = None,
) -> IssueSearch:
    """Build the ``POST /issues/_search`` body for field filters, leaving out the ones not given.

    Args:
        queue: A queue key.
        status: A status key.
        assignee: An assignee login.
        epic: An epic key.
        type_: An issue type key.

    Returns:
        The request body.

    Examples:
        >>> filter_body(queue="DE", type_="bug").filter
        {'queue': 'DE', 'type': 'bug'}
    """
    fields = {"queue": queue, "status": status, "assignee": assignee, "epic": epic, "type": type_}
    return IssueSearch(filter={name: value for name, value in fields.items() if value is not None})


class ImportTask(RequestBody):
    """Typed body for ``POST /issues/_import`` — import one issue, preserving its history.

    Examples:
        >>> ImportTask(
        ...     queue="TEST",
        ...     summary="Test",
        ...     created_at="2017-08-29T12:34:41.740+0000",
        ...     created_by="11",
        ... ).model_dump(exclude_none=True)  # doctest: +NORMALIZE_WHITESPACE
        {'queue': 'TEST', 'summary': 'Test', 'createdAt': '2017-08-29T12:34:41.740+0000',
         'createdBy': '11'}
    """

    queue: str = Field(description="Key of the queue to import the issue into.")
    summary: str = Field(description="Issue title (max 255 characters).")
    created_at: str = Field(
        alias="createdAt",
        description="Original creation time (``YYYY-MM-DDThh:mm:ss.sss±hhmm``); not in the future.",
    )
    created_by: str = Field(
        alias="createdBy", description="Login or id of the original issue author."
    )
    key: str | None = Field(
        default=None, description="Explicit issue key (must belong to the queue)."
    )
    description: str | None = Field(default=None, description="Issue description (YFM markdown).")
    assignee: str | None = Field(default=None, description="Login or id of the assignee.")
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Original last-edit time (only together with ``updated_by``).",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="Login or id of the last editor (only together with ``updated_at``).",
    )
