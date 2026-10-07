"""DataLens HTML pages FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    EntryID,
    PermissionsInfo,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.htmlpages.models import (
    HTMLPage,
    HTMLPageAnnotation,
    HTMLPageCreated,
    HTMLPagePreview,
    HTMLPageSaved,
    HTMLPageUpdate,
    PreviewLanguage,
    PreviewTheme,
)
from ycli.yandex.datalens.models import RevisionBranch
from ycli.yandex.models import Ack

mcp = new_server("datalens-htmlpages")

PageBranch = Annotated[
    RevisionBranch | None,
    Field(description="The version to read when no revision is named: `saved` or `published`."),
]
PageRevision = Annotated[
    str | None, Field(description="One revision, as it is; give it or `branch`, not both.")
]


@mcp.tool(name="htmlpages_get", annotations={**RO, "title": "Get DataLens HTML page"})
def get(
    entry_id: EntryID,
    rev_id: PageRevision = None,
    branch: PageBranch = None,
    include_permissions: PermissionsInfo = None,
    include_favorite: Annotated[
        bool | None, Field(description="Also say whether the page is a favourite.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> HTMLPage:
    """One HTML page: where it lies and its revisions.

    The reply has no HTML of the page; ``htmlpages_preview_url_get`` gives a link that shows
    it. ``entries_list`` with the scope ``artifact`` finds the pages.
    """
    return client.htmlpages.get(
        entry_id,
        rev_id=rev_id,
        branch=branch,
        include_permissions=include_permissions,
        include_favorite=include_favorite,
    )


@mcp.tool(name="htmlpages_create", annotations={**WRITE, "title": "Create DataLens HTML page"})
def create(
    content: Annotated[str, Field(description="The HTML of the page.")],
    annotation: Annotated[
        HTMLPageAnnotation | None, Field(description="A description of the page.")
    ] = None,
    key: Annotated[str | None, Field(description="The page's key, in a folder.")] = None,
    workbook_id: Annotated[
        str | None, Field(description="The workbook to create the page in.")
    ] = None,
    name: Annotated[str | None, Field(description="The page's name, in a workbook.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> HTMLPageCreated:
    """Create an HTML page; the reply has it under ``entry`` and ``warnings`` about its HTML."""
    return client.htmlpages.create(
        content=content, annotation=annotation, key=key, workbook_id=workbook_id, name=name
    )


@mcp.tool(
    name="htmlpages_update",
    annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens HTML page"},
)
def update(
    body: Annotated[
        HTMLPageUpdate,
        Field(
            description="Either new HTML, `{entryId, content, mode}`, or a revision to make "
            "current, `{entryId, revId, mode}`: one of the two, not both."
        ),
    ],
    client: DataLensClient = Depends(datalens_client),
) -> HTMLPageSaved:
    """Save new HTML of a page, or make one of its revisions the current one.

    ``mode`` ``save`` makes a new revision and leaves the public one; ``publish`` shows it to
    everyone. With ``revId``, ``save`` copies that revision as the current draft.
    """
    return client.htmlpages.update(body)


@mcp.tool(
    name="htmlpages_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens HTML page"}
)
def delete(entry_id: EntryID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete an HTML page."""
    client.htmlpages.delete(entry_id)
    return Ack.deleted("HTML page", entry_id)


@mcp.tool(
    name="htmlpages_preview_url_get",
    annotations={**RO, "title": "Get a preview link of a DataLens HTML page"},
)
def preview_url_get(
    entry_id: EntryID,
    branch: PageBranch = None,
    rev_id: PageRevision = None,
    lang: Annotated[
        PreviewLanguage | None, Field(description="Language of the preview: `en` or `ru`.")
    ] = None,
    theme: Annotated[PreviewTheme | None, Field(description="Theme of the preview.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> HTMLPagePreview:
    """A temporary signed link that shows the page; it stops working after a while."""
    return client.htmlpages.preview_url_get(
        entry_id, branch=branch, rev_id=rev_id, lang=lang, theme=theme
    )
