"""DataLens Lakehouse operations FastMCP tool (read-only) — Depends DI, native errors."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.dependencies import RO, datalens_client
from ycli.yandex.datalens.models import LakehouseOperation

mcp = FastMCP("datalens-lakehouseoperations")


@mcp.tool(
    name="lakehouseoperations_get", annotations={**RO, "title": "Get DataLens Lakehouse operation"}
)
def get(
    operation_id: Annotated[
        str,
        Field(description="Operation id, from making a cloud environment or a REST catalog."),
    ],
    client: DataLensClient = Depends(datalens_client),
) -> LakehouseOperation:
    """How far an operation is: ``done`` or not, and then its ``error`` or its ``response``.

    Experimental in the DataLens API and written from its document: not measured. An id
    nothing knows answers 403 Permission denied, not 404: it is not a lack of rights.
    """
    return client.lakehouseoperations.get(operation_id)
