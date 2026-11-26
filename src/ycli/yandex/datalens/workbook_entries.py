"""What the DataLens kinds of ``ycli sync`` share: an entry of a workbook as its file reads it."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import ConfigDict, Field

from ycli.yandex.models import APIModel, RequestBody
from ycli.yandex.sync.marks import Place

if TYPE_CHECKING:
    import httpx2

    from ycli.yandex.core.endpoint import Endpoint


class EntryInWorkbook(APIModel):
    """An entry of a workbook, read: what ties it to its file, beside the content of its kind.

    DataLens answers no name, only a ``key`` that ends in it (``2356…/sales``); ``name`` is
    that last part, and it is where the file lies.
    """

    # The content of a kind is a closed request body; what DataLens adds to a reply is kept.
    model_config = ConfigDict(extra="allow")

    entry_id: str | None = Field(default=None, alias="entryId", description="The entry's id.")
    rev_id: str | None = Field(default=None, alias="revId", description="The revision read.")
    workbook_id: str | None = Field(
        default=None, alias="workbookId", description="The workbook it lies in."
    )
    key: str | None = Field(default=None, description="Its key: an id and its name.")
    saved_id: str | None = Field(
        default=None, alias="savedId", description="The revision saved last."
    )
    published_id: str | None = Field(
        default=None, alias="publishedId", description="The revision everyone sees."
    )
    name: Annotated[str | None, Place()] = Field(
        default=None, description="Its name in the workbook: the name of its file."
    )


class LinkLeftOut(RequestBody):
    """The id and revision of an entry, left out of its content: they are the link of a file.

    Put first among the bases of a generated entry of a write, it makes that entry the content of
    a file: a closed body in which neither can hold a value, so neither is written or sent.
    """

    entry_id: None = Field(default=None, alias="entryId", description="The link's, never content.")
    rev_id: None = Field(default=None, alias="revId", description="The link's, never sent.")


def unpublished_draft(entry: EntryInWorkbook) -> str | None:
    """Why an entry must not be published over now: a draft saved after what everyone sees.

    Args:
        entry: The entry, read.

    Returns:
        The reason; ``None`` when what was saved last is what is published.

    Examples:
        >>> unpublished_draft(EntryInWorkbook(savedId="d1", publishedId="r1"))
        'unpublished draft in DataLens; publish or discard it first'
        >>> unpublished_draft(EntryInWorkbook(savedId="r1", publishedId="r1")) is None
        True
    """
    if entry.saved_id == entry.published_id:
        return None
    return "unpublished draft in DataLens; publish or discard it first"


def as_entry[E: EntryInWorkbook](request: Endpoint[Any], model: type[E]) -> Endpoint[E]:
    """``request`` with its reply read as the entry it holds, named by the end of its key.

    Args:
        request: A read or a write of one entry, whose reply holds it under ``entry``.
        model: The entry as its kind reads it.

    Returns:
        The same request; its reply is the entry.

    Examples:
        >>> import httpx2
        >>> from ycli.yandex.datalens.charts import endpoints
        >>> request = as_entry(endpoints.editor_delete("ch1"), EntryInWorkbook)
        >>> reply = httpx2.Response(200, json={"entry": {"entryId": "ch1", "key": "9/sales"}})
        >>> request.parse(reply).name
        'sales'
        >>> sent = httpx2.Request("POST", "https://api.datalens.tech/rpc/deleteEditorChart")
        >>> request.parse(httpx2.Response(200, json=["not an entry"], request=sent))
        Traceback (most recent call last):
            ...
        ycli.yandex.errors.YandexUnexpectedReplyError: the reply to POST rpc/deleteEditorChart ...
    """

    def parse(response: httpx2.Response) -> E:
        held = json.loads(response.content)
        entry = model.model_validate(held.get("entry") if isinstance(held, dict) else held)
        return entry.model_copy(update={"name": (entry.key or "").rpartition("/")[2] or None})

    return replace(request, response_type=model, parser=parse)
