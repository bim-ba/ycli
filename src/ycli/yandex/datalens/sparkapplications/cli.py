"""`datalens sparkapplications` commands."""

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.sparkapplications.models import SparkApplication, SparkApplicationLog
from ycli.yandex.models import ItemList

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
    *,
    config: AppConfig,
    datalens: DataLensClient,
) -> ItemList[SparkApplication]:
    """List the applications of a Spark cluster (auto-paginated)."""
    cap = config.http.cap(limit, all_=all_)
    return datalens.sparkapplications.list(cluster_id, filter=filter or None, limit=cap)


@app.command(epilog=UNMEASURED)
def get(
    cluster_id: SparkClusterArg,
    application_id: ApplicationOption,
    *,
    datalens: DataLensClient,
) -> SparkApplication:
    """Print one Spark application: its status, its times and what it runs."""
    return datalens.sparkapplications.get(cluster_id, application_id=application_id)


@app.command(
    epilog="Experimental in the DataLens API, written from its document and never called: "
    "not measured."
)
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
