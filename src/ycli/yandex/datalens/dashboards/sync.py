"""A dashboard as a file: ``datalens/workbooks/<workbook>/dashboards/<name>.yaml``, published.

DataLens holds an entry under ``entry``, takes its id inside the body of a write and answers no
name of its own, so the operations of the kind are built here on those of ``endpoints.py``.
"""

from typing import Annotated

from pydantic import Field

from ycli.yandex.core.endpoint import Endpoint, Paged
from ycli.yandex.datalens import workbooks
from ycli.yandex.datalens.dashboards import endpoints
from ycli.yandex.datalens.dashboards.models import (
    DashboardContent,
    DashboardCreate,
    DashboardEntry,
    DashboardSaved,
    DashboardUpdate,
)
from ycli.yandex.datalens.workbook_entries import as_entry, unpublished_draft
from ycli.yandex.datalens.workbooks import endpoints as workbook_endpoints
from ycli.yandex.datalens.workbooks.models import EntriesPage, WorkbookEntry
from ycli.yandex.sync.document import Link, as_sent
from ycli.yandex.sync.formats import YAMLFile
from ycli.yandex.sync.kind import CheckedVersion, Kind
from ycli.yandex.sync.marks import Container, Identity, Version


class DashboardLink(Link):
    """What ties the file of a dashboard to its dashboard."""

    entry_id: Annotated[str | None, Identity()] = Field(
        default=None, alias="entryId", description="Id of the dashboard."
    )
    rev_id: Annotated[str | None, Version()] = Field(
        default=None, alias="revId", description="The published revision it was read at."
    )


def find(
    workbook_id: Annotated[str, Container(workbooks)],
) -> Paged[EntriesPage, WorkbookEntry]:
    """The dashboards of a workbook."""
    return workbook_endpoints.entries_list(
        workbook_id,
        include_permissions_info=None,
        only_my=None,
        created_by=None,
        scope="dash",
        order_by=None,
        filters=None,
    )


def read(
    workbook_id: Annotated[str, Container(workbooks)], entry_id: Annotated[str, Identity()]
) -> Endpoint[DashboardEntry]:
    """The published dashboard, read in its workbook: DataLens refuses it in any other."""
    request = endpoints.get(
        entry_id,
        rev_id=None,
        include_permissions=None,
        include_links=None,
        include_favorite=None,
        branch="published",
        workbook_id=workbook_id,
    )
    return as_entry(request, DashboardEntry)


def create(
    workbook_id: Annotated[str, Container(workbooks)], body: DashboardEntry
) -> Endpoint[DashboardEntry]:
    """A new dashboard in the workbook, under the name of its file."""
    entry = DashboardCreate.model_validate(as_sent(body) | {"workbookId": workbook_id})
    return as_entry(endpoints.create(entry), DashboardEntry)


def update(
    entry_id: Annotated[str, Identity()], body: DashboardContent
) -> Endpoint[DashboardSaved]:
    """The dashboard, published as the file holds it; no revision goes with it."""
    entry = DashboardUpdate.model_validate(as_sent(body) | {"entryId": entry_id})
    return endpoints.update(entry, mode="publish", lock_token=None)


DASHBOARD = Kind(
    name="datalens/dashboard",
    layout=YAMLFile(),
    link=DashboardLink,
    content=DashboardContent,
    find=find,
    read=read,
    create=create,
    update=update,
    delete=endpoints.delete,
    # DataLens checks no revision on a write (#484): the published one is read and recorded;
    # the content fingerprint guards the write.
    version=CheckedVersion(),
    # A publish of the file would throw away a draft somebody saved in DataLens since.
    holds=unpublished_draft,
)
