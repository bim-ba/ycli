"""Contract cases for DataLens charts (see tests/contract/)."""

import json

from pydantic import TypeAdapter

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.charts.models import (
    EditorChartCreate,
    EditorChartUpdate,
    EntryAnnotation,
    QLChartChange,
    QLChartData,
    WizardChartData,
)

CHART = "ch000000000001"
PARAMS = {"year": "2026", "city": ["Moscow", "Kazan"]}
TABLES = {
    "chartType": "wizard",
    "results": [
        {
            "schema": [
                {"name": "City", "guid": "guid-1", "type": "string"},
                {"name": "Orders", "guid": "guid-2", "type": "integer"},
            ],
            "rows": [["Moscow", 120]],
        }
    ],
}

WB = "wb000000000001"
# What a chart of the wizard holds, with the keys of a live flat table (2026-10-06).
WIZARD = {
    "sources": {"datasetsIds": ["ds000000000001"]},
    "visualization": {"type": "flatTable", "columns": {"items": [{"guid": "guid-1"}]}},
}
NOTE = {"description": "Top products"}
REVISIONS = {"revId": "rev1", "savedId": "rev1", "publishedId": "rev1"}
WIZARD_ENTRY = {
    "version": 1,
    "entryId": CHART,
    "key": "Sales/Top",
    "scope": "widget",
    "type": "table_wizard_node",
    "workbookId": WB,
    "data": WIZARD,
    **REVISIONS,
}
# A save moves `revId` and `savedId`; `publishedId` stays (measured).
SAVED = {**WIZARD_ENTRY, "revId": "rev2", "savedId": "rev2"}
GET = {
    "workbookId": WB,
    "revId": "rev1",
    "includePermissions": True,
    "includeLinks": False,
    "includeFavorite": True,
    "branch": "published",
}
GET_KWARGS = {
    "workbook_id": WB,
    "rev_id": "rev1",
    "include_permissions": True,
    "include_links": False,
    "include_favorite": True,
    "branch": "published",
}
GET_FLAGS = [
    *("--workbook-id", WB, "--rev-id", "rev1", "--include-permissions"),
    *("--no-include-links", "--include-favorite", "--branch", "published"),
]
# A QL chart comes flat (the keys of a live `getQLChart`, 2026-10-06); what `create` and
# `update` answer, and every Editor reply, is not measured and follows the document.
QL_CHART = {
    "entryId": CHART,
    "key": "Sales/Top",
    "scope": "widget",
    "type": "table_ql_node",
    "version": None,
    "sourceVersion": None,
    "annotation": None,
    "collectionId": None,
    "workbookId": WB,
    "hidden": False,
    "public": False,
    "data": {"queryValue": "select 1"},
    **REVISIONS,
}
QL_ENTRY = {"entry": {"entryId": CHART, "scope": "widget", "type": "table_ql_node"}}
QL_DATA = {"queryValue": "select 1"}
QL_CHANGE = {"queryValue": "select 2"}
EDITOR_NEW = {"type": "table_node", "workbookId": WB, "name": "Top"}
EDITOR_CHANGE = {"type": "table_node", "entryId": CHART}
EDITOR_ENTRY = {"entry": {"entryId": CHART, "type": "table_node", "scope": "widget"}}


def _get(kind: str, rpc: str, reply: dict) -> list[Case]:
    """Reading a chart of one kind: by id alone, and with every argument."""
    return [
        Case(
            f"datalens.charts.{kind}_get",
            args=(CHART,),
            cli=["datalens", "charts", kind, "get", CHART],
            mcp=(f"datalens_charts_{kind}_get", {"chart_id": CHART}),
            effect=Effect.READ,
            exchanges=[(Sent("POST", f"rpc/{rpc}", json={"chartId": CHART}), Reply(json=reply))],
        ),
        Case(
            f"datalens.charts.{kind}_get",
            args=(CHART,),
            kwargs=GET_KWARGS,
            cli=["datalens", "charts", kind, "get", CHART, *GET_FLAGS],
            mcp=(f"datalens_charts_{kind}_get", {"chart_id": CHART, **GET_KWARGS}),
            effect=Effect.READ,
            exchanges=[
                (Sent("POST", f"rpc/{rpc}", json={"chartId": CHART, **GET}), Reply(json=reply))
            ],
        ),
    ]


