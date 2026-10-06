"""Contract cases for DataLens Lakehouse operations (see tests/contract/).

Written from the document: no operation exists to read in the owner's instance.
"""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

STAMP = {"seconds": "1790000000", "nanos": 0}
DONE = {
    "id": "op0000000000001",
    "description": "Create cloud environment",
    "createdAt": STAMP,
    "createdBy": "user-1",
    "modifiedAt": STAMP,
    "done": True,
    "metadata": {"cloudEnvironmentId": "env0000000001"},
    "response": {"id": "env0000000001"},
}

CASES = [
    Case(
        "datalens.lakehouseoperations.get",
        args=("op0000000000001",),
        cli=["datalens", "lakehouseoperations", "get", "op0000000000001"],
        mcp=("datalens_lakehouseoperations_get", {"operation_id": "op0000000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getLakehouseOperation", json={"operationId": "op0000000000001"}),
                Reply(json=DONE),
            )
        ],
    ),
    # An operation that failed carries its error in place of a response.
    Case(
        "datalens.lakehouseoperations.get",
        args=("op0000000000008",),
        cli=["datalens", "lakehouseoperations", "get", "op0000000000008"],
        mcp=("datalens_lakehouseoperations_get", {"operation_id": "op0000000000008"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getLakehouseOperation", json={"operationId": "op0000000000008"}),
                Reply(
                    json={
                        **{key: value for key, value in DONE.items() if key != "response"},
                        "id": "op0000000000008",
                        "error": {"code": 9, "message": "The subnet is not found", "details": []},
                    }
                ),
            )
        ],
    ),
]
