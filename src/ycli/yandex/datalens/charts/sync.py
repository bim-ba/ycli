"""An Editor chart as a file: ``datalens/workbooks/<workbook>/charts/<name>.yaml``, published.

DataLens holds an entry under ``entry``, takes its id inside the body of a write and answers no
name of its own, so the operations of the kind are built here on those of ``endpoints.py``.
"""

from typing import Annotated, Any, get_args

from pydantic import Field, TypeAdapter

from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.datalens import workbooks
from ycli.yandex.datalens.charts import endpoints
from ycli.yandex.datalens.charts.models import (
    EditorChartContent,
    EditorChartCreate,
    EditorChartEntry,
    EditorChartSaved,
    EditorChartUpdate,
)
from ycli.yandex.datalens.workbook_entries import as_entry
from ycli.yandex.datalens.workbooks import endpoints as workbook_endpoints
from ycli.yandex.datalens.workbooks.models import EntriesPage, WorkbookEntry
from ycli.yandex.sync.document import Link, as_sent
from ycli.yandex.sync.formats import YAMLFile
from ycli.yandex.sync.kind import CheckedVersion, Kind
from ycli.yandex.sync.marks import Container, Identity, Version

#: The kinds of Editor chart DataLens describes; a chart of the wizard or of QL is none of them.
EDITOR_TYPES = frozenset(
    get_args(variant.model_fields["type"].annotation)[0]
    for variant in get_args(EditorChartUpdate)
    if "type" in variant.model_fields
)


class EditorChartLink(Link):
    """What ties the file of an Editor chart to its chart."""

    entry_id: Annotated[str | None, Identity()] = Field(
        default=None, alias="entryId", description="Id of the chart."
    )
    rev_id: Annotated[str | None, Version()] = Field(
        default=None, alias="revId", description="The published revision it was read at."
    )


def find(
    workbook_id: Annotated[str, Container(workbooks)],
) -> Paged[EntriesPage, WorkbookEntry]:
    """The Editor charts of a workbook: its widgets, without those of the wizard and QL."""
    listing = workbook_endpoints.entries_list(
        workbook_id,
        include_permissions_info=None,
        only_my=None,
        created_by=None,
        scope="widget",
        order_by=None,
        filters=None,
    )
    every = listing.items_of
    return Paged(
        listing.endpoint,
        listing.pagination,
        lambda page: [entry for entry in every(page) if entry.type in EDITOR_TYPES],
    )


def read(
    workbook_id: Annotated[str, Container(workbooks)], entry_id: Annotated[str, Identity()]
) -> Endpoint[EditorChartEntry]:
    """The published chart, read in its workbook: DataLens refuses it in any other."""
    request = endpoints.editor_get(
        entry_id,
        workbook_id=workbook_id,
        rev_id=None,
        include_permissions=None,
        include_links=None,
        include_favorite=None,
        branch="published",
    )
    return as_entry(request, EditorChartEntry)


def create(
    workbook_id: Annotated[str, Container(workbooks)], body: EditorChartEntry
) -> Endpoint[EditorChartEntry]:
    """A new chart in the workbook, under the name of its file."""
    entry: Any = as_sent(body) | {"workbookId": workbook_id}
    request = endpoints.editor_create(TypeAdapter(EditorChartCreate).validate_python(entry))
    return as_entry(request, EditorChartEntry)


def update(
    entry_id: Annotated[str, Identity()], body: EditorChartContent
) -> Endpoint[EditorChartSaved]:
    """The chart, published as the file holds it; no revision goes with it."""
    entry: Any = as_sent(body) | {"entryId": entry_id}
    return endpoints.editor_update(
        TypeAdapter(EditorChartUpdate).validate_python(entry), mode="publish"
    )


EDITOR_CHART = Kind(
    name="datalens/editor-chart",
    layout=YAMLFile(),
    link=EditorChartLink,
    content=EditorChartContent,
    find=find,
    read=read,
    create=create,
    update=update,
    delete=endpoints.editor_delete,
    # DataLens checks no revision on a write (#484): the published one is read and compared.
    version=CheckedVersion(),
)
