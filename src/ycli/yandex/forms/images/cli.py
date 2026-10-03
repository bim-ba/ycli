"""`forms images` commands: upload (a binary payload, so CLI/SDK only) and clone."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.images.models import Image, ImageClone
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,
)

app = typer.Typer(name="images", help="Forms images.", no_args_is_help=True)

# Module-level Annotated alias so ``Path`` is referenced at runtime (typer resolves annotations
# via get_type_hints), keeping the import out of a TYPE_CHECKING block.
ImagePathArg = Annotated[
    Path, typer.Argument(metavar="IMAGE_PATH", help="Local image file to upload.")
]


@app.command()
def upload(survey_id: SurveyIdArg, image_path: ImagePathArg, *, forms: FormsClient) -> Image:
    """Upload an image to add to a form (POST …/images); returns the image id and links."""
    return forms.images.upload(survey_id, filename=image_path.name, data=image_path.read_bytes())


@app.command()
def clone(
    survey_id: SurveyIdArg,
    image_id: Annotated[
        int | None, typer.Option("--image-id", help="Id of the image to clone.")
    ] = None,
    name: Annotated[str | None, typer.Option(help="File name for the clone.")] = None,
    link: Annotated[
        list[str] | None,
        typer.Option("--link", help="SIZE=URL of the image to clone (repeatable)."),
    ] = None,
    *,
    forms: FormsClient,
) -> Image:
    """Copy an existing image into the form (POST …/images/clone); returns the new image."""
    links = dict(item.split("=", 1) for item in link) if link else None
    body = ImageClone(id=image_id, links=links, name=name)
    return forms.images.clone(survey_id, body)
