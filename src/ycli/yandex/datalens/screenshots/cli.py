"""`datalens screenshots` commands: a picture of a dashboard or a chart, as a link or a file."""

import base64 as b64
import binascii
import json
from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.cli.typedefs import values_option
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.screenshots.models import ImageType, Screenshot
from ycli.yandex.errors import YandexUnexpectedReplyError

app = typer.Typer(
    name="screenshots",
    help="Pictures of DataLens dashboards and charts, rendered by DataLens (experimental).",
    no_args_is_help=True,
)

TypeOption = Annotated[
    str | None, values_option(ImageType, "--type", help="The format of the picture.")
]
Base64Option = Annotated[
    bool | None,
    typer.Option("--base64/--no-base64", help="Put the file itself in the reply, base64-encoded."),
]
S3Option = Annotated[
    bool | None,
    typer.Option("--s3/--no-s3", help="Put the file in S3 and reply with its link."),
]
WidthOption = Annotated[
    int | None, typer.Option("--width", help="The width of the page in pixels, at most 6000.")
]
HeightOption = Annotated[
    int | None,
    typer.Option("--height", help="The height of the page in pixels, at most 6000."),
]
FullPageOption = Annotated[
    bool | None,
    typer.Option(
        "--full-page/--no-full-page", help="Capture the whole page, not one screen of it."
    ),
]
QueryParamsOption = Annotated[
    str | None,
    typer.Option(
        "--query-params",
        help='Parameters of the page, as a JSON object: {"tab": "tab__2", "_theme": "dark"}.',
    ),
]
ImageOutputOption = Annotated[
    str | None,
    typer.Option(
        "--output",
        help="Write the picture to this path ('-' for stdout); the reply then carries it in "
        "base64, so it does not go with --s3 or --no-base64. Omitted, the reply is printed.",
    ),
]
RATE = "DataLens takes about three of these a minute; a 429 is retried with a back-off."


def _base64(output: str | None, base64: bool | None, s3: bool | None) -> bool | None:
    """What ``base64`` is sent as: a file is written only from a picture in the reply."""
    if output is None:
        return base64
    if s3 or base64 is False:
        # violation(arch-9): ycli's own --output, which needs the picture in the reply
        raise typer.BadParameter(
            "--output writes the picture in the reply: drop --s3 and --no-base64"
        )
    # violation(as-given): a file is written from the picture in the reply, which only base64
    # puts there.
    return True


def _image(reply: Screenshot) -> bytes:
    if reply.data is None:
        raise YandexUnexpectedReplyError(
            f"the reply holds no picture: {reply.code} {reply.message}"
        )
    try:
        return b64.b64decode(reply.data, validate=True)
    except binascii.Error as error:
        raise YandexUnexpectedReplyError("the reply holds no base64 picture") from error


@app.command("dashboard-get", epilog=RATE)
def dashboard_get(
    dash_id: Annotated[str, typer.Argument(metavar="DASH_ID", help="The dashboard to capture.")],
    type_: TypeOption = None,
    base64: Base64Option = None,
    s3: S3Option = None,
    width: WidthOption = None,
    height: HeightOption = None,
    full_page: FullPageOption = None,
    query_params: QueryParamsOption = None,
    output: ImageOutputOption = None,
    *,
    datalens: DataLensClient,
) -> Screenshot | BinaryResult:
    """Print the link to a picture of a dashboard, or write the picture to --output."""
    reply = datalens.screenshots.dashboard_get(
        dash_id,
        type=type_,
        base64=_base64(output, base64, s3),
        s3=s3,
        width=width,
        height=height,
        full_page=full_page,
        query_params=None if query_params is None else json.loads(query_params),
    )
    return reply if output is None else BinaryResult(_image(reply), output)


@app.command("chart-get", epilog=RATE)
def chart_get(
    chart_id: Annotated[str, typer.Argument(metavar="CHART_ID", help="The chart to capture.")],
    type_: TypeOption = None,
    base64: Base64Option = None,
    s3: S3Option = None,
    width: WidthOption = None,
    height: HeightOption = None,
    full_page: FullPageOption = None,
    query_params: QueryParamsOption = None,
    output: ImageOutputOption = None,
    *,
    datalens: DataLensClient,
) -> Screenshot | BinaryResult:
    """Print the link to a picture of a chart, or write the picture to --output."""
    reply = datalens.screenshots.chart_get(
        chart_id,
        type=type_,
        base64=_base64(output, base64, s3),
        s3=s3,
        width=width,
        height=height,
        full_page=full_page,
        query_params=None if query_params is None else json.loads(query_params),
    )
    return reply if output is None else BinaryResult(_image(reply), output)
