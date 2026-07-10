"""Declarative Tracker Entities client (uplink) — transport ONLY.

Covers the unified projects / portfolios / goals surface: the entity itself plus its comments,
checklists, links and attachments. ``entity_type`` (project | portfolio | goal) is the first
path segment of every route.

NOTE: do NOT add ``from __future__ import annotations`` — uplink reads parameter annotations
eagerly. ``import requests`` is intentional: the binary attachment download and the no-body
DELETE/POST endpoints return the raw ``requests.Response`` (the transport hook raises a typed
``YandexError`` on any non-2xx, so callers never touch a failed response).
"""

import requests
import uplink

from ycli.yandex.pagination import RelativeCursorStrategy
from ycli.yandex.tracker.base import TrackerResource
from ycli.yandex.tracker.entities.models import (
    Attachment,
    AttachmentList,
    BulkChangeOperation,
    Comment,
    CommentList,
    CommentsRelativeResponse,
    Entity,
    EntityEventList,
    EntityEventsResponse,
    EntityList,
    EntitySearchResponse,
    ExtendedPermissions,
    LinkList,
)


class EntitiesClient(TrackerResource):
    """Declarative HTTP for ``/entities/{entity_type}`` and its sub-resources."""

    # ---- core -------------------------------------------------------------------------------

    @uplink.returns.json()
    @uplink.json
    @uplink.post("entities/{entity_type}")
    def create(self, entity_type: uplink.Path, body: uplink.Body) -> Entity:  # ty: ignore[empty-body]
        """``POST /entities/{entity_type}`` — create an entity from a ``{fields: …}`` body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.create(
            ...     "project", {"fields": {"summary": "Q4"}}
            ... ).id  # doctest: +SKIP
            '655f…'
        """

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}")
    def get(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        expand: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        fields: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> Entity:  # ty: ignore[empty-body]
        """``GET /entities/{entity_type}/{entity_id}`` → a single entity (raises on non-2xx).

        ``fields`` is a comma-separated selector of extra ``fields`` keys (``summary``,
        ``checklistItems``, ``keyResultItems``, ``metricItems``, …); ``expand=attachments``
        embeds attachment metadata.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.get(
            ...     "project", "655f", fields="summary"
            ... ).fields.summary  # doctest: +SKIP
            'Q4'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("entities/{entity_type}/{entity_id}")
    def edit(self, entity_type: uplink.Path, entity_id: uplink.Path, body: uplink.Body) -> Entity:  # ty: ignore[empty-body]
        """``PATCH /entities/{entity_type}/{entity_id}`` — edit fields/comment/links. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.edit(
            ...     "project", "655f", {"fields": {"summary": "New"}}
            ... ).fields.summary  # doctest: +SKIP
            'New'
        """

    @uplink.delete("entities/{entity_type}/{entity_id}")
    def _delete(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        with_board: uplink.Query("withBoard") = None,  # ty: ignore[invalid-type-form]
    ) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE /entities/{entity_type}/{entity_id}`` (internal; use :meth:`delete`)."""

    def delete(self, entity_type: str, entity_id: str, *, with_board: bool | None = None) -> None:
        """Delete an entity. Pass ``with_board=True`` to delete its board too. Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.delete("project", "655f", with_board=True)  # doctest: +SKIP
        """
        self._delete(entity_type, entity_id, with_board=with_board)

    @uplink.returns.json()
    @uplink.json
    @uplink.post("entities/{entity_type}/_search")
    def _search(
        self,
        entity_type: uplink.Path,
        body: uplink.Body,
        fields: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
        per_page: uplink.Query("perPage") = None,  # ty: ignore[invalid-type-form]
        page: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> EntitySearchResponse:  # ty: ignore[empty-body]
        """One raw ``{hits, pages, values}`` page (internal; callers use :meth:`search`)."""

    def search(
        self,
        entity_type: str,
        body: dict | None = None,
        *,
        fields: str | None = None,
        per_page: int | None = None,
        page: int | None = None,
    ) -> EntityList:
        """``POST /entities/{entity_type}/_search`` → flat :class:`EntityList` of ``values``.

        ``body`` carries ``input`` (substring), ``filter`` (field→value), ``orderBy``,
        ``orderAsc`` and ``rootOnly``. ``fields`` selects extra ``fields`` keys in the results;
        ``per_page``/``page`` page the server-side listing.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.search("project", {"filter": {"entityStatus": "in_progress"}}).root[
            ...     0
            ... ].id  # doctest: +SKIP
            '655f…'
        """
        response = self._search(
            entity_type, body or {}, fields=fields, per_page=per_page, page=page
        )
        return EntityList(response.values)

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/events/_relative")
    def _history_page(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
        from_id: uplink.Query("from") = None,  # ty: ignore[invalid-type-form]
    ) -> EntityEventsResponse:  # ty: ignore[empty-body]
        """One raw ``{events, hasNext, hasPrev}`` page (internal; callers use :meth:`history`)."""

    def history(
        self, entity_type: str, entity_id: str, *, limit: int | None = None
    ) -> EntityEventList:
        """``GET …/events/_relative`` → flat :class:`EntityEventList`, draining ``from=<id>``.

        Walks the relative-cursor listing (each page repeats with ``from`` = the last event's
        id) until exhausted or ``limit`` events collected.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.history("project", "655f", limit=50).root[
            ...     0
            ... ].display  # doctest: +SKIP
            'Issue updated'
        """
        strategy = RelativeCursorStrategy(
            extract=lambda page: page.events,
            id_of=lambda event: event.id,
        )
        events = strategy.collect(
            lambda cursor: self._history_page(entity_type, entity_id, from_id=cursor),
            limit,
        )
        return EntityEventList(events)

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/extendedPermissions")
    def permissions(self, entity_type: uplink.Path, entity_id: uplink.Path) -> ExtendedPermissions:  # ty: ignore[empty-body]
        """``GET …/extendedPermissions`` → access settings (acl + permissionSources).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.permissions("project", "655f").acl.read.roles  # doctest: +SKIP
            ['OWNER']
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("entities/{entity_type}/{entity_id}/extendedPermissions")
    def set_permissions(
        self, entity_type: uplink.Path, entity_id: uplink.Path, body: uplink.Body
    ) -> ExtendedPermissions:  # ty: ignore[empty-body]
        """``PATCH …/extendedPermissions`` — set access settings. Returns the new settings.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.set_permissions(
            ...     "project", "655f", {"acl": {"READ": {"roles": ["OWNER"]}}}
            ... ).acl.read.roles  # doctest: +SKIP
            ['OWNER']
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("entities/{entity_type}/bulkchange/_update")
    def bulk_update(self, entity_type: uplink.Path, body: uplink.Body) -> BulkChangeOperation:  # ty: ignore[empty-body]
        """``POST …/bulkchange/_update`` — mass-edit entities (async). Returns the operation.

        The response is a handle whose ``status`` starts at ``CREATED``; poll
        :meth:`bulk_status` with ``id`` until it reaches a terminal status.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.bulk_update(
            ...     "project", {"metaEntities": ["1"], "values": {"comment": "done"}}
            ... ).status  # doctest: +SKIP
            'CREATED'
        """

    @uplink.returns.json()
    @uplink.get("bulkchange/{operation_id}")
    def bulk_status(self, operation_id: uplink.Path) -> BulkChangeOperation:  # ty: ignore[empty-body]
        """``GET /bulkchange/{operation_id}`` → the current bulk-change operation status.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.bulk_status("656").status  # doctest: +SKIP
            'COMPLETE'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("entities/report/")
    def create_report(self, body: uplink.Body) -> Entity:  # ty: ignore[empty-body]
        """``POST /entities/report/`` — build an issue report from a ``{fields: …}`` body.

        The body carries the report name plus export ``parameters`` (type/format, the issue
        ``filter`` and the column ``fields``); the response is the created ``report`` entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.create_report(
            ...     {
            ...         "fields": {
            ...             "summary": "Export",
            ...             "parameters": {
            ...                 "type": "issueFilterExport",
            ...                 "format": "xlsx",
            ...                 "filter": {"query": "Queue: SUPPORT"},
            ...                 "fields": ["key", "summary"],
            ...             },
            ...         }
            ...     }
            ... ).entity_type  # doctest: +SKIP
            'report'
        """

    # ---- comments ---------------------------------------------------------------------------

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/comments")
    def comments_list(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        expand: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> CommentList:  # ty: ignore[empty-body]
        """``GET …/comments`` → all comments on the entity.

        ``expand`` embeds extras (``html``, ``attachments``, ``reactions``, or ``all``).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_list("project", "655f").root[0].text  # doctest: +SKIP
            'Готово'
        """

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/comments/_relative")
    def _comments_relative_page(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        per_page: uplink.Query("perPage") = 100,  # ty: ignore[invalid-type-form]
        from_id: uplink.Query("from") = None,  # ty: ignore[invalid-type-form]
    ) -> CommentsRelativeResponse:  # ty: ignore[empty-body]
        """One raw ``{comments, hasNext, hasPrev}`` page (internal; see comments_relative)."""

    def comments_relative(
        self, entity_type: str, entity_id: str, *, limit: int | None = None
    ) -> CommentList:
        """``GET …/comments/_relative`` → flat :class:`CommentList`, draining ``from=<longId>``.

        The paginated twin of :meth:`comments_list`; walks the relative-cursor listing until
        exhausted or ``limit`` comments collected.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_relative("project", "655f", limit=50).root[
            ...     0
            ... ].id  # doctest: +SKIP
            22
        """
        strategy = RelativeCursorStrategy(
            extract=lambda page: page.comments,
            id_of=lambda comment: comment.long_id,
        )
        comments = strategy.collect(
            lambda cursor: self._comments_relative_page(entity_type, entity_id, from_id=cursor),
            limit,
        )
        return CommentList(comments)

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/comments/{comment_id}")
    def comments_get(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        comment_id: uplink.Path,
        expand: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> Comment:  # ty: ignore[empty-body]
        """``GET …/comments/{comment_id}`` → a single comment.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_get("project", "655f", "22").text  # doctest: +SKIP
            'Готово'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("entities/{entity_type}/{entity_id}/comments")
    def comments_create(
        self, entity_type: uplink.Path, entity_id: uplink.Path, body: uplink.Body
    ) -> Comment:  # ty: ignore[empty-body]
        """``POST …/comments`` — add a comment. Returns the created comment.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_create(
            ...     "project", "655f", {"text": "Готово"}
            ... ).id  # doctest: +SKIP
            22
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("entities/{entity_type}/{entity_id}/comments")
    def comments_edit(
        self, entity_type: uplink.Path, entity_id: uplink.Path, body: uplink.Body
    ) -> Comment:  # ty: ignore[empty-body]
        """``PATCH …/comments`` — edit a comment (its id travels in ``body``). Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_edit(
            ...     "project", "655f", {"id": 22, "text": "fixed"}
            ... ).text  # doctest: +SKIP
            'fixed'
        """

    @uplink.delete("entities/{entity_type}/{entity_id}/comments/{comment_id}")
    def _comments_delete(
        self, entity_type: uplink.Path, entity_id: uplink.Path, comment_id: uplink.Path
    ) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE …/comments/{comment_id}`` (internal; use :meth:`comments_delete`)."""

    def comments_delete(self, entity_type: str, entity_id: str, comment_id: str) -> None:
        """Delete a comment from an entity. Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_delete("project", "655f", "22")  # doctest: +SKIP
        """
        self._comments_delete(entity_type, entity_id, comment_id)

    # ---- checklists -------------------------------------------------------------------------

    @uplink.returns.json()
    @uplink.json
    @uplink.post("entities/{entity_type}/{entity_id}/checklistItems")
    def checklists_create(
        self, entity_type: uplink.Path, entity_id: uplink.Path, body: uplink.Body
    ) -> Entity:  # ty: ignore[empty-body]
        """``POST …/checklistItems`` — add items (``body`` is a JSON array). Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_create(
            ...     "project", "655f", [{"text": "step"}]
            ... ).id  # doctest: +SKIP
            '655f…'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("entities/{entity_type}/{entity_id}/checklistItems")
    def checklists_edit(
        self, entity_type: uplink.Path, entity_id: uplink.Path, body: uplink.Body
    ) -> Entity:  # ty: ignore[empty-body]
        """``PATCH …/checklistItems`` — replace items (``body`` is a JSON array of ``{id, …}``).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_edit(
            ...     "project", "655f", [{"id": "5f", "text": "step"}]
            ... ).id  # doctest: +SKIP
            '655f…'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.patch("entities/{entity_type}/{entity_id}/checklistItems/{item_id}")
    def checklists_edit_item(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        item_id: uplink.Path,
        body: uplink.Body,
    ) -> Entity:  # ty: ignore[empty-body]
        """``PATCH …/checklistItems/{item_id}`` — edit one item. Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_edit_item(
            ...     "project", "655f", "5f", {"checked": True}
            ... ).id  # doctest: +SKIP
            '655f…'
        """

    @uplink.returns.json()
    @uplink.delete("entities/{entity_type}/{entity_id}/checklistItems")
    def checklists_delete(self, entity_type: uplink.Path, entity_id: uplink.Path) -> Entity:  # ty: ignore[empty-body]
        """``DELETE …/checklistItems`` — clear the whole checklist. Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_delete("project", "655f").id  # doctest: +SKIP
            '655f…'
        """

    @uplink.returns.json()
    @uplink.delete("entities/{entity_type}/{entity_id}/checklistItems/{item_id}")
    def checklists_delete_item(
        self, entity_type: uplink.Path, entity_id: uplink.Path, item_id: uplink.Path
    ) -> Entity:  # ty: ignore[empty-body]
        """``DELETE …/checklistItems/{item_id}`` — remove one item. Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_delete_item("project", "655f", "5f").id  # doctest: +SKIP
            '655f…'
        """

    @uplink.returns.json()
    @uplink.json
    @uplink.post("entities/{entity_type}/{entity_id}/checklistItems/{item_id}/_move")
    def checklists_move(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        item_id: uplink.Path,
        body: uplink.Body,
    ) -> Entity:  # ty: ignore[empty-body]
        """``POST …/checklistItems/{item_id}/_move`` — reorder an item. Returns the entity.

        ``body`` is ``{"before": "<item id>"}``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_move(
            ...     "project", "655f", "5f", {"before": "6a"}
            ... ).id  # doctest: +SKIP
            '655f…'
        """

    # ---- links ------------------------------------------------------------------------------

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/links")
    def links_list(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        fields: uplink.Query = None,  # ty: ignore[invalid-parameter-default]
    ) -> LinkList:  # ty: ignore[empty-body]
        """``GET …/links`` → the entity's links to other entities.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.links_list("project", "655f").root[0].type  # doctest: +SKIP
            'relates'
        """

    @uplink.json
    @uplink.post("entities/{entity_type}/{entity_id}/links")
    def _links_create(
        self, entity_type: uplink.Path, entity_id: uplink.Path, body: uplink.Body
    ) -> requests.Response:  # ty: ignore[empty-body]
        """``POST …/links`` (200 OK, no body; internal; use :meth:`links_create`)."""

    def links_create(self, entity_type: str, entity_id: str, body: dict) -> None:
        """Create a link (``body`` is ``{relationship, entity}``). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.links_create(
            ...     "project", "655f", {"relationship": "relates", "entity": "658"}
            ... )  # doctest: +SKIP
        """
        self._links_create(entity_type, entity_id, body)  # ty: ignore[too-many-positional-arguments]

    @uplink.delete("entities/{entity_type}/{entity_id}/links")
    def _links_delete(
        self,
        entity_type: uplink.Path,
        entity_id: uplink.Path,
        right: uplink.Query,
    ) -> requests.Response:  # ty: ignore[empty-body]
        """``DELETE …/links?right=`` (200 OK, no body; internal; use :meth:`links_delete`)."""

    def links_delete(self, entity_type: str, entity_id: str, right: str) -> None:
        """Delete the link to entity ``right``. Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.links_delete("project", "655f", "658")  # doctest: +SKIP
        """
        self._links_delete(entity_type, entity_id, right=right)

    # ---- attachments ------------------------------------------------------------------------

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/attachments")
    def attachments_list(self, entity_type: uplink.Path, entity_id: uplink.Path) -> AttachmentList:  # ty: ignore[empty-body]
        """``GET …/attachments`` → files attached to the entity (metadata only).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_list("project", "655f").root[0].name  # doctest: +SKIP
            'Shops.csv'
        """

    @uplink.returns.json()
    @uplink.get("entities/{entity_type}/{entity_id}/attachments/{file_id}")
    def attachments_get(
        self, entity_type: uplink.Path, entity_id: uplink.Path, file_id: uplink.Path
    ) -> Attachment:  # ty: ignore[empty-body]
        """``GET …/attachments/{file_id}`` → one attachment's metadata (name, size, download URL).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_get("project", "655f", "5").name  # doctest: +SKIP
            'flowers.jpg'
        """

    @uplink.get("attachments/{file_id}/{filename}")
    def _attachment_download(
        self, file_id: uplink.Path, filename: uplink.Path
    ) -> requests.Response:  # ty: ignore[empty-body]
        """GET the raw attachment bytes (internal; callers use :meth:`attachment_download`)."""

    def attachment_download(self, file_id: str, filename: str) -> bytes:
        """Download an attachment's raw bytes (raises on non-2xx via the transport hook).

        Binary output is CLI/SDK-only — never an MCP payload. ``file_id`` and ``filename`` come
        from :meth:`attachments_list` / :meth:`attachments_get` (the ``id`` and ``name`` fields).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachment_download("5", "flowers.jpg")[:4]  # doctest: +SKIP
            b'\\xff\\xd8\\xff\\xe0'
        """
        return self._attachment_download(file_id, filename).content

    @uplink.returns.json()
    @uplink.post("entities/{entity_type}/{entity_id}/attachments/{temp_file_id}")
    def attachments_attach(
        self, entity_type: uplink.Path, entity_id: uplink.Path, temp_file_id: uplink.Path
    ) -> Entity:  # ty: ignore[empty-body]
        """``POST …/attachments/{temp_file_id}`` — attach a previously uploaded temp file.

        Returns the updated entity. ``temp_file_id`` is the id of a file uploaded to the temp
        attachments endpoint.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_attach("project", "655f", "tmp9").id  # doctest: +SKIP
            '655f…'
        """

    @uplink.returns.json()
    @uplink.delete("entities/{entity_type}/{entity_id}/attachments/{file_id}")
    def attachments_delete(
        self, entity_type: uplink.Path, entity_id: uplink.Path, file_id: uplink.Path
    ) -> Entity:  # ty: ignore[empty-body]
        """``DELETE …/attachments/{file_id}`` — detach a file. Returns the updated entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_delete("project", "655f", "5").id  # doctest: +SKIP
            '655f…'
        """
