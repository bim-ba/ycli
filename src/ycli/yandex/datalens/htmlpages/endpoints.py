"""DataLens HTML page operations, declared once (sans-IO).

Examples:
    >>> delete("hp1").body
    {'entryId': 'hp1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
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
from ycli.yandex.datalens.models import RevisionBranch, one_revision
from ycli.yandex.datalens.schemas.html_pages import (
    CreateHtmlPageArgs,
    DeleteHtmlPageArgs,
    GetHtmlPageArgs,
    GetHtmlPagePreviewUrlArgs,
)


def get(
    entry_id: str,
    *,
    rev_id: str | None,
    branch: RevisionBranch | None,
    include_permissions: bool | None,
    include_favorite: bool | None,
) -> Endpoint[HTMLPage]:
    one_revision(branch=branch, rev_id=rev_id)
    body = GetHtmlPageArgs(
        entryId=entry_id,
        revId=rev_id,
        branch=branch,
        includePermissions=include_permissions,
        includeFavorite=include_favorite,
    )
    return RPC("getHtmlPage", HTMLPage, json=body, effect=Effect.READ)


def create(
    *,
    content: str,
    annotation: HTMLPageAnnotation | None,
    key: str | None,
    workbook_id: str | None,
    name: str | None,
) -> Endpoint[HTMLPageCreated]:
    body = CreateHtmlPageArgs(
        content=content, annotation=annotation, key=key, workbookId=workbook_id, name=name
    )
    return RPC("createHtmlPage", HTMLPageCreated, json=body, effect=Effect.WRITE)


def update(body: HTMLPageUpdate) -> Endpoint[HTMLPageSaved]:
    # The request is a union of two objects that nothing tags: new content, or a revision.
    return RPC("updateHtmlPage", HTMLPageSaved, json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(entry_id: str) -> Endpoint[None]:
    # Measured: DataLens answers `{}`; nothing in it is read.
    body = DeleteHtmlPageArgs(entryId=entry_id)
    return RPC("deleteHtmlPage", json=body, effect=Effect.DESTRUCTIVE)


def preview_url_get(
    entry_id: str,
    *,
    branch: RevisionBranch | None,
    rev_id: str | None,
    lang: PreviewLanguage | None,
    theme: PreviewTheme | None,
) -> Endpoint[HTMLPagePreview]:
    one_revision(branch=branch, rev_id=rev_id)
    body = GetHtmlPagePreviewUrlArgs(
        entryId=entry_id, branch=branch, revId=rev_id, lang=lang, theme=theme
    )
    return RPC("getHtmlPagePreviewUrl", HTMLPagePreview, json=body, effect=Effect.READ)
