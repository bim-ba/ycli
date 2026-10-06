"""DataLens Lakehouse operation, declared once (sans-IO).

Examples:
    >>> get("op1").body
    {'operationId': 'op1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.models import LakehouseOperation
from ycli.yandex.datalens.schemas.lakehouse_operations import GetLakehouseOperationArgs


def get(operation_id: str) -> Endpoint[LakehouseOperation]:
    body = GetLakehouseOperationArgs(operationId=operation_id)
    return RPC("getLakehouseOperation", LakehouseOperation, json=body, effect=Effect.READ)
