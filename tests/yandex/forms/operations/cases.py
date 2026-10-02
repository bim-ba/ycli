"""Contract cases for Forms ``/operations`` (see tests/contract.py)."""

from tests.contract import Case, Reply, Sent

CASES = [
    Case(
        "forms.operations.get",
        args=("op-4a1b",),
        cli=["forms", "operations", "get", "op-4a1b"],
        mcp=("forms_operations_get", {"operation_id": "op-4a1b"}),
        exchanges=[
            (Sent("GET", "operations/op-4a1b"), Reply(json={"id": "op-4a1b", "status": "ok"}))
        ],
    ),
]
