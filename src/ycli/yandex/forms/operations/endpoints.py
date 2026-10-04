"""Forms ``/operations``, declared once (sans-IO).

Examples:
    >>> get("op-1").path
    'operations/op-1'
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, segment
from ycli.yandex.forms.models import OperationResult


def get(operation_id: str) -> Endpoint[OperationResult]:
    return Endpoint("GET", f"operations/{segment(operation_id)}", OperationResult)