def _delete(kind: str, rpc: str) -> Case:
    return Case(
        f"datalens.charts.{kind}_delete",
        args=(CHART,),
        cli=["datalens", "charts", kind, "delete", CHART],
        mcp=(f"datalens_charts_{kind}_delete", {"chart_id": CHART}),
        effect=Effect.DESTRUCTIVE,
        # Measured for the wizard: 200 with `{}`.
        exchanges=[(Sent("POST", f"rpc/{rpc}", json={"chartId": CHART}), Reply(json={}))],
    )


CASES = [
    Case(
        "datalens.charts.data_get",
        args=(CHART,),
        cli=["datalens", "charts", "data-get", CHART],
        mcp=("datalens_charts_data_get", {"chart_id": CHART}),
        effect=Effect.READ,
        exchanges=[(Sent("POST", "rpc/getChartData", json={"chartId": CHART}), Reply(json=TABLES))],
    ),
    Case(
        "datalens.charts.data_get",
        args=(CHART,),
        kwargs={"params": PARAMS},
        cli=["datalens", "charts", "data-get", CHART, "--params", json.dumps(PARAMS)],
        mcp=("datalens_charts_data_get", {"chart_id": CHART, "params": PARAMS}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getChartData", json={"chartId": CHART, "params": PARAMS}),
                Reply(json=TABLES),
            )
        ],
    ),
    *_get("wizard", "getWizardChart", {"entry": WIZARD_ENTRY}),
    Case(
        "datalens.charts.wizard_create",
        args=(WizardChartData.model_validate(WIZARD),),
        kwargs={"workbook_id": WB, "name": "Sales"},
        cli=[
            *("datalens", "charts", "wizard", "create", "--data", json.dumps(WIZARD)),
            *("--workbook-id", WB, "--name", "Sales"),
        ],
        mcp=("datalens_charts_wizard_create", {"data": WIZARD, "workbook_id": WB, "name": "Sales"}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createWizardChart",
                    json={"data": WIZARD, "workbookId": WB, "name": "Sales"},
                ),
                Reply(json={"entry": WIZARD_ENTRY}),
            )
        ],
    ),
    Case(
        "datalens.charts.wizard_create",
        args=(WizardChartData.model_validate(WIZARD),),
        kwargs={"annotation": EntryAnnotation.model_validate(NOTE), "key": "Sales/Top"},
        cli=[
            *("datalens", "charts", "wizard", "create", "--data", json.dumps(WIZARD)),
            *("--annotation", json.dumps(NOTE), "--key", "Sales/Top"),
        ],
        mcp=(
            "datalens_charts_wizard_create",
            {"data": WIZARD, "annotation": NOTE, "key": "Sales/Top"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createWizardChart",
                    json={"data": WIZARD, "annotation": NOTE, "key": "Sales/Top"},
                ),
                Reply(json={"entry": WIZARD_ENTRY}),
            )
        ],
    ),
    Case(
        "datalens.charts.wizard_update",
        args=(CHART,),
        kwargs={"mode": "save", "data": WizardChartData.model_validate(WIZARD)},
        cli=[
            *("datalens", "charts", "wizard", "update", CHART, "--mode", "save"),
            *("--data", json.dumps(WIZARD)),
        ],
        mcp=("datalens_charts_wizard_update", {"chart_id": CHART, "mode": "save", "data": WIZARD}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateWizardChart",
                    json={"chartId": CHART, "mode": "save", "data": WIZARD},
                ),
                Reply(json={"entry": SAVED}),
            )
        ],
    ),
    Case(
        "datalens.charts.wizard_update",
        args=(CHART,),
        kwargs={
            "mode": "publish",
            "data": WizardChartData.model_validate(WIZARD),
            "annotation": EntryAnnotation.model_validate(NOTE),
            "rev_id": "rev1",
        },
        cli=[
            *("datalens", "charts", "wizard", "update", CHART, "--mode", "publish"),
            *("--data", json.dumps(WIZARD), "--annotation", json.dumps(NOTE)),
            *("--rev-id", "rev1"),
        ],
        mcp=(
            "datalens_charts_wizard_update",
            {
                "chart_id": CHART,
                "mode": "publish",
                "data": WIZARD,
                "annotation": NOTE,
                "rev_id": "rev1",
            },
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateWizardChart",
                    json={
                        "chartId": CHART,
                        "mode": "publish",
                        "data": WIZARD,
                        "annotation": NOTE,
                        "revId": "rev1",
                    },
                ),
                Reply(json={"entry": SAVED}),
            )
        ],
    ),
    _delete("wizard", "deleteWizardChart"),
    *_get("ql", "getQLChart", QL_CHART),
    Case(
        "datalens.charts.ql_create",
        kwargs={
            "template": "ql",
            "data": QLChartData(QL_DATA),
            "workbook_id": WB,
            "name": "Top",
        },
        cli=[
            *("datalens", "charts", "ql", "create", "--template", "ql"),
            *("--data", json.dumps(QL_DATA), "--workbook-id", WB, "--name", "Top"),
        ],
        mcp=(
            "datalens_charts_ql_create",
            {"template": "ql", "data": QL_DATA, "workbook_id": WB, "name": "Top"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createQLChart",
                    json={"template": "ql", "data": QL_DATA, "workbookId": WB, "name": "Top"},
                ),
                Reply(json=QL_ENTRY),
            )
        ],
    ),
    Case(
        "datalens.charts.ql_create",
        kwargs={
            "template": "ql",
            "data": QLChartData(QL_DATA),
            "annotation": EntryAnnotation.model_validate(NOTE),
            "key": "Sales/Top",
        },
        cli=[
            *("datalens", "charts", "ql", "create", "--template", "ql"),
            *("--data", json.dumps(QL_DATA), "--annotation", json.dumps(NOTE)),
            *("--key", "Sales/Top"),
        ],
        mcp=(
            "datalens_charts_ql_create",
            {"template": "ql", "data": QL_DATA, "annotation": NOTE, "key": "Sales/Top"},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createQLChart",
                    json={
                        "template": "ql",
                        "data": QL_DATA,
                        "annotation": NOTE,
                        "key": "Sales/Top",
                    },
                ),
                Reply(json=QL_ENTRY),
            )
        ],
    ),
    Case(
        "datalens.charts.ql_update",
        args=(CHART,),
        kwargs={
            "template": "ql",
            "mode": "save",
            "data": QLChartChange(QL_CHANGE),
            "annotation": EntryAnnotation.model_validate(NOTE),
        },
        cli=[
            *("datalens", "charts", "ql", "update", CHART, "--template", "ql", "--mode", "save"),
            *("--data", json.dumps(QL_CHANGE), "--annotation", json.dumps(NOTE)),
        ],
        mcp=(
            "datalens_charts_ql_update",
            {
                "entry_id": CHART,
                "template": "ql",
                "mode": "save",
                "data": QL_CHANGE,
                "annotation": NOTE,
            },
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateQLChart",
                    json={
                        "entryId": CHART,
                        "template": "ql",
                        "mode": "save",
                        "data": QL_CHANGE,
                        "annotation": NOTE,
                    },
                ),
                Reply(json=QL_ENTRY),
            )
        ],
    ),
    _delete("ql", "deleteQLChart"),
    *_get("editor", "getEditorChart", EDITOR_ENTRY),
    Case(
        "datalens.charts.editor_create",
        args=(TypeAdapter(EditorChartCreate).validate_python(EDITOR_NEW),),
        cli=["datalens", "charts", "editor", "create", "--entry", json.dumps(EDITOR_NEW)],
        mcp=("datalens_charts_editor_create", {"entry": EDITOR_NEW}),
        exchanges=[
            (
                Sent("POST", "rpc/createEditorChart", json={"entry": EDITOR_NEW}),
                Reply(json=EDITOR_ENTRY),
            )
        ],
    ),
    Case(
        "datalens.charts.editor_update",
        args=(TypeAdapter(EditorChartUpdate).validate_python(EDITOR_CHANGE),),
        kwargs={"mode": "save"},
        cli=[
            *("datalens", "charts", "editor", "update", "--mode", "save"),
            *("--entry", json.dumps(EDITOR_CHANGE)),
        ],
        mcp=("datalens_charts_editor_update", {"entry": EDITOR_CHANGE, "mode": "save"}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateEditorChart",
                    json={"entry": EDITOR_CHANGE, "mode": "save"},
                ),
                Reply(json=EDITOR_ENTRY),
            )
        ],
    ),
    _delete("editor", "deleteEditorChart"),
]
