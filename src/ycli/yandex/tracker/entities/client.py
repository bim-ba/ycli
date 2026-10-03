"""Tracker Entities client on the httpx2 core.

Covers the unified projects / portfolios / goals surface: the entity itself plus its comments,
checklists, links and attachments. Every method sends one declaration from
:mod:`ycli.yandex.tracker.entities.endpoints`.
"""

from __future__ import annotations

from typing import Any

from ycli.yandex.core.resource import Resource
from ycli.yandex.models import ItemList
from ycli.yandex.tracker.entities import endpoints
from ycli.yandex.tracker.entities.models import (
    Acl,
    Attachment,
    BulkChangeOperation,
    Comment,
    DirectPermissionsUpdate,
    Entity,
    EntityEvent,
    ExtendedPermissions,
    Link,
)


def _page_size(limit: int | None) -> int:
    """A positive ``limit`` narrows the page; ``None``/``0`` asks for full pages.

    Args:
        limit: The most items wanted; ``None`` or ``0`` means no cap.

    Returns:
        The page size to request.
    """
    return min(endpoints.RELATIVE_PAGE_SIZE, limit) if limit else endpoints.RELATIVE_PAGE_SIZE


class EntitiesClient(Resource):
    """``/entities/{entity_type}`` and its sub-resources."""

    # ---- core -------------------------------------------------------------------------------

    def create(self, entity_type: str, body: dict[str, Any]) -> Entity:
        """``POST /entities/{entity_type}`` — create an entity from a ``{fields: …}`` body.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            body: The new entity, as ``{"fields": {...}}``.

        Returns:
            The created entity.

        Examples:
            >>> tracker.entities.create("project", {"fields": {"summary": "Q4 launch"}}).id
            '655f'
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

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            expand: The extras to embed, such as ``attachments``.
            fields: The extra ``fields`` keys to include, comma-separated.

        Returns:
            The entity.

        Examples:
            >>> tracker.entities.get(
            ...     "goal", "g2", expand="attachments", fields="summary,keyResultItems"
            ... ).fields.summary
            'Ship'
        """
        endpoint = endpoints.get_entity(entity_type, entity_id, expand=expand, fields=fields)
        return self._session.send(endpoint)

    def edit(self, entity_type: str, entity_id: str, body: dict[str, Any]) -> Entity:
        """``PATCH /entities/{entity_type}/{entity_id}`` — edit fields/comment/links. Returns it.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            body: The changes: ``fields``, a ``comment`` or ``links``.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.edit("project", "655f04", {"fields": {"summary": "Renamed"}}).id
            '655f04'
        """
        return self._session.send(endpoints.edit_entity(entity_type, entity_id, body))

    def delete(self, entity_type: str, entity_id: str, *, with_board: bool | None = None) -> None:
        """Delete an entity. Pass ``with_board=True`` to delete its board too. Raises on non-2xx.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            with_board: Whether to delete the entity's board too.

        Examples:
            >>> tracker.entities.delete("project", "655f07", with_board=True)
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
    ) -> ItemList[Entity]:
        """``POST /entities/{entity_type}/_search`` → flat ``ItemList[Entity]`` of ``values``.

        ``body`` carries ``input`` (substring), ``filter`` (field→value), ``orderBy``,
        ``orderAsc`` and ``rootOnly``. ``fields`` selects extra ``fields`` keys in the results;
        ``per_page``/``page`` page the server-side listing.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            body: The search: ``input``, ``filter``, ``orderBy``, ``orderAsc``, ``rootOnly``.
            fields: The extra ``fields`` keys to include, comma-separated.
            per_page: The page size.
            page: The page number.

        Returns:
            The matching entities.

        Examples:
            >>> tracker.entities.search(
            ...     "project", {"input": "Q4", "filter": {"entityStatus": "in_progress"}}
            ... ).root[0].id
            '655f'
        """
        endpoint = endpoints.search_entities(
            entity_type, body or {}, fields=fields, per_page=per_page, page=page
        )
        return ItemList[Entity](self._session.send(endpoint).values)

    def history(
        self, entity_type: str, entity_id: str, *, limit: int | None = None
    ) -> ItemList[EntityEvent]:
        """``GET …/events/_relative`` → flat ``ItemList[EntityEvent]``, draining ``from=<id>``.

        Walks the relative-cursor listing (each page repeats with ``from`` = the last event's
        id) until exhausted or ``limit`` events collected.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            limit: The most events to return; ``None`` returns every event.

        Returns:
            The entity's events.

        Examples:
            >>> [event.id for event in tracker.entities.history("project", "655f13").root]
            ['e1', 'e2']
        """
        paged = endpoints.list_events(entity_type, entity_id, per_page=_page_size(limit))
        return ItemList[EntityEvent](list(self._session.iterate(paged, limit=limit)))

    def permissions(self, entity_type: str, entity_id: str) -> ExtendedPermissions:
        """``GET …/extendedPermissions`` → access settings (acl + permissionSources).

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.

        Returns:
            The entity's access settings.

        Examples:
            >>> tracker.entities.permissions("project", "655f15").acl.read.roles
            ['OWNER']
        """
        return self._session.send(endpoints.get_permissions(entity_type, entity_id))

    def set_permissions(
        self, entity_type: str, entity_id: str, body: dict[str, Any]
    ) -> ExtendedPermissions:
        """``PATCH …/extendedPermissions`` — set access settings. Returns the new settings.

        The ``acl`` object accepts only ``grant`` / ``revoke`` actions, each mapping an access
        level (``READ``/``WRITE``/``GRANT``) to users/groups/roles.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            body: The ``acl`` with its ``grant`` and ``revoke`` actions.

        Returns:
            The new access settings.

        Examples:
            >>> tracker.entities.set_permissions(
            ...     "portfolio",
            ...     "pf16",
            ...     {"acl": {"grant": {"READ": {"users": ["8000000000000002"]}}}},
            ... ).acl.read.users[0].id
            '8000000000000002'
        """
        return self._session.send(endpoints.set_permissions(entity_type, entity_id, body))

    def direct_permissions(self, entity_type: str, entity_id: str) -> Acl:
        """``GET …/permissions`` → the direct READ / WRITE / GRANT rights, without inheritance.

        :meth:`permissions` is the extended view (``acl`` plus where rights are inherited from).

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.

        Returns:
            The entity's direct rights.

        Examples:
            >>> tracker.entities.direct_permissions("project", "655f17").grant.roles
            ['AUTHOR', 'OWNER']
        """
        return self._session.send(endpoints.get_direct_permissions(entity_type, entity_id))

    def set_direct_permissions(
        self, entity_type: str, entity_id: str, body: DirectPermissionsUpdate
    ) -> Acl:
        """``PATCH …/permissions`` — grant and revoke direct rights. Returns the resulting rights.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            body: The rights to grant and to revoke.

        Returns:
            The resulting direct rights.

        Examples:
            >>> from ycli.yandex.tracker.entities.models import AclInput, AclPrincipalsInput
            >>> grant = AclInput(read=AclPrincipalsInput(users=["ann"]))
            >>> update = DirectPermissionsUpdate(grant=grant)
            >>> tracker.entities.set_direct_permissions("goal", "g18", update).read.users[0].display
            'Ann'
        """
        dumped = body.model_dump(by_alias=True, exclude_none=True)
        return self._session.send(endpoints.set_direct_permissions(entity_type, entity_id, dumped))

    def bulk_update(self, entity_type: str, body: dict[str, Any]) -> BulkChangeOperation:
        """``POST …/bulkchange/_update`` — mass-edit entities (async). Returns the operation.

        The response is a handle whose ``status`` starts at ``CREATED``; poll
        :meth:`bulk_status` with ``id`` until it reaches a terminal status.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            body: The entities to change (``metaEntities``) and the ``values`` to set.

        Returns:
            The started bulk-change operation.

        Examples:
            >>> tracker.entities.bulk_update(
            ...     "project", {"metaEntities": ["655f17"], "values": {"comment": "Handed over"}}
            ... ).status
            'CREATED'
        """
        return self._session.send(endpoints.bulk_update(entity_type, body))

    def bulk_status(self, operation_id: str) -> BulkChangeOperation:
        """``GET /bulkchange/{operation_id}`` → the current bulk-change operation status.

        Args:
            operation_id: The bulk-change operation's id.

        Returns:
            The operation with its current status.

        Examples:
            >>> tracker.entities.bulk_status("658").status
            'COMPLETE'
        """
        return self._session.send(endpoints.get_bulk_status(operation_id))

    def create_report(self, body: dict[str, Any]) -> Entity:
        """``POST /entities/report/`` — build an issue report from a ``{fields: …}`` body.

        The body carries the report name plus export ``parameters`` (type/format, the issue
        ``filter`` and the column ``fields``); the response is the created ``report`` entity.

        Args:
            body: The report, as ``{"fields": {...}}``.

        Returns:
            The created report entity.

        Examples:
            >>> tracker.entities.create_report(
            ...     {
            ...         "fields": {
            ...             "summary": "Support export",
            ...             "parameters": {
            ...                 "type": "issueFilterExport",
            ...                 "format": "csv",
            ...                 "filter": {"query": "Queue: SUPPORT"},
            ...                 "fields": ["key", "summary", "assignee"],
            ...             },
            ...         }
            ...     }
            ... ).entity_type
            'report'
        """
        return self._session.send(endpoints.create_report(body))

    # ---- comments ---------------------------------------------------------------------------

    def comments_list(
        self, entity_type: str, entity_id: str, expand: str | None = None
    ) -> ItemList[Comment]:
        """``GET …/comments`` → all comments on the entity.

        ``expand`` embeds extras (``html``, ``attachments``, ``reactions``, or ``all``).

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            expand: The extras to embed.

        Returns:
            The entity's comments.

        Examples:
            >>> tracker.entities.comments_list("project", "655f20").root[0].text
            'Готово'
        """
        return self._session.send(endpoints.list_comments(entity_type, entity_id, expand=expand))

    def comments_relative(
        self, entity_type: str, entity_id: str, *, limit: int | None = None
    ) -> ItemList[Comment]:
        """``GET …/comments/_relative`` → flat ``ItemList[Comment]``, draining ``from=<longId>``.

        The paginated twin of :meth:`comments_list`; walks the relative-cursor listing until
        exhausted or ``limit`` comments collected.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            limit: The most comments to return; ``None`` returns every comment.

        Returns:
            The entity's comments.

        Examples:
            >>> [
            ...     c.id
            ...     for c in tracker.entities.comments_relative("portfolio", "pf22", limit=10).root
            ... ]
            [31, 32]
        """
        paged = endpoints.list_comments_relative(entity_type, entity_id, per_page=_page_size(limit))
        return ItemList[Comment](list(self._session.iterate(paged, limit=limit)))

    def comments_get(
        self, entity_type: str, entity_id: str, comment_id: str, expand: str | None = None
    ) -> Comment:
        """``GET …/comments/{comment_id}`` → a single comment.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            comment_id: The comment's id.
            expand: The extras to embed.

        Returns:
            The comment.

        Examples:
            >>> tracker.entities.comments_get("project", "655f23", "23").text
            'hi'
        """
        endpoint = endpoints.get_comment(entity_type, entity_id, comment_id, expand=expand)
        return self._session.send(endpoint)

    def comments_create(self, entity_type: str, entity_id: str, body: dict[str, Any]) -> Comment:
        """``POST …/comments`` — add a comment. Returns the created comment.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            body: The new comment: its text and optional summonees.

        Returns:
            The created comment.

        Examples:
            >>> tracker.entities.comments_create("project", "655f25", {"text": "Готово"}).id
            22
        """
        return self._session.send(endpoints.create_comment(entity_type, entity_id, body))

    def comments_edit(
        self, entity_type: str, entity_id: str, comment_id: str, body: dict[str, Any]
    ) -> Comment:
        """``PATCH …/comments/{comment_id}`` — edit a comment. Returns the updated comment.

        The live v3 API only accepts the per-comment route (a PATCH on the ``…/comments``
        collection answers 405), so the comment id travels in the path, not the body.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            comment_id: The comment's id.
            body: The comment fields to change.

        Returns:
            The updated comment.

        Examples:
            >>> tracker.entities.comments_edit("goal", "g27", "27", {"text": "Fixed typo"}).text
            'Fixed typo'
        """
        endpoint = endpoints.edit_comment(entity_type, entity_id, comment_id, body)
        return self._session.send(endpoint)

    def comments_delete(self, entity_type: str, entity_id: str, comment_id: str) -> None:
        """Delete a comment from an entity. Raises on non-2xx.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            comment_id: The comment's id.

        Examples:
            >>> tracker.entities.comments_delete("portfolio", "pf28", "28")
        """
        self._session.send(endpoints.delete_comment(entity_type, entity_id, comment_id))

    # ---- checklists -------------------------------------------------------------------------

    def checklists_create(
        self, entity_type: str, entity_id: str, body: list[dict[str, Any]]
    ) -> Entity:
        """``POST …/checklistItems`` — add items (``body`` is a JSON array). Returns the entity.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            body: The items to add.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.checklists_create(
            ...     "project", "655f29", [{"text": "Draft"}, {"text": "Review"}]
            ... ).id
            '655f29'
        """
        return self._session.send(endpoints.create_checklist_items(entity_type, entity_id, body))

    def checklists_edit(
        self, entity_type: str, entity_id: str, body: list[dict[str, Any]]
    ) -> Entity:
        """``PATCH …/checklistItems`` — replace items (``body`` is a JSON array of ``{id, …}``).

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            body: The items to replace, each with its ``id``.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.checklists_edit(
            ...     "goal", "g30", [{"id": "5f", "text": "Renamed"}, {"id": "6a", "text": "Second"}]
            ... ).id
            'g30'
        """
        return self._session.send(endpoints.edit_checklist(entity_type, entity_id, body))

    def checklists_edit_item(
        self, entity_type: str, entity_id: str, item_id: str, body: dict[str, Any]
    ) -> Entity:
        """``PATCH …/checklistItems/{item_id}`` — edit one item. Returns the entity.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            item_id: The checklist item's id.
            body: The item fields to change.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.checklists_edit_item(
            ...     "portfolio", "pf32", "1f", {"text": "Sign off", "checked": True}
            ... ).id
            'pf32'
        """
        endpoint = endpoints.edit_checklist_item(entity_type, entity_id, item_id, body)
        return self._session.send(endpoint)

    def checklists_delete(self, entity_type: str, entity_id: str) -> Entity:
        """``DELETE …/checklistItems`` — clear the whole checklist. Returns the entity.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.checklists_delete("project", "655f34").id
            '655f34'
        """
        return self._session.send(endpoints.delete_checklist(entity_type, entity_id))

    def checklists_delete_item(self, entity_type: str, entity_id: str, item_id: str) -> Entity:
        """``DELETE …/checklistItems/{item_id}`` — remove one item. Returns the entity.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            item_id: The checklist item's id.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.checklists_delete_item("goal", "g35", "3f").id
            'g35'
        """
        return self._session.send(endpoints.delete_checklist_item(entity_type, entity_id, item_id))

    def checklists_move(
        self, entity_type: str, entity_id: str, item_id: str, body: dict[str, Any]
    ) -> Entity:
        """``POST …/checklistItems/{item_id}/_move`` — reorder an item. Returns the entity.

        ``body`` is ``{"before": "<item id>"}``.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            item_id: The checklist item's id.
            body: The new position, as ``{"before": "<item id>"}``.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.checklists_move("portfolio", "pf36", "4f", {"before": "5a"}).id
            'pf36'
        """
        endpoint = endpoints.move_checklist_item(entity_type, entity_id, item_id, body)
        return self._session.send(endpoint)

    # ---- links ------------------------------------------------------------------------------

    def links_list(
        self, entity_type: str, entity_id: str, fields: str | None = None
    ) -> ItemList[Link]:
        """``GET …/links`` → the entity's links to other entities.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            fields: The extra link fields to include, comma-separated.

        Returns:
            The entity's links.

        Examples:
            >>> tracker.entities.links_list("project", "655f38").root[0].type
            'relates'
        """
        return self._session.send(endpoints.list_links(entity_type, entity_id, fields=fields))

    def links_create(self, entity_type: str, entity_id: str, body: dict) -> None:
        """Create a link (``body`` is ``{relationship, entity}``). Raises on non-2xx.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            body: The link, as ``{"relationship": ..., "entity": ...}``.

        Examples:
            >>> tracker.entities.links_create(
            ...     "portfolio", "pf40", {"relationship": "depends on", "entity": "pf41"}
            ... )
        """
        self._session.send(endpoints.create_link(entity_type, entity_id, body))

    def links_delete(self, entity_type: str, entity_id: str, right: str) -> None:
        """Delete the link to entity ``right``. Raises on non-2xx.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            right: The id of the linked entity.

        Examples:
            >>> tracker.entities.links_delete("goal", "g42", "g43")
        """
        self._session.send(endpoints.delete_link(entity_type, entity_id, right))

    # ---- attachments ------------------------------------------------------------------------

    def attachments_list(self, entity_type: str, entity_id: str) -> ItemList[Attachment]:
        """``GET …/attachments`` → files attached to the entity (metadata only).

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.

        Returns:
            The entity's attachments.

        Examples:
            >>> tracker.entities.attachments_list("project", "655f44").root[0].name
            'Shops.csv'
        """
        return self._session.send(endpoints.list_attachments(entity_type, entity_id))

    def attachments_get(self, entity_type: str, entity_id: str, file_id: str) -> Attachment:
        """``GET …/attachments/{file_id}`` → one attachment's metadata (name, size, download URL).

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            file_id: The attachment's id.

        Returns:
            The attachment's metadata.

        Examples:
            >>> tracker.entities.attachments_get("goal", "g45", "45").name
            'flowers.jpg'
        """
        return self._session.send(endpoints.get_attachment(entity_type, entity_id, file_id))

    def attachment_download(self, file_id: str, filename: str) -> bytes:
        r"""Download an attachment's raw bytes (a non-2xx answer raises a typed error).

        Binary output is CLI/SDK-only — never an MCP payload. ``file_id`` and ``filename`` come
        from :meth:`attachments_list` / :meth:`attachments_get` (the ``id`` and ``name`` fields).

        Args:
            file_id: The attachment's id.
            filename: The attachment's file name.

        Returns:
            The attachment's raw bytes.

        Examples:
            >>> tracker.entities.attachment_download("46", "flowers.jpg")[:4]
            b'\xff\xd8\xff\xe0'
        """
        return self._session.send(endpoints.download_attachment(file_id, filename))

    def attachments_attach(self, entity_type: str, entity_id: str, temp_file_id: str) -> Entity:
        """``POST …/attachments/{temp_file_id}`` — attach a previously uploaded temp file.

        Returns the updated entity. ``temp_file_id`` is the id of a file uploaded to the temp
        attachments endpoint.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            temp_file_id: The id of the uploaded temporary file.

        Returns:
            The updated entity.

        Examples:
            >>> tracker.entities.attachments_attach("portfolio", "pf47", "tmp47").id
            'pf47'
        """
        return self._session.send(endpoints.attach_file(entity_type, entity_id, temp_file_id))

    def attachments_delete(self, entity_type: str, entity_id: str, file_id: str) -> None:
        """Detach a file from an entity. Raises on non-2xx.

        The live API answers with an empty body.

        Args:
            entity_type: The entity type (``project``, ``portfolio`` or ``goal``).
            entity_id: The entity's id.
            file_id: The attachment's id.

        Examples:
            >>> tracker.entities.attachments_delete("project", "655f48", "48")
        """
        self._session.send(endpoints.delete_attachment(entity_type, entity_id, file_id))
