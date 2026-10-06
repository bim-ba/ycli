"""DataLens Spark application operations, declared once (sans-IO).

Every one of them is marked experimental in the document DataLens publishes.

Examples:
    >>> get("sc1", application_id="app1").body
    {'clusterId': 'sc1', 'applicationId': 'app1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.schemas.spark_applications import (
    CancelSparkApplicationArgs,
    GetSparkApplicationArgs,
    ListSparkApplicationLogArgs,
    ListSparkApplicationsArgs,
)
from ycli.yandex.datalens.sparkapplications.models import (
    SparkApplication,
    SparkApplicationLog,
    SparkApplicationsPage,
)


def list_(
    cluster_id: str,
    *,
    filter: Sequence[str] | None,  # noqa: A002  # the API's own name for it
) -> Paged[SparkApplicationsPage, SparkApplication]:
    body = ListSparkApplicationsArgs(
        clusterId=cluster_id, filter=None if filter is None else list(filter)
    )
    return Paged(
        RPC("listSparkApplications", SparkApplicationsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.applications or [],
    )


def get(cluster_id: str, *, application_id: str) -> Endpoint[SparkApplication]:
    body = GetSparkApplicationArgs(clusterId=cluster_id, applicationId=application_id)
    return RPC("getSparkApplication", SparkApplication, json=body, effect=Effect.READ)


def cancel(cluster_id: str, *, application_id: str) -> Endpoint[LakehouseOperation]:
    body = CancelSparkApplicationArgs(clusterId=cluster_id, applicationId=application_id)
    return RPC("cancelSparkApplication", LakehouseOperation, json=body, effect=Effect.WRITE)


def log_list(
    cluster_id: str, *, application_id: str, page_size: int | None, page_token: str | None
) -> Endpoint[SparkApplicationLog]:
    # One fragment of a text, not a list of items: the caller asks for the next by its token.
    body = ListSparkApplicationLogArgs(
        clusterId=cluster_id,
        applicationId=application_id,
        pageSize=page_size,
        pageToken=page_token,
    )
    return RPC("listSparkApplicationLog", SparkApplicationLog, json=body, effect=Effect.READ)
