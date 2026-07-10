"""`forms images` commands (image upload — CLI/SDK only, never MCP)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)

app = typer.Typer(name="images", help="Forms images.", no_args_is_help=True)

# Module-level Annotated alias so ``Path`` is referenced at runtime (typer resolves annotations
# via get_type_hints), keeping the import out of a TYPE_CHECKING block.
ImagePathArg = Annotated[
    Path, typer.Argument(metavar="IMAGE_PATH", help="Local image file to upload.")
]


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def upload(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    image_path: ImagePathArg,
) -> None:
    """Upload an image to add to a form (POST …/images); returns the image id and links."""
    app_ctx = AppContext.from_typer_context(ctx)
    result = app_ctx.forms.images.upload(
        survey_id, filename=image_path.name, data=image_path.read_bytes()
    )
    Serializer.serialize(result, app_ctx.strategy, app_ctx.console)
