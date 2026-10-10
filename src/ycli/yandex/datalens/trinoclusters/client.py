"""DataLens Trino clusters client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.trinoclusters import endpoints

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ycli.yandex.core.listing import Listing
    from ycli.yandex.datalens.models import LakehouseOperation
    from ycli.yandex.datalens.trinoclusters.models import (
        TrinoCatalogToAdd,
        TrinoCluster,
        TrinoNewCatalog,
        TrinoResourcePreset,
        TrinoWorkerConfig,
    )


class TrinoClustersClient(Resource):
    """Trino clusters: a query engine DataLens runs in a cloud environment, over REST catalogs.

    Experimental in the DataLens API. Listing the clusters is measured; the rest is written
    from the document: a cluster is cloud resources that are billed while it runs, so making,
    starting, stopping and deleting one, and its catalogs, were never called. An id nothing
    knows answers ``403 Permission denied``, not ``404``.
    """

    def list(
        self,
        *,
        filter: Sequence[str] | None = None,  # noqa: A002  # the API's own name for it
        collection_id: str | None = None,
        catalog_id: str | None = None,
        limit: int | None = None,
        next: str | None = None,
    ) -> Listing[TrinoCluster]:
        """``listTrinoClusters`` → the Trino clusters, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every cluster).

        Args:
            filter: Conditions the clusters must meet.
            collection_id: Only the clusters of this collection.
            catalog_id: Only the clusters this REST catalog is attached to.
            limit: The most clusters to return; ``None`` returns every one.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The Trino clusters.

        Examples:
            >>> found = datalens.trinoclusters.list(collection_id="col0000000001").collect().items
            >>> [(cluster.id, cluster.status) for cluster in found]
            [('tc00000000001', 'RUNNING')]
        """
        paged = endpoints.list_(filter=filter, collection_id=collection_id, catalog_id=catalog_id)
        return self._session.iterate(paged, limit=limit, next=next)

    def get(
        self,
        id: str,  # noqa: A002  # the API's own name for it
    ) -> TrinoCluster:
        """``getTrinoCluster`` → one Trino cluster (not measured).

        Args:
            id: The cluster's id.

        Returns:
            The cluster: its configuration, its health, its status and its coordinator.

        Examples:
            >>> datalens.trinoclusters.get("tc00000000001").name
            'reports'
        """
        return self._session.send(endpoints.get(id))

    def create(
        self,
        *,
        collection_id: str,
        cloud_environment_id: str,
        name: str,
        worker_config: TrinoWorkerConfig,
        description: str | None = None,
        labels: Mapping[str, str] | None = None,
        catalogs_config: Sequence[TrinoNewCatalog] | None = None,
        trino_version: str | None = None,
    ) -> LakehouseOperation:
        """``createTrinoCluster`` — make a Trino cluster (not measured, never called).

        A cluster is cloud resources, billed while it runs. The reply is an operation: ask
        ``lakehouseoperations.get`` for it until ``done``.

        Args:
            collection_id: The DataLens collection to make it in.
            cloud_environment_id: The cloud environment to make it in.
            name: The cluster's name.
            worker_config: The workers: their resource preset and how many there may be.
            description: A description.
            labels: Labels, a name to a value.
            catalogs_config: The REST catalogs to attach.
            trino_version: The version of Trino; the service's own when left out.

        Returns:
            The operation that makes it.

        Examples:
            >>> from ycli.yandex.datalens.trinoclusters.models import TrinoWorkerConfig
            >>> workers = TrinoWorkerConfig.model_validate(
            ...     {"resources": {"resourcePresetId": "c4-m16"}}
            ... )
            >>> started = datalens.trinoclusters.create(
            ...     collection_id="col0000000001",
            ...     cloud_environment_id="env0000000001",
            ...     name="reports",
            ...     worker_config=workers,
            ... )
            >>> started.id
            'op0000000000011'
        """
        return self._session.send(
            endpoints.create(
                collection_id=collection_id,
                cloud_environment_id=cloud_environment_id,
                name=name,
                worker_config=worker_config,
                description=description,
                labels=labels,
                catalogs_config=catalogs_config,
                trino_version=trino_version,
            )
        )

    def delete(
        self,
        id: str,  # noqa: A002  # the API's own name for it
    ) -> LakehouseOperation:
        """``deleteTrinoCluster`` — delete a Trino cluster (not measured, never called).

        Args:
            id: The cluster's id.

        Returns:
            The operation that deletes it.

        Examples:
            >>> datalens.trinoclusters.delete("tc00000000001").id
            'op0000000000012'
        """
        return self._session.send(endpoints.delete(id))

    def start(self, cluster_id: str) -> LakehouseOperation:
        """``startTrinoCluster`` — start a stopped cluster (not measured, never called).

        A running cluster is billed.

        Args:
            cluster_id: The cluster's id.

        Returns:
            The operation that starts it.

        Examples:
            >>> datalens.trinoclusters.start("tc00000000001").id
            'op0000000000013'
        """
        return self._session.send(endpoints.start(cluster_id))

    def stop(self, cluster_id: str) -> LakehouseOperation:
        """``stopTrinoCluster`` — stop a running cluster (not measured, never called).

        Args:
            cluster_id: The cluster's id.

        Returns:
            The operation that stops it.

        Examples:
            >>> datalens.trinoclusters.stop("tc00000000001").id
            'op0000000000014'
        """
        return self._session.send(endpoints.stop(cluster_id))

    def catalog_create(self, cluster_id: str, *, catalog: TrinoCatalogToAdd) -> LakehouseOperation:
        """``addTrinoClusterCatalog`` — attach a REST catalog (not measured, never called).

        Args:
            cluster_id: The cluster's id.
            catalog: The catalog to attach, by its id.

        Returns:
            The operation that attaches it.

        Examples:
            >>> from ycli.yandex.datalens.trinoclusters.models import TrinoCatalogToAdd
            >>> catalog = TrinoCatalogToAdd.model_validate({"catalogId": "cat0000000001"})
            >>> datalens.trinoclusters.catalog_create("tc00000000001", catalog=catalog).id
            'op0000000000015'
        """
        return self._session.send(endpoints.catalog_create(cluster_id, catalog=catalog))

    def catalog_delete(self, cluster_id: str, *, catalog_id: str) -> LakehouseOperation:
        """``deleteTrinoClusterCatalog`` — detach a REST catalog (not measured, never called).

        The cluster loses the catalog; the catalog itself stays.

        Args:
            cluster_id: The cluster's id.
            catalog_id: The id of the catalog to detach.

        Returns:
            The operation that detaches it.

        Examples:
            >>> datalens.trinoclusters.catalog_delete(
            ...     "tc00000000001", catalog_id="cat0000000001"
            ... ).id
            'op0000000000016'
        """
        return self._session.send(endpoints.catalog_delete(cluster_id, catalog_id=catalog_id))

    def resource_presets_list(
        self, cloud_environment_id: str, *, limit: int | None = None, next: str | None = None
    ) -> Listing[TrinoResourcePreset]:
        """``listTrinoResourcePresets`` → the sizes a cluster's machines may have (not measured).

        The environment is required: without it the API answers ``400``.

        Args:
            cloud_environment_id: The cloud environment the presets are of.
            limit: The most presets to return; ``None`` returns every one.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The presets: an id, the cores and the memory of each.

        Examples:
            >>> presets = (
            ...     datalens.trinoclusters.resource_presets_list("env0000000001").collect().items
            ... )
            >>> [(preset.id, preset.cores) for preset in presets]
            [('c4-m16', '4')]
        """
        paged = endpoints.resource_presets_list(cloud_environment_id)
        return self._session.iterate(paged, limit=limit, next=next)

    def resource_preset_get(
        self, resource_preset_id: str, *, cloud_environment_id: str
    ) -> TrinoResourcePreset:
        """``getTrinoResourcePreset`` → one size of a cluster's machines (not measured).

        Args:
            resource_preset_id: The preset's id.
            cloud_environment_id: The cloud environment the preset is of.

        Returns:
            The preset: its cores and its memory.

        Examples:
            >>> datalens.trinoclusters.resource_preset_get(
            ...     "c4-m16", cloud_environment_id="env0000000001"
            ... ).memory
            '17179869184'
        """
        return self._session.send(
            endpoints.resource_preset_get(
                resource_preset_id, cloud_environment_id=cloud_environment_id
            )
        )
