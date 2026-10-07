"""Forms images FastMCP tools: ``images_clone`` only.

The other endpoint is a multipart image **upload** taking raw file bytes — a binary payload a
JSON MCP tool cannot carry — so it stays on the CLI and SDK.
"""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import WRITE, forms_client, new_server
from ycli.yandex.forms.images.models import Image, ImageClone

mcp = new_server("forms-images")


@mcp.tool(name="images_clone", annotations={**WRITE, "title": "Clone a Forms image"})
def clone(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    body: Annotated[ImageClone, Field(description="The image to copy and the clone's name.")],
    client: FormsClient = Depends(forms_client),
) -> Image:
    """Copy an existing image into a form; returns the new image with its integer ``id``.

    Reference the returned ``id`` from a question's, option's or form style's ``image``.
    """
    return client.images.clone(survey_id, body)
