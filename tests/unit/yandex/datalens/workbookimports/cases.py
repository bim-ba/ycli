"""Contract cases for DataLens workbook imports (see tests/contract/)."""

import json
from pathlib import Path

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

EXPORTED = {"export": {"version": "1", "entries": {}}, "hash": "h1"}
FROM_FILE = str(Path(__file__).parent / "export.json")
IN_THE_FILE = json.loads(Path(FROM_FILE).read_text(encoding="utf-8"))["data"]

CASES = [
    Case(
        "datalens.workbookimports.start",
        args=(EXPORTED,),
        kwargs={"title": "Sales, copy", "collection_id": "col0000000001"},
        cli=[
            *("datalens", "workbookimports", "start", "--data", json.dumps(EXPORTED)),
            *("--title", "Sales, copy", "--collection-id", "col0000000001", "--no-wait"),
        ],
        mcp=(
            "datalens_workbookimports_start",
            {"data": EXPORTED, "title": "Sales, copy", "collection_id": "col0000000001"},
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/startWorkbookImport",
                    json={
                        "data": EXPORTED,
                        "title": "Sales, copy",
                        "collectionId": "col0000000001",
                    },
                ),
                Reply(json={"importId": "imp0000000001", "workbookId": "wb000000000002"}),
            )
        ],
    ),
    # The document from a file, into the root: no collection is an explicit null.
    Case(
        "datalens.workbookimports.start",
        args=(IN_THE_FILE,),
        kwargs={"title": "Stock", "description": "From the file"},
        cli=[
            *("--body-file", FROM_FILE, "datalens", "workbookimports", "start"),
            *("--title", "Stock", "--description", "From the file", "--no-wait"),
        ],
        mcp=(
            "datalens_workbookimports_start",
            {"data": IN_THE_FILE, "title": "Stock", "description": "From the file"},
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/startWorkbookImport",
                    json={
                        "data": IN_THE_FILE,
                        "title": "Stock",
                        "description": "From the file",
                        "collectionId": None,
                    },
                ),
                Reply(json={"importId": "imp0000000003", "workbookId": "wb000000000004"}),
            )
        ],
    ),
    Case(
        "datalens.workbookimports.status_get",
        args=("imp0000000001",),
        cli=["datalens", "workbookimports", "status-get", "imp0000000001"],
        mcp=("datalens_workbookimports_status_get", {"import_id": "imp0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getWorkbookImportStatus", json={"importId": "imp0000000001"}),
                # Measured: a finished import sends no `notifications` key at all.
                Reply(
                    json={
                        "importId": "imp0000000001",
                        "workbookId": "wb000000000002",
                        "status": "success",
                        "progress": 100,
                    }
                ),
            )
        ],
    ),
]
