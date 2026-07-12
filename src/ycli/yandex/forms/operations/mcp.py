"""Forms /operations FastMCP tool (reads-only) — poll an async operation to completion."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, forms_client
from ycli.yandex.forms.operations.models import OperationResult

mcp = FastMCP("forms-operations")


@mcp.tool(name="operations_get", annotations={**RO, "title": "Get Forms operation"}, tags=TAGS)
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

    >>> await client.call_tool("operations_get", {"operation_id": "op-4a1b"})  # doctest: +SKIP
    """
    result = client.operations.get(operation_id)
    # Forms models are fully lenient — a 404 / empty body deserializes into an all-None
    # OperationResult rather than raising; turn that into a clean not-found error.
    if result.id is None:
        raise ValueError(
            f"operation {operation_id!r} not found (empty response — check the id or permissions)"
        )
    return result
