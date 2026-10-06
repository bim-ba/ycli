"""DataLens Spark applications client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.sparkapplications import endpoints
from ycli.yandex.datalens.sparkapplications.models import SparkApplication
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ycli.yandex.datalens.models import LakehouseOperation
    from ycli.yandex.datalens.sparkapplications.models import (
        SparkApplicationCreate,
        SparkApplicationLog,
    )


class SparkApplicationsClient(Resource):
    """Spark applications: the jobs of a Spark cluster, their state and their logs.

    Experimental in the DataLens API and written from its document: the owner's instance has no
    Spark cluster, so no reply was measured. A cluster nothing knows answers
    ``403 Permission denied``, not ``404``.
    """

    def list(
        self,
        cluster_id: str,
        *,
        filter: Sequence[str] | None = None,  # noqa: A002  # the API's own name for it
        limit: int | None = None,
    ) -> ItemList[SparkApplication]:
        """``listSparkApplications`` → the applications of a cluster (not measured).

        Capped at ``limit`` (``None`` = every application). The cluster is required: without
        it the API answers ``400``.

        Args:
            cluster_id: The Spark cluster's id.
            filter: Conditions, all of which must hold; each is ``field="value"`` over ``name``,
                ``created_by``, ``application_type`` or ``catalog_id``.
            limit: The most applications to return; ``None`` returns every one.

        Returns:
            The applications of the cluster.

        Examples:
            >>> found = datalens.sparkapplications.list("sc00000000001").root
            >>> [(application.id, application.status) for application in found]
            [('app0000000001', 'RUNNING')]
        """
        paged = endpoints.list_(cluster_id, filter=filter)
        return ItemList[SparkApplication](list(self._session.iterate(paged, limit=limit)))

    def get(self, cluster_id: str, *, application_id: str) -> SparkApplication:
        """``getSparkApplication`` → one Spark application (not measured).

        Args:
            cluster_id: The Spark cluster's id.
            application_id: The application's id.

        Returns:
            The application: its status, its times and what it runs.

        Examples:
            >>> datalens.sparkapplications.get("sc00000000001", application_id="app0000000001").name
            'nightly'
        """
        return self._session.send(endpoints.get(cluster_id, application_id=application_id))

    def create(self, body: SparkApplicationCreate) -> LakehouseOperation:
        """``createSparkApplication`` — make a Spark application (not measured, never called).

        The request is one of three kinds, told apart by the field that holds the application:
        ``sparkApplication`` (a JAR), ``pysparkApplication`` (a Python file) or
        ``sparkConnectApplication``.

        Args:
            body: The application to make: the cluster, a name, the catalogs to attach and
                exactly one of the three kinds.

        Returns:
            The operation that makes it.

        Examples:
            >>> from ycli.yandex.datalens.sparkapplications.models import SparkApplicationCreate
            >>> new = SparkApplicationCreate.model_validate(
            ...     {
            ...         "clusterId": "sc00000000001",
            ...         "name": "nightly",
            ...         "pysparkApplication": {"mainPythonFileUri": "s3a://bucket/jobs/nightly.py"},
            ...     }
            ... )
            >>> datalens.sparkapplications.create(new).id
            'op0000000000022'
        """
        return self._session.send(endpoints.create(body))

    def cancel(self, cluster_id: str, *, application_id: str) -> LakehouseOperation:
        """``cancelSparkApplication`` — stop a Spark application (not measured, never called).

        Args:
            cluster_id: The Spark cluster's id.
            application_id: The application's id.

        Returns:
            The operation that cancels it.

        Examples:
            >>> datalens.sparkapplications.cancel(
            ...     "sc00000000001", application_id="app0000000001"
            ... ).id
            'op0000000000021'
        """
        return self._session.send(endpoints.cancel(cluster_id, application_id=application_id))

    def log_list(
        self,
        cluster_id: str,
        *,
        application_id: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SparkApplicationLog:
        """``listSparkApplicationLog`` → one fragment of an application's log (not measured).

        Give ``next_page_token`` of a fragment back as ``page_token`` for the next one.

        Args:
            cluster_id: The Spark cluster's id.
            application_id: The application's id.
            page_size: The most characters the fragment may hold.
            page_token: The token of the fragment to read; the first when left out.

        Returns:
            The fragment and the token of the next one.

        Examples:
            >>> fragment = datalens.sparkapplications.log_list(
            ...     "sc00000000001", application_id="app0000000001"
            ... )
            >>> fragment.content, fragment.next_page_token
            ('driver started', 'l2')
        """
        return self._session.send(
            endpoints.log_list(
                cluster_id,
                application_id=application_id,
                page_size=page_size,
                page_token=page_token,
            )
        )
