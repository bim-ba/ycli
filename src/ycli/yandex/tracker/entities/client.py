"""Tracker Entities client on the httpx2 core.

Covers the unified projects / portfolios / goals surface: the entity itself plus its comments,
checklists, links and attachments. Every method sends one declaration from
:mod:`ycli.yandex.tracker.entities.endpoints`.
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.tracker.entities import endpoints
from ycli.yandex.tracker.entities.models import (
    Acl,
    Attachment,
    AttachmentList,
    BulkChangeOperation,
    Comment,
    CommentList,
    DirectPermissionsUpdate,
    Entity,
    EntityEventList,
    EntityList,
    ExtendedPermissions,
    LinkList,
)


def _page_size(limit: int | None) -> int:
    """A positive ``limit`` narrows the page; ``None``/``0`` asks for full pages."""
    return min(endpoints.RELATIVE_PAGE_SIZE, limit) if limit else endpoints.RELATIVE_PAGE_SIZE


class EntitiesClient(Resource):
    """``/entities/{entity_type}`` and its sub-resources."""

    # ---- core -------------------------------------------------------------------------------

    def create(self, entity_type: str, body: dict[str, Any]) -> Entity:
        """``POST /entities/{entity_type}`` — create an entity from a ``{fields: …}`` body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.create(
            ...     "project", {"fields": {"summary": "Q4"}}
            ... ).id  # doctest: +SKIP
            '655f…'
        """
        return self._session.send(endpoints.create_entity(entity_type, body))

    def get(
        self,
        entity_type: str,
        entity_id: str,
        expand: str | None = None,
        fields: str | None = None,
    ) -> Entity:
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
        endpoint = endpoints.get_entity(entity_type, entity_id, expand=expand, fields=fields)
        return self._session.send(endpoint)

    def edit(self, entity_type: str, entity_id: str, body: dict[str, Any]) -> Entity:
        """``PATCH /entities/{entity_type}/{entity_id}`` — edit fields/comment/links. Returns it.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.edit(
            ...     "project", "655f", {"fields": {"summary": "New"}}
            ... ).fields.summary  # doctest: +SKIP
            'New'
        """
        return self._session.send(endpoints.edit_entity(entity_type, entity_id, body))

    def delete(self, entity_type: str, entity_id: str, *, with_board: bool | None = None) -> None:
        """Delete an entity. Pass ``with_board=True`` to delete its board too. Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.delete("project", "655f", with_board=True)  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_entity(entity_type, entity_id, with_board=with_board))

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
        endpoint = endpoints.search_entities(
            entity_type, body or {}, fields=fields, per_page=per_page, page=page
        )
        return EntityList(self._session.send(endpoint).values)

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
        paged = endpoints.list_events(entity_type, entity_id, per_page=_page_size(limit))
        return EntityEventList(list(self._session.iterate(paged, limit=limit)))

    def permissions(self, entity_type: str, entity_id: str) -> ExtendedPermissions:
        """``GET …/extendedPermissions`` → access settings (acl + permissionSources).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.permissions("project", "655f").acl.read.roles  # doctest: +SKIP
            ['OWNER']
        """
        return self._session.send(endpoints.get_permissions(entity_type, entity_id))

    def set_permissions(
        self, entity_type: str, entity_id: str, body: dict[str, Any]
    ) -> ExtendedPermissions:
        """``PATCH …/extendedPermissions`` — set access settings. Returns the new settings.

        The ``acl`` object accepts only ``grant`` / ``revoke`` actions, each mapping an access
        level (``READ``/``WRITE``/``GRANT``) to users/groups/roles.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.set_permissions(
            ...     "project", "655f", {"acl": {"grant": {"READ": {"users": ["800…2"]}}}}
            ... ).acl.read.users  # doctest: +SKIP
            ['800…2']
        """
        return self._session.send(endpoints.set_permissions(entity_type, entity_id, body))

    def direct_permissions(self, entity_type: str, entity_id: str) -> Acl:
        """``GET …/permissions`` → the direct READ / WRITE / GRANT rights, without inheritance.

        :meth:`permissions` is the extended view (``acl`` plus where rights are inherited from).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.direct_permissions("project", "655f").grant.roles  # doctest: +SKIP
            ['AUTHOR', 'OWNER']
        """
        return self._session.send(endpoints.get_direct_permissions(entity_type, entity_id))

    def set_direct_permissions(
        self, entity_type: str, entity_id: str, body: DirectPermissionsUpdate
    ) -> Acl:
        """``PATCH …/permissions`` — grant and revoke direct rights. Returns the resulting rights.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> grant = AclInput(read=AclPrincipalsInput(users=["ann"]))
            >>> update = DirectPermissionsUpdate(grant=grant)
            >>> client.entities.set_direct_permissions(
            ...     "project", "655f", update
            ... ).read.users  # doctest: +SKIP
            [UserRef(...)]
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.set_direct_permissions(entity_type, entity_id, dumped))

    def bulk_update(self, entity_type: str, body: dict[str, Any]) -> BulkChangeOperation:
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
        return self._session.send(endpoints.bulk_update(entity_type, body))

    def bulk_status(self, operation_id: str) -> BulkChangeOperation:
        """``GET /bulkchange/{operation_id}`` → the current bulk-change operation status.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.bulk_status("656").status  # doctest: +SKIP
            'COMPLETE'
        """
        return self._session.send(endpoints.get_bulk_status(operation_id))

    def create_report(self, body: dict[str, Any]) -> Entity:
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
        return self._session.send(endpoints.create_report(body))

    # ---- comments ---------------------------------------------------------------------------

    def comments_list(
        self, entity_type: str, entity_id: str, expand: str | None = None
    ) -> CommentList:
        """``GET …/comments`` → all comments on the entity.

        ``expand`` embeds extras (``html``, ``attachments``, ``reactions``, or ``all``).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_list("project", "655f").root[0].text  # doctest: +SKIP
            'Готово'
        """
        return self._session.send(endpoints.list_comments(entity_type, entity_id, expand=expand))

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
        paged = endpoints.list_comments_relative(entity_type, entity_id, per_page=_page_size(limit))
        return CommentList(list(self._session.iterate(paged, limit=limit)))

    def comments_get(
        self, entity_type: str, entity_id: str, comment_id: str, expand: str | None = None
    ) -> Comment:
        """``GET …/comments/{comment_id}`` → a single comment.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_get("project", "655f", "22").text  # doctest: +SKIP
            'Готово'
        """
        endpoint = endpoints.get_comment(entity_type, entity_id, comment_id, expand=expand)
        return self._session.send(endpoint)

    def comments_create(self, entity_type: str, entity_id: str, body: dict[str, Any]) -> Comment:
        """``POST …/comments`` — add a comment. Returns the created comment.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_create(
            ...     "project", "655f", {"text": "Готово"}
            ... ).id  # doctest: +SKIP
            22
        """
        return self._session.send(endpoints.create_comment(entity_type, entity_id, body))

    def comments_edit(
        self, entity_type: str, entity_id: str, comment_id: str, body: dict[str, Any]
    ) -> Comment:
        """``PATCH …/comments/{comment_id}`` — edit a comment. Returns the updated comment.

        The live v3 API only accepts the per-comment route (a PATCH on the ``…/comments``
        collection answers 405), so the comment id travels in the path, not the body.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_edit(
            ...     "project", "655f", "22", {"text": "fixed"}
            ... ).text  # doctest: +SKIP
            'fixed'
        """
        endpoint = endpoints.edit_comment(entity_type, entity_id, comment_id, body)
        return self._session.send(endpoint)

    def comments_delete(self, entity_type: str, entity_id: str, comment_id: str) -> None:
        """Delete a comment from an entity. Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.comments_delete("project", "655f", "22")  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_comment(entity_type, entity_id, comment_id))

    # ---- checklists -------------------------------------------------------------------------

    def checklists_create(
        self, entity_type: str, entity_id: str, body: list[dict[str, Any]]
    ) -> Entity:
        """``POST …/checklistItems`` — add items (``body`` is a JSON array). Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_create(
            ...     "project", "655f", [{"text": "step"}]
            ... ).id  # doctest: +SKIP
            '655f…'
        """
        return self._session.send(endpoints.create_checklist_items(entity_type, entity_id, body))

    def checklists_edit(
        self, entity_type: str, entity_id: str, body: list[dict[str, Any]]
    ) -> Entity:
        """``PATCH …/checklistItems`` — replace items (``body`` is a JSON array of ``{id, …}``).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_edit(
            ...     "project", "655f", [{"id": "5f", "text": "step"}]
            ... ).id  # doctest: +SKIP
            '655f…'
        """
        return self._session.send(endpoints.edit_checklist(entity_type, entity_id, body))

    def checklists_edit_item(
        self, entity_type: str, entity_id: str, item_id: str, body: dict[str, Any]
    ) -> Entity:
        """``PATCH …/checklistItems/{item_id}`` — edit one item. Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_edit_item(
            ...     "project", "655f", "5f", {"checked": True}
            ... ).id  # doctest: +SKIP
            '655f…'
        """
        endpoint = endpoints.edit_checklist_item(entity_type, entity_id, item_id, body)
        return self._session.send(endpoint)

    def checklists_delete(self, entity_type: str, entity_id: str) -> Entity:
        """``DELETE …/checklistItems`` — clear the whole checklist. Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_delete("project", "655f").id  # doctest: +SKIP
            '655f…'
        """
        return self._session.send(endpoints.delete_checklist(entity_type, entity_id))

    def checklists_delete_item(self, entity_type: str, entity_id: str, item_id: str) -> Entity:
        """``DELETE …/checklistItems/{item_id}`` — remove one item. Returns the entity.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_delete_item("project", "655f", "5f").id  # doctest: +SKIP
            '655f…'
        """
        return self._session.send(endpoints.delete_checklist_item(entity_type, entity_id, item_id))

    def checklists_move(
        self, entity_type: str, entity_id: str, item_id: str, body: dict[str, Any]
    ) -> Entity:
        """``POST …/checklistItems/{item_id}/_move`` — reorder an item. Returns the entity.

        ``body`` is ``{"before": "<item id>"}``.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.checklists_move(
            ...     "project", "655f", "5f", {"before": "6a"}
            ... ).id  # doctest: +SKIP
            '655f…'
        """
        endpoint = endpoints.move_checklist_item(entity_type, entity_id, item_id, body)
        return self._session.send(endpoint)

    # ---- links ------------------------------------------------------------------------------

    def links_list(self, entity_type: str, entity_id: str, fields: str | None = None) -> LinkList:
        """``GET …/links`` → the entity's links to other entities.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.links_list("project", "655f").root[0].type  # doctest: +SKIP
            'relates'
        """
        return self._session.send(endpoints.list_links(entity_type, entity_id, fields=fields))

    def links_create(self, entity_type: str, entity_id: str, body: dict) -> None:
        """Create a link (``body`` is ``{relationship, entity}``). Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.links_create(
            ...     "project", "655f", {"relationship": "relates", "entity": "658"}
            ... )  # doctest: +SKIP
        """
        self._session.send(endpoints.create_link(entity_type, entity_id, body))

    def links_delete(self, entity_type: str, entity_id: str, right: str) -> None:
        """Delete the link to entity ``right``. Raises on non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.links_delete("project", "655f", "658")  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_link(entity_type, entity_id, right))

    # ---- attachments ------------------------------------------------------------------------

    def attachments_list(self, entity_type: str, entity_id: str) -> AttachmentList:
        """``GET …/attachments`` → files attached to the entity (metadata only).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_list("project", "655f").root[0].name  # doctest: +SKIP
            'Shops.csv'
        """
        return self._session.send(endpoints.list_attachments(entity_type, entity_id))

    def attachments_get(self, entity_type: str, entity_id: str, file_id: str) -> Attachment:
        """``GET …/attachments/{file_id}`` → one attachment's metadata (name, size, download URL).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_get("project", "655f", "5").name  # doctest: +SKIP
            'flowers.jpg'
        """
        return self._session.send(endpoints.get_attachment(entity_type, entity_id, file_id))

    def attachment_download(self, file_id: str, filename: str) -> bytes:
        """Download an attachment's raw bytes (a non-2xx answer raises a typed error).

        Binary output is CLI/SDK-only — never an MCP payload. ``file_id`` and ``filename`` come
        from :meth:`attachments_list` / :meth:`attachments_get` (the ``id`` and ``name`` fields).

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachment_download("5", "flowers.jpg")[:4]  # doctest: +SKIP
            b'\\xff\\xd8\\xff\\xe0'
        """
        return self._session.send(endpoints.download_attachment(file_id, filename))

    def attachments_attach(self, entity_type: str, entity_id: str, temp_file_id: str) -> Entity:
        """``POST …/attachments/{temp_file_id}`` — attach a previously uploaded temp file.

        Returns the updated entity. ``temp_file_id`` is the id of a file uploaded to the temp
        attachments endpoint.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_attach("project", "655f", "tmp9").id  # doctest: +SKIP
            '655f…'
        """
        return self._session.send(endpoints.attach_file(entity_type, entity_id, temp_file_id))

    def attachments_delete(self, entity_type: str, entity_id: str, file_id: str) -> None:
        """Detach a file from an entity (the live API answers with an empty body). Raises on
        non-2xx.

        Example:
            >>> client = TrackerClient(oauth_token="…", organization_id="…")  # doctest: +SKIP
            >>> client.entities.attachments_delete("project", "655f", "5")  # doctest: +SKIP
        """
        self._session.send(endpoints.delete_attachment(entity_type, entity_id, file_id))
