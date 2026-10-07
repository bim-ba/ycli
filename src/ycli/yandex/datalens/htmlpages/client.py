"""DataLens HTML pages client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.htmlpages import endpoints

if TYPE_CHECKING:
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


class HTMLPagesClient(Resource):
    """HTML pages: an entry that holds a page of HTML, shown as it is."""

    def get(
        self,
        entry_id: str,
        *,
        rev_id: str | None = None,
        branch: RevisionBranch | None = None,
        include_permissions: bool | None = None,
        include_favorite: bool | None = None,
    ) -> HTMLPage:
        """``getHtmlPage`` → one HTML page: where it lies and its revisions, not its HTML.

        The reply has no content of the page; :meth:`preview_url_get` gives a link that shows
        it.

        Args:
            entry_id: The page's id.
            rev_id: The revision to read; the current one when left out.
            branch: ``saved`` or ``published``.
            include_permissions: Also say what the caller may do with the page.
            include_favorite: Also say whether the page is a favourite.

        Returns:
            The page.

        Examples:
            >>> datalens.htmlpages.get("hp000000000001").type
            'html-page'
        """
        return self._session.send(
            endpoints.get(
                entry_id,
                rev_id=rev_id,
                branch=branch,
                include_permissions=include_permissions,
                include_favorite=include_favorite,
            )
        )

    def create(
        self,
        *,
        content: str,
        annotation: HTMLPageAnnotation | None = None,
        key: str | None = None,
        workbook_id: str | None = None,
        name: str | None = None,
    ) -> HTMLPageCreated:
        """``createHtmlPage`` — create an HTML page → it, with what DataLens warns of.

        Args:
            content: The HTML of the page.
            annotation: A description of the page.
            key: The page's key, in a folder.
            workbook_id: The workbook to create the page in.
            name: The page's name, in a workbook.

        Returns:
            The new page under ``entry``, and ``warnings`` about its HTML.

        Examples:
            >>> made = datalens.htmlpages.create(
            ...     content="<p>Hello</p>", workbook_id="wb000000000001", name="Hello"
            ... )
            >>> made.warnings
            []
        """
        return self._session.send(
            endpoints.create(
                content=content, annotation=annotation, key=key, workbook_id=workbook_id, name=name
            )
        )

    def update(self, body: HTMLPageUpdate) -> HTMLPageSaved:
        """``updateHtmlPage`` — save new HTML, or make a revision the current one → the page.

        The request is one of two: new ``content`` (``HTMLPageContent``), or a ``revId`` to
        save or publish (``HTMLPageRevision``). With ``mode`` ``save`` a new revision is made and
        the published one stays; ``publish`` shows it to everyone. For a revision, ``save``
        copies it as the current one (measured). The API takes ``content`` and ``revId``
        together and saves the content; ycli refuses the pair, as the document describes none.

        Args:
            body: The new content, or the revision.

        Returns:
            The page under ``entry``, and ``warnings`` about its HTML.

        Examples:
            >>> from ycli.yandex.datalens.htmlpages.models import HTMLPageUpdate
            >>> change = HTMLPageUpdate.model_validate(
            ...     {"entryId": "hp000000000001", "content": "<p>Bye</p>", "mode": "save"}
            ... )
            >>> datalens.htmlpages.update(change).entry.rev_id
            'rev2'
        """
        return self._session.send(endpoints.update(body))

    def delete(self, entry_id: str) -> None:
        """``deleteHtmlPage`` — delete an HTML page.

        Args:
            entry_id: The page's id.

        Examples:
            >>> datalens.htmlpages.delete("hp000000000001")
        """
        self._session.send(endpoints.delete(entry_id))

    def preview_url_get(
        self,
        entry_id: str,
        *,
        branch: RevisionBranch | None = None,
        rev_id: str | None = None,
        lang: PreviewLanguage | None = None,
        theme: PreviewTheme | None = None,
    ) -> HTMLPagePreview:
        """``getHtmlPagePreviewUrl`` → a temporary signed link that shows the page.

        Args:
            entry_id: The page's id.
            branch: ``saved`` or ``published``; the published one when left out.
            rev_id: The revision to show.
            lang: The language of the preview: ``en`` or ``ru``.
            theme: The theme of the preview, e.g. ``light`` or ``dark``.

        Returns:
            The link under ``url``; it stops working after a while.

        Examples:
            >>> datalens.htmlpages.preview_url_get("hp000000000001").url
            'https://preview.example/hp000000000001?sig=1'
        """
        return self._session.send(
            endpoints.preview_url_get(
                entry_id, branch=branch, rev_id=rev_id, lang=lang, theme=theme
            )
        )
