"""DataLens cloud environments client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.cloudenvironments import endpoints
from ycli.yandex.datalens.cloudenvironments.models import CloudEnvironment
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.datalens.cloudenvironments.models import (
        CloudEnvironmentNewStorage,
        CloudEnvironmentStorageChange,
    )
    from ycli.yandex.datalens.models import LakehouseOperation


class CloudEnvironmentsClient(Resource):
    """Cloud environments: a cloud and a subnet DataLens runs clusters in, with a bucket.

    Experimental in the DataLens API. Listing is measured; the rest is written from the
    document: making, changing and deleting an environment creates cloud resources and was
    never called.
    """

    def list(
        self,
        *,
        filter: Sequence[str] | None = None,  # noqa: A002  # the API's own name for it
        include_permissions: bool | None = None,
        limit: int | None = None,
    ) -> ItemList[CloudEnvironment]:
        """``listCloudEnvironments`` → the cloud environments, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every environment).

        Args:
            filter: Conditions, all of which must hold; each is ``field="value"`` over ``name``,
                ``cloud_id``, ``status`` or ``created_by_id``.
            include_permissions: Also say what the caller may do with each one.
            limit: The most environments to return; ``None`` returns every one.

        Returns:
            The cloud environments.

        Examples:
            >>> found = datalens.cloudenvironments.list(filter=['status="READY"']).root
            >>> [(environment.id, environment.status) for environment in found]
            [('env0000000001', 'READY')]
        """
        paged = endpoints.list_(filter=filter, include_permissions=include_permissions)
        return ItemList[CloudEnvironment](list(self._session.iterate(paged, limit=limit)))

    def get(
        self,
        id: str,  # noqa: A002  # the API's own name for it
        *,
        include_permissions: bool | None = None,
    ) -> CloudEnvironment:
        """``getCloudEnvironment`` → one cloud environment (not measured).

        An id nothing knows answers ``403 Permission denied``, not ``404``.

        Args:
            id: The environment's id.
            include_permissions: Also say what the caller may do with it.

        Returns:
            The environment: its cloud, its subnet, its status and its storage.

        Examples:
            >>> datalens.cloudenvironments.get("env0000000001").name
            'Analytics'
        """
        return self._session.send(endpoints.get(id, include_permissions=include_permissions))

    def create(
        self,
        *,
        name: str,
        cloud_id: str,
        subnet_id: str,
        description: str | None = None,
        security_group_ids: Sequence[str] | None = None,
        storage: CloudEnvironmentNewStorage | None = None,
    ) -> LakehouseOperation:
        """``createCloudEnvironment`` — make a cloud environment (not measured, never called).

        It creates resources in a cloud, which may be billed. The reply is an operation: ask
        ``getLakehouseOperation`` for it until ``done``.

        Args:
            name: The environment's name.
            cloud_id: The cloud to make it in.
            subnet_id: The subnet it uses.
            description: A description.
            security_group_ids: The security groups it uses.
            storage: The settings of its storage bucket; no bucket when left out.

        Returns:
            The operation that makes it.

        Examples:
            >>> started = datalens.cloudenvironments.create(
            ...     name="Analytics", cloud_id="b1g00000000000000001", subnet_id="e9b0000000001"
            ... )
            >>> started.id, started.done
            ('op0000000000001', False)
        """
        return self._session.send(
            endpoints.create(
                name=name,
                cloud_id=cloud_id,
                subnet_id=subnet_id,
                description=description,
                security_group_ids=security_group_ids,
                storage=storage,
            )
        )

    def update(
        self,
        id: str,  # noqa: A002  # the API's own name for it
        *,
        name: str | None = None,
        description: str | None = None,
        security_group_ids: Sequence[str] | None = None,
        storage: CloudEnvironmentStorageChange | None = None,
    ) -> LakehouseOperation:
        """``updateCloudEnvironment`` — change the fields given (not measured, never called).

        The cloud and the subnet cannot change. An empty description clears it.

        Args:
            id: The environment's id.
            name: A new name.
            description: A new description.
            security_group_ids: The security groups it is to use.
            storage: New settings of its storage bucket.

        Returns:
            The operation that changes it.

        Examples:
            >>> datalens.cloudenvironments.update("env0000000001", name="Analytics, EU").id
            'op0000000000002'
        """
        return self._session.send(
            endpoints.update(
                id,
                name=name,
                description=description,
                security_group_ids=security_group_ids,
                storage=storage,
            )
        )

    def delete(
        self,
        id: str,  # noqa: A002  # the API's own name for it
    ) -> LakehouseOperation:
        """``deleteCloudEnvironment`` — delete a cloud environment (not measured, never called).

        Args:
            id: The environment's id.

        Returns:
            The operation that deletes it.

        Examples:
            >>> datalens.cloudenvironments.delete("env0000000001").id
            'op0000000000003'
        """
        return self._session.send(endpoints.delete(id))
