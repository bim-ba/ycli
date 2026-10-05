"""Forms /operations FastMCP tool (reads-only) — poll an async operation to completion."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, forms_client
from ycli.yandex.forms.models import OperationResult

mcp = FastMCP("forms-operations")


@mcp.tool(name="operations_get", annotations={**RO, "title": "Get Forms operation"})
def get(
    operation_id: Annotated[
        str,
        Field(description="Operation id returned by an async trigger (e.g. an answers export)."),
    ],
    client: FormsClient = Depends(forms_client),
) -> OperationResult:
    """The status of a long-running Forms operation — poll this to watch an async export finish.

    Returns ``{id, status, message}`` where ``status`` is one of ``ok`` (finished, result
    ready), ``fail``, ``wait`` (still running) or ``not_running``. Take the ``operation_id``
    from the ``id`` an async trigger returned (e.g. the ``answers_export`` tool or
    ``ycli forms answers export … --no-wait``); re-call until ``status`` is ``ok`` or ``fail``.
    """
    return client.operations.get(operation_id)
