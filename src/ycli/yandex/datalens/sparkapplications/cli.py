"""`datalens sparkapplications` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.body_fields import CallerFields
from ycli.cli.typedefs import AllOption, LimitOption, NextOption
from ycli.settings import AppConfig
from ycli.yandex.core.listing import Listing
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.sparkapplications.models import (
    SparkApplication,
    SparkApplicationCreate,
    SparkApplicationLog,
)

UNMEASURED = (
    "Experimental in the DataLens API and written from its document: not measured. A cluster "
    "nothing knows answers 403 Permission denied, not 404."
)
app = typer.Typer(
    name="sparkapplications",
    help="DataLens Spark applications (experimental in the API).",
    no_args_is_help=True,
)

SparkClusterArg = Annotated[
    str, typer.Argument(metavar="CLUSTER_ID", help="Id of the Spark cluster.")
]
ApplicationOption = Annotated[
    str, typer.Option("--application-id", help="Id of the Spark application.")
]


@app.command("list", epilog=UNMEASURED)
def list_(
    cluster_id: SparkClusterArg,
    filter: Annotated[  # noqa: A002  # the API's own name for it
        list[str] | None,
        typer.Option(
            "--filter",
            help='A condition, all must hold: name="…", created_by="…", '
            'application_type="…", catalog_id="…" (repeatable).',
        ),
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    next_: NextOption = None,
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> Listing[SparkApplication]:
    """List the applications of a Spark cluster (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.sparkapplications.list(cluster_id, filter=filter or None, limit=cap, next=next_)


@app.command(epilog=UNMEASURED)
def get(
    cluster_id: SparkClusterArg,
    application_id: ApplicationOption,
    *,
    datalens: DataLensClient,
) -> SparkApplication:
    """Print one Spark application: its status, its times and what it runs."""
    return datalens.sparkapplications.get(cluster_id, application_id=application_id)


NEVER_CALLED = (
    "Experimental in the DataLens API, written from its document and never called: not measured."
)


@app.command(epilog=NEVER_CALLED)
def create(
    cluster_id: SparkClusterArg,
    name: Annotated[str | None, typer.Option("--name", help="The application's name.")] = None,
    catalogs: Annotated[
        list[str] | None,
        typer.Option(
            "--catalogs",
            help='A REST catalog to attach, as a JSON object: {"catalogId": "…"} (repeatable).',
        ),
    ] = None,
    spark_application: Annotated[
        str | None,
        typer.Option(
            "--spark-application",
            help="An application in a JAR, as a JSON object: "
            '{"mainJarFileUri": "…", "mainClass": "…", "args": ["…"]}.',
        ),
    ] = None,
    pyspark_application: Annotated[
        str | None,
        typer.Option(
            "--pyspark-application",
            help="An application in a Python file, as a JSON object: "
            '{"mainPythonFileUri": "…", "args": ["…"]}.',
        ),
    ] = None,
    spark_connect_application: Annotated[
        str | None,
        typer.Option(
            "--spark-connect-application",
            help='A Spark Connect application, as a JSON object: {"properties": {"…": "…"}}.',
        ),
    ] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Make a Spark application on a cluster; prints the operation that makes it.

    Give exactly one of the three kinds. --body-file and -F give the request itself
    (`pysparkApplication`, `catalogs`, `name`); a flag wins over them.
    """
    # The body is a union of three kinds: the file and -F are merged before it is validated.
    kinds = {
        "sparkApplication": spark_application,
        "pysparkApplication": pyspark_application,
        "sparkConnectApplication": spark_connect_application,
    }
    given = {
        "clusterId": cluster_id,
        "name": name,
        "catalogs": [json.loads(item) for item in catalogs] if catalogs else None,
        **{field: None if value is None else json.loads(value) for field, value in kinds.items()},
    }
    body = caller.over({field: value for field, value in given.items() if value is not None})
    return datalens.sparkapplications.create(SparkApplicationCreate.model_validate(body))


@app.command(epilog=NEVER_CALLED)
def cancel(
    cluster_id: SparkClusterArg,
    application_id: ApplicationOption,
    *,
    datalens: DataLensClient,
) -> LakehouseOperation:
    """Stop a Spark application; prints the operation that cancels it."""
    return datalens.sparkapplications.cancel(cluster_id, application_id=application_id)


@app.command("log-list", epilog=UNMEASURED)
def log_list(
    cluster_id: SparkClusterArg,
    application_id: ApplicationOption,
    page_size: Annotated[
        int | None,
        typer.Option("--page-size", help="The most characters the fragment may hold."),
    ] = None,
    page_token: Annotated[
        str | None,
        typer.Option("--page-token", help="The token of the fragment to read; the first if not."),
    ] = None,
    *,
    datalens: DataLensClient,
) -> SparkApplicationLog:
    """Print one fragment of an application's log, and the token of the next."""
    return datalens.sparkapplications.log_list(
        cluster_id, application_id=application_id, page_size=page_size, page_token=page_token
    )
