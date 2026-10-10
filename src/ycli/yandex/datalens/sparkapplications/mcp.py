"""DataLens Spark applications FastMCP tools (read + write) — Depends DI, native errors."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import (
    LIMIT_CAP,
    RO,
    WRITE,
    All,
    Next,
    app_config,
    datalens_client,
    new_server,
)
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.sparkapplications.models import (
    SparkApplication,
    SparkApplicationCreate,
    SparkApplicationLog,
)
from ycli.yandex.models import Listed

mcp = new_server("datalens-sparkapplications")

SparkCluster = Annotated[str, Field(description="Id of the Spark cluster.")]
Application = Annotated[str, Field(description="Id of the Spark application.")]


@mcp.tool(
    name="sparkapplications_list", annotations={**RO, "title": "List DataLens Spark applications"}
)
def list_(
    cluster_id: SparkCluster,
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None,
        Field(
            description='Conditions, all of which must hold; each is ``field="value"`` over '
            "``name``, ``created_by``, ``application_type`` or ``catalog_id``."
        ),
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description=f"Max applications to return; {LIMIT_CAP}")
    ] = None,
    all: All = False,
    next: Next = None,
    client: DataLensClient = Depends(datalens_client),
    config: AppConfig = Depends(app_config),
) -> Listed[SparkApplication]:
    """The applications of a Spark cluster, auto-paginated.

    Experimental in the DataLens API and written from its document: not measured. A cluster
    nothing knows answers 403 Permission denied, not 404: it is not a lack of rights.
    """
    return client.sparkapplications.list(
        cluster_id, filter=filter, limit=config.http.tool_cap(limit, all_=all), next=next
    ).collect()


@mcp.tool(
    name="sparkapplications_get", annotations={**RO, "title": "Get DataLens Spark application"}
)
def get(
    cluster_id: SparkCluster,
    application_id: Application,
    client: DataLensClient = Depends(datalens_client),
) -> SparkApplication:
    """One Spark application: its status, its times and what it runs.

    Experimental in the DataLens API and written from its document: not measured. An id
    nothing knows answers 403 Permission denied, not 404.
    """
    return client.sparkapplications.get(cluster_id, application_id=application_id)


@mcp.tool(
    name="sparkapplications_create",
    annotations={**WRITE, "title": "Create DataLens Spark application"},
)
def create(
    body: Annotated[
        SparkApplicationCreate,
        Field(
            description="The application to make: ``clusterId``, a ``name``, the ``catalogs`` "
            "to attach, and exactly one of ``sparkApplication`` (a JAR), "
            "``pysparkApplication`` (a Python file) or ``sparkConnectApplication``."
        ),
    ],
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Make a Spark application on a cluster and return the operation that makes it.

    Experimental in the DataLens API, written from its document and never called: not
    measured. Ask the person before calling.
    """
    return client.sparkapplications.create(body)


@mcp.tool(
    name="sparkapplications_cancel",
    annotations={**WRITE, "title": "Cancel DataLens Spark application"},
)
def cancel(
    cluster_id: SparkCluster,
    application_id: Application,
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """Stop a Spark application and return the operation that cancels it.

    Experimental in the DataLens API, written from its document and never called: not measured.
    """
    return client.sparkapplications.cancel(cluster_id, application_id=application_id)


@mcp.tool(
    name="sparkapplications_log_list",
    annotations={**RO, "title": "Read the log of a DataLens Spark application"},
)
def log_list(
    cluster_id: SparkCluster,
    application_id: Application,
    page_size: Annotated[
        int | None, Field(description="The most characters the fragment may hold.")
    ] = None,
    page_token: Annotated[
        str | None,
        Field(description="The token of the fragment to read; the first when left out."),
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> SparkApplicationLog:
    """One fragment of an application's log, and the token of the next one.

    Give ``nextPageToken`` back as ``page_token`` to read on. Experimental in the DataLens API
    and written from its document: not measured.
    """
    return client.sparkapplications.log_list(
        cluster_id, application_id=application_id, page_size=page_size, page_token=page_token
    )
