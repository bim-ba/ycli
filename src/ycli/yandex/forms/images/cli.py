"""`forms images` commands (image upload — a binary payload, so CLI/SDK only)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.images.models import Image
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,
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
def upload(survey_id: SurveyIdArg, image_path: ImagePathArg, *, forms: FormsClient) -> Image:
    """Upload an image to add to a form (POST …/images); returns the image id and links."""
    result = forms.images.upload(survey_id, filename=image_path.name, data=image_path.read_bytes())
    return result
