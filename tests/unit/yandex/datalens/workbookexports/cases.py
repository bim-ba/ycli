"""Contract cases for DataLens workbook exports (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

# The keys of the live replies (2026-10-06), for a workbook holding one empty dataset.
EXPORTED = {
    "exportId": "exp0000000001",
    "status": "success",
    "data": {
        "export": {"version": "1", "entries": {"dataset": {"0": {"dataset": {"name": "Sales"}}}}},
        "hash": "9f2c1e",
    },
}

CASES = [
    Case(
        "datalens.workbookexports.start",
        args=("wb000000000001",),
        cli=["datalens", "workbookexports", "start", "wb000000000001", "--no-wait"],
        mcp=("datalens_workbookexports_start", {"workbook_id": "wb000000000001"}),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/startWorkbookExport", json={"workbookId": "wb000000000001"}),
                Reply(json={"exportId": "exp0000000001"}),
            )
        ],
    ),
    Case(
        "datalens.workbookexports.status_get",
        args=("exp0000000001",),
        cli=["datalens", "workbookexports", "status-get", "exp0000000001"],
        mcp=("datalens_workbookexports_status_get", {"export_id": "exp0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getWorkbookExportStatus", json={"exportId": "exp0000000001"}),
                Reply(
                    json={
                        "exportId": "exp0000000001",
                        "status": "success",
                        "progress": 100,
                        "notifications": [],
                    }
                ),
            )
        ],
    ),
    # Still running, with a notification about an entry (its keys are the document's).
    Case(
        "datalens.workbookexports.status_get",
        args=("exp0000000003",),
        cli=["datalens", "workbookexports", "status-get", "exp0000000003"],
        mcp=("datalens_workbookexports_status_get", {"export_id": "exp0000000003"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getWorkbookExportStatus", json={"exportId": "exp0000000003"}),
                Reply(
                    json={
                        "exportId": "exp0000000003",
                        "status": "pending",
                        "progress": 40,
                        "notifications": [
                            {
                                "entryId": "ent0000000001",
                                "scope": "connection",
                                "code": "NOTIFICATION_CODE",
                                "message": "A text for a person",
                                "level": "warning",
                            }
                        ],
                    }
                ),
            )
        ],
    ),
    Case(
        "datalens.workbookexports.result_get",
        args=("exp0000000001",),
        cli=["datalens", "workbookexports", "result-get", "exp0000000001"],
        mcp=("datalens_workbookexports_result_get", {"export_id": "exp0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getWorkbookExportResult", json={"exportId": "exp0000000001"}),
                Reply(json=EXPORTED),
            )
        ],
    ),
    Case(
        "datalens.workbookexports.cancel",
        args=("exp0000000002",),
        cli=["datalens", "workbookexports", "cancel", "exp0000000002"],
        mcp=("datalens_workbookexports_cancel", {"export_id": "exp0000000002"}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/cancelWorkbookExport", json={"exportId": "exp0000000002"}),
                Reply(json={"exportId": "exp0000000002"}),
            )
        ],
    ),
]
