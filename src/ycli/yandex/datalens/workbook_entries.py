"""What the DataLens kinds of ``ycli sync`` share: an entry of a workbook as its file reads it."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import ConfigDict, Field

from ycli.yandex.models import APIModel
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
    name: Annotated[str | None, Place()] = Field(
        default=None, description="Its name in the workbook: the name of its file."
    )


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
