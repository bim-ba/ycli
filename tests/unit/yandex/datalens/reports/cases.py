"""Contract cases for DataLens reports (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.reports.models import EntryAnnotation, ReportData, ReportMeta

REP = "rep00000000001"
WB = "wb000000000001"
DATA = {"slides": [{"id": "s1"}]}
CHANGE = {"slides": [{"id": "s1"}, {"id": "s2"}]}
META = {"title": "Q1"}
NOTE = {"description": "The quarter"}
# The document requires four fields with one value each: `scope`, an empty `type`, `version`
# and `public`; a live report (2026-10-06) comes under `entry` with these very values.
ENTRY = {
    "entryId": REP,
    "key": "Sales/Q1",
    "scope": "report",
    "type": "",
    "version": 2,
    "public": False,
    "workbookId": WB,
    "data": DATA,
    "revId": "rev1",
    "savedId": "rev1",
    "publishedId": "rev1",
}
SAVED = {**ENTRY, "data": CHANGE, "revId": "rev2", "savedId": "rev2"}

CASES = [
    Case(
        "datalens.reports.get",
        args=(REP,),
        cli=["datalens", "reports", "get", REP],
        mcp=("datalens_reports_get", {"entry_id": REP}),
        effect=Effect.READ,
        exchanges=[
            (Sent("POST", "rpc/getReport", json={"entryId": REP}), Reply(json={"entry": ENTRY}))
        ],
    ),
    Case(
        "datalens.reports.get",
        args=(REP,),
        kwargs={"rev_id": "rev1", "include_permissions": True, "include_favorite": False},
        cli=[
            *("datalens", "reports", "get", REP, "--rev-id", "rev1"),
            *("--include-permissions", "--no-include-favorite"),
        ],
        mcp=(
            "datalens_reports_get",
            {
                "entry_id": REP,
                "rev_id": "rev1",
                "include_permissions": True,
                "include_favorite": False,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getReport",
                    json={
                        "entryId": REP,
                        "revId": "rev1",
                        "includePermissions": True,
                        "includeFavorite": False,
                    },
                ),
                Reply(json={"entry": ENTRY, "isFavorite": False}),
            )
        ],
    ),
    Case(
        "datalens.reports.create",
        kwargs={
            "data": ReportData.model_validate(DATA),
            "meta": None,
            "workbook_id": WB,
            "name": "Q1",
        },
        cli=[
            *("datalens", "reports", "create", "--data", json.dumps(DATA), "--meta", "null"),
            *("--workbook-id", WB, "--name", "Q1"),
        ],
        mcp=(
            "datalens_reports_create",
            {"data": DATA, "meta": None, "workbook_id": WB, "name": "Q1"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createReport",
                    json={"data": DATA, "meta": None, "workbookId": WB, "name": "Q1"},
                ),
                Reply(json={"entry": ENTRY}),
            )
        ],
    ),
    Case(
        "datalens.reports.create",
        kwargs={
            "data": ReportData.model_validate(DATA),
            "meta": ReportMeta(META),
            "annotation": EntryAnnotation.model_validate(NOTE),
            "include_permissions": True,
            "key": "Sales/Q1",
        },
        cli=[
            *("datalens", "reports", "create", "--data", json.dumps(DATA)),
            *("--meta", json.dumps(META), "--annotation", json.dumps(NOTE)),
            *("--include-permissions", "--key", "Sales/Q1"),
        ],
        mcp=(
            "datalens_reports_create",
            {
                "data": DATA,
                "meta": META,
                "annotation": NOTE,
                "include_permissions": True,
                "key": "Sales/Q1",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createReport",
                    json={
                        "data": DATA,
                        "meta": META,
                        "annotation": NOTE,
                        "includePermissions": True,
                        "key": "Sales/Q1",
                    },
                ),
                Reply(json={"entry": ENTRY}),
            )
        ],
    ),
    Case(
        "datalens.reports.update",
        args=(REP,),
        kwargs={"data": ReportData.model_validate(CHANGE), "mode": "save", "meta": None},
        cli=[
            *("datalens", "reports", "update", REP, "--mode", "save"),
            *("--data", json.dumps(CHANGE), "--meta", "null"),
        ],
        mcp=(
            "datalens_reports_update",
            {"entry_id": REP, "data": CHANGE, "mode": "save", "meta": None},
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateReport",
                    json={"entryId": REP, "data": CHANGE, "mode": "save", "meta": None},
                ),
                Reply(json={"entry": SAVED}),
            )
        ],
    ),
    Case(
        "datalens.reports.update",
        args=(REP,),
        kwargs={
            "data": ReportData.model_validate(CHANGE),
            "mode": "publish",
            "meta": ReportMeta(META),
            "rev_id": "rev1",
            "annotation": EntryAnnotation.model_validate(NOTE),
        },
        cli=[
            *("datalens", "reports", "update", REP, "--mode", "publish"),
            *("--data", json.dumps(CHANGE), "--meta", json.dumps(META)),
            *("--rev-id", "rev1", "--annotation", json.dumps(NOTE)),
        ],
        mcp=(
            "datalens_reports_update",
            {
                "entry_id": REP,
                "data": CHANGE,
                "mode": "publish",
                "meta": META,
                "rev_id": "rev1",
                "annotation": NOTE,
            },
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateReport",
                    json={
                        "entryId": REP,
                        "data": CHANGE,
                        "mode": "publish",
                        "meta": META,
                        "revId": "rev1",
                        "annotation": NOTE,
                    },
                ),
                Reply(json={"entry": SAVED}),
            )
        ],
    ),
    Case(
        "datalens.reports.delete",
        args=(REP,),
        cli=["datalens", "reports", "delete", REP],
        mcp=("datalens_reports_delete", {"entry_id": REP}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[(Sent("POST", "rpc/deleteReport", json={"entryId": REP}), Reply(json={}))],
    ),
]
