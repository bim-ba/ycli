"""Forms files FastMCP tools (verify read + delete write, honest hints).

``upload`` (multipart raw bytes in) and ``download`` (raw bytes out) move binary payloads a
JSON MCP tool cannot carry, so they stay CLI/SDK-only; ``verify`` (a read done via POST) and
``delete`` are exposed here.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import DESTRUCTIVE, RO, TAGS, WRITE_TAGS, forms_client
from ycli.yandex.forms.files.models import FileIn, FileList
from ycli.yandex.models import Ack

mcp = FastMCP("forms-files")


@mcp.tool(name="files_verify", annotations={**RO, "title": "Verify Forms files"}, tags=TAGS)
def verify(
    survey_id: Annotated[str, Field(description="Form id (24-char hex) the files belong to.")],
    files: Annotated[
        list[FileIn],
        Field(description="File references to check — each a ``{path, url}`` from an upload."),
    ],
    client: FormsClient = Depends(forms_client),
) -> FileList:
    """Check the upload/scan status and download access of already-uploaded form-filling files.

    A read done via POST — nothing is mutated. Each returned item's ``check_status`` is one of
    ``check``, ``ready``, ``infected``, ``error``, ``deleted``. Uploading and downloading the
    files themselves are binary payloads — CLI/SDK-only.
    """
    return client.files.verify(survey_id, files)


@mcp.tool(
    name="files_delete", annotations={**DESTRUCTIVE, "title": "Delete Forms file"}, tags=WRITE_TAGS
)
def delete(
    path: Annotated[
        str | None, Field(description="File download path (from the upload response).")
    ] = None,
    url: Annotated[str | None, Field(description="File download URL.")] = None,
    client: FormsClient = Depends(forms_client),
) -> Ack:
    """Delete a stored form-filling file, identified by its ``path`` and/or ``url``.

    At least one of ``path`` / ``url`` must identify the file. The API answers ``200 OK`` with
    no useful body, so the returned record confirms the accepted action.
    """
    return client.files.delete(path=path, url=url)
