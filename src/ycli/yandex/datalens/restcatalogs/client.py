"""DataLens REST catalogs client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.restcatalogs import endpoints
from ycli.yandex.datalens.restcatalogs.models import RestCatalog
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ycli.yandex.datalens.models import LakehouseOperation
    from ycli.yandex.datalens.restcatalogs.models import (
        RestCatalogBucketSettings,
        RestCatalogSortField,
    )


class RestCatalogsClient(Resource):
    """REST catalogs: a catalog of tables with a bucket of its own, in a cloud environment.

    Experimental in the DataLens API. Listing is measured; making a catalog creates a bucket in
    a cloud and was never called: it is written from the document.
    """

    def list(
        self,
        *,
        cloud_environment_id: str | None = None,
        filter: Sequence[str] | None = None,  # noqa: A002  # the API's own name for it
        sort_by: RestCatalogSortField | None = None,
        reverse_order: bool | None = None,
        include_permissions: bool | None = None,
        limit: int | None = None,
    ) -> ItemList[RestCatalog]:
        """``listCatalogs`` → the REST catalogs, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every catalog).

        Args:
            cloud_environment_id: Only the catalogs of this environment; all when left out.
            filter: Conditions such as ``name="…"``; only the catalogs that match are kept.
            sort_by: The field to sort by: ``name``, ``createdAt`` or ``updatedAt``.
            reverse_order: Sort the other way round.
            include_permissions: Also say what the caller may do with each one.
            limit: The most catalogs to return; ``None`` returns every one.

        Returns:
            The REST catalogs.

        Examples:
            >>> found = datalens.restcatalogs.list(cloud_environment_id="env0000000001").root
            >>> [(catalog.id, catalog.name) for catalog in found]
            [('cat0000000001', 'lake')]
        """
        paged = endpoints.list_(
            cloud_environment_id=cloud_environment_id,
            filter=filter,
            sort_by=sort_by,
            reverse_order=reverse_order,
            include_permissions=include_permissions,
        )
        return ItemList[RestCatalog](list(self._session.iterate(paged, limit=limit)))

    def create(
        self,
        *,
        cloud_environment_id: str,
        name: str,
        bucket_settings: RestCatalogBucketSettings,
        description: str | None = None,
        labels: Mapping[str, str] | None = None,
    ) -> LakehouseOperation:
        """``createRestCatalog`` — make a REST catalog (not measured, never called).

        It creates a bucket in a cloud, which may be billed. The reply is an operation: ask
        ``lakehouseoperations.get`` for it until ``done``, then look at its ``error`` or its
        ``response``.

        Args:
            cloud_environment_id: The cloud environment to make it in.
            name: The catalog's name.
            bucket_settings: The settings of its bucket; an empty one is valid by the document.
            description: A description.
            labels: Labels, a name to a value.

        Returns:
            The operation that makes it.

        Examples:
            >>> from ycli.yandex.datalens.restcatalogs.models import RestCatalogBucketSettings
            >>> started = datalens.restcatalogs.create(
            ...     cloud_environment_id="env0000000001",
            ...     name="lake",
            ...     bucket_settings=RestCatalogBucketSettings(),
            ... )
            >>> started.id, started.done
            ('op0000000000006', False)
        """
        return self._session.send(
            endpoints.create(
                cloud_environment_id=cloud_environment_id,
                name=name,
                bucket_settings=bucket_settings,
                description=description,
                labels=labels,
            )
        )
