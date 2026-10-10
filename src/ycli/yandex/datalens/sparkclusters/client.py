"""DataLens Spark clusters client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.sparkclusters import endpoints

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.core.listing import Listing
    from ycli.yandex.datalens.models import LakehouseOperation
    from ycli.yandex.datalens.sparkclusters.models import (
        NewClusterConfig,
        SparkCluster,
        SparkResourcePreset,
    )


class SparkClustersClient(Resource):
    """Spark clusters of DataLens: an experimental API, wrapped by its document, not measured.

    A cluster is paid for while it runs. A write answers with an operation that goes on after
    the reply: ask ``lakehouseoperations.get`` for it until ``done`` to learn how it ended.
    """

    def list(
        self,
        *,
        limit: int | None = None,
        next: str | None = None,
        collection_id: str | None = None,
        filter: Sequence[str] | None = None,  # noqa: A002  # the API's own name for it
    ) -> Listing[SparkCluster]:
        """``listSparkClusters`` → the Spark clusters, draining ``nextPageToken``.

        Args:
            limit: The most clusters to return; ``None`` returns every cluster.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.
            collection_id: Keep the clusters of one collection.
            filter: Filter expressions of the API.

        Returns:
            The clusters found.

        Examples:
            >>> [cluster.name for cluster in datalens.sparkclusters.list(limit=45)]
            ['etl', 'adhoc']
        """
        paged = endpoints.list_(
            collection_id=collection_id, filter=None if filter is None else [*filter]
        )
        return self._session.iterate(paged, limit=limit, next=next)

    def get(self, id: str) -> SparkCluster:  # noqa: A002  # the API's own name for it
        """``getSparkCluster`` → one Spark cluster: its settings, health and status.

        Args:
            id: The cluster's id.

        Returns:
            The cluster.

        Examples:
            >>> datalens.sparkclusters.get("sc000000000001").status
            'RUNNING'
        """
        return self._session.send(endpoints.get(id))

    def create(
        self,
        *,
        collection_id: str,
        cloud_environment_id: str,
        name: str,
        config: NewClusterConfig,
        description: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> LakehouseOperation:
        """``createSparkCluster`` — create a Spark cluster → the operation that creates it.

        Args:
            collection_id: The collection to create the cluster in.
            cloud_environment_id: The cloud environment the cluster runs in.
            name: The cluster's name.
            config: The Spark version, the pools of the driver and executors, and the rest.
            description: A description of the cluster.
            labels: Labels of the cluster.

        Returns:
            The operation; it goes on after the reply.

        Examples:
            >>> from ycli.yandex.datalens.sparkclusters.models import NewClusterConfig
            >>> datalens.sparkclusters.create(
            ...     collection_id="col00000000001",
            ...     cloud_environment_id="env00000000001",
            ...     name="etl",
            ...     config=NewClusterConfig(sparkVersion="3.5"),
            ... ).done
            False
        """
        return self._session.send(
            endpoints.create(
                collection_id=collection_id,
                cloud_environment_id=cloud_environment_id,
                name=name,
                config=config,
                description=description,
                labels=labels,
            )
        )

    def delete(self, id: str) -> LakehouseOperation:  # noqa: A002  # the API's own name for it
        """``deleteSparkCluster`` — delete a Spark cluster → the operation that deletes it.

        Args:
            id: The cluster's id.

        Returns:
            The operation; it goes on after the reply.

        Examples:
            >>> datalens.sparkclusters.delete("sc000000000001").id
            'op000000000001'
        """
        return self._session.send(endpoints.delete(id))

    def start(self, cluster_id: str) -> LakehouseOperation:
        """``startSparkCluster`` — start a stopped Spark cluster → the operation.

        Args:
            cluster_id: The cluster's id.

        Returns:
            The operation; it goes on after the reply.

        Examples:
            >>> datalens.sparkclusters.start("sc000000000001").id
            'op000000000001'
        """
        return self._session.send(endpoints.start(cluster_id))

    def stop(self, cluster_id: str) -> LakehouseOperation:
        """``stopSparkCluster`` — stop a running Spark cluster → the operation.

        Args:
            cluster_id: The cluster's id.

        Returns:
            The operation; it goes on after the reply.

        Examples:
            >>> datalens.sparkclusters.stop("sc000000000001").id
            'op000000000001'
        """
        return self._session.send(endpoints.stop(cluster_id))

    def resource_presets_list(
        self, cloud_environment_id: str, *, limit: int | None = None, next: str | None = None
    ) -> Listing[SparkResourcePreset]:
        """``listSparkResourcePresets`` → the sizes an instance of a cluster can take.

        Args:
            cloud_environment_id: The cloud environment the presets are for.
            limit: The most presets to return; ``None`` returns every preset.
            next: What an earlier call returned as ``next``. The token carries its listing;
                give what is required again, and nothing else but the limit.

        Returns:
            The presets found.

        Examples:
            >>> found = datalens.sparkclusters.resource_presets_list("env00000000001", limit=45)
            >>> [preset.id for preset in found]
            ['c2-m8', 'c4-m16']
        """
        paged = endpoints.resource_presets_list(cloud_environment_id)
        return self._session.iterate(paged, limit=limit, next=next)

    def resource_presets_get(
        self, resource_preset_id: str, *, cloud_environment_id: str
    ) -> SparkResourcePreset:
        """``getSparkResourcePreset`` → one preset: its cores and its memory.

        Args:
            resource_preset_id: The preset's id.
            cloud_environment_id: The cloud environment the preset is asked for.

        Returns:
            The preset.

        Examples:
            >>> datalens.sparkclusters.resource_presets_get(
            ...     "c2-m8", cloud_environment_id="env00000000001"
            ... ).cores
            '2'
        """
        return self._session.send(
            endpoints.resource_presets_get(
                resource_preset_id, cloud_environment_id=cloud_environment_id
            )
        )
