"""Contract cases for DataLens datasets (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.datasets.models import (
    DataFilter,
    DataParameter,
    DatasetContent,
    DatasetUpdate,
    DatasetValidate,
    DataSort,
)

DS = "ds000000000001"
WB = "wb000000000001"
# What an empty dataset holds, as a live `createDataset` took it (2026-10-06).
EMPTY = {
    "sources": [],
    "source_avatars": [],
    "avatar_relations": [],
    "result_schema": [],
    "obligatory_filters": [],
    "rls": {},
    "rls2": {},
}
# A source of a kind the document does not list (measured on a demo dataset), and a field.
CONTENT = {
    **EMPTY,
    "description": "Sales by city",
    "sources": [{"id": "src1", "source_type": "CH_FROZEN_SOURCE", "title": "sales"}],
    "result_schema": [{"guid": "guid-1", "title": "City", "calc_mode": "direct", "source": "city"}],
}
REVISIONS = {"publishedId": None, "revId": "rev1", "savedId": "rev1"}
# The top level of a live `getDataset` reply.
READ = {
    "id": DS,
    "name": "Sales",
    "key": "Sales/Sales",
    "workbook_id": WB,
    "is_favorite": False,
    "permissions": {"admin": True, "edit": True, "execute": True, "read": True},
    "full_permissions": {"admin": True, "edit": True, "execute": True, "read": True},
    "options": {"preview": {"enabled": True}},
    "dataset": CONTENT,
    **REVISIONS,
}
# `createDataset` answers the content, the id, the options and the revisions.
CREATED = {"id": DS, "dataset": EMPTY, "options": {}, **REVISIONS}
# `updateDataset` answers no id.
CHANGE = {"dataset": {**CONTENT, "description": "Q1"}, "mode": "save"}
SAVED = {"dataset": CHANGE["dataset"], "options": {}, **REVISIONS, "revId": "rev2"}
TRIED = {"dataset": CONTENT}
CHECKED = {"code": "OK", "message": "", "dataset_errors": [], **SAVED}
FILTER = {"guid": "guid-1", "operation": "eq", "values": ["Moscow"]}
PARAMETER = {"guid": "guid-9", "value": 2026}
SORT = {"guid": "guid-2", "direction": "desc"}
PAGE = {
    "schema": [
        {"name": "City", "guid": "guid-1", "type": "string"},
        {"name": "Orders", "guid": "guid-2", "type": "integer"},
    ],
    "rows": [["Moscow", 120], ["Kazan", 80]],
}

CASES = [
    Case(
        "datalens.datasets.get",
        args=(DS,),
        cli=["datalens", "datasets", "get", DS],
        mcp=("datalens_datasets_get", {"dataset_id": DS}),
        effect=Effect.READ,
        exchanges=[(Sent("POST", "rpc/getDataset", json={"datasetId": DS}), Reply(json=READ))],
    ),
    Case(
        "datalens.datasets.get",
        args=(DS,),
        kwargs={"workbook_id": WB, "rev_id": "rev1"},
        cli=["datalens", "datasets", "get", DS, "--workbook-id", WB, "--rev-id", "rev1"],
        mcp=("datalens_datasets_get", {"dataset_id": DS, "workbook_id": WB, "rev_id": "rev1"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getDataset",
                    json={"datasetId": DS, "workbookId": WB, "rev_id": "rev1"},
                ),
                Reply(json=READ),
            )
        ],
    ),
    Case(
        "datalens.datasets.create",
        args=(DatasetContent.model_validate(EMPTY),),
        kwargs={"name": "Sales", "workbook_id": WB},
        cli=[
            *("datalens", "datasets", "create", "--dataset", json.dumps(EMPTY)),
            *("--name", "Sales", "--workbook-id", WB),
        ],
        mcp=("datalens_datasets_create", {"dataset": EMPTY, "name": "Sales", "workbook_id": WB}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createDataset",
                    json={"dataset": EMPTY, "name": "Sales", "workbook_id": WB},
                ),
                Reply(json=CREATED),
            )
        ],
    ),
    Case(
        "datalens.datasets.create",
        args=(DatasetContent.model_validate(CONTENT),),
        kwargs={
            "collection_id": "col1",
            "created_via": "user",
            "dir_path": "Sales",
            "name": "Sales",
            "options": None,
            "preview": False,
            "published_id": "rev0",
            "rev_id": "rev1",
            "saved_id": "rev1",
        },
        cli=[
            *("datalens", "datasets", "create", "--dataset", json.dumps(CONTENT)),
            *("--collection-id", "col1", "--created-via", "user", "--dir-path", "Sales"),
            *("--name", "Sales", "--no-preview", "--published-id", "rev0"),
            *("--rev-id", "rev1", "--saved-id", "rev1"),
        ],
        mcp=(
            "datalens_datasets_create",
            {
                "dataset": CONTENT,
                "collection_id": "col1",
                "created_via": "user",
                "dir_path": "Sales",
                "name": "Sales",
                "preview": False,
                "published_id": "rev0",
                "rev_id": "rev1",
                "saved_id": "rev1",
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createDataset",
                    json={
                        "dataset": CONTENT,
                        "collection_id": "col1",
                        "created_via": "user",
                        "dir_path": "Sales",
                        "name": "Sales",
                        "preview": False,
                        "publishedId": "rev0",
                        "revId": "rev1",
                        "savedId": "rev1",
                    },
                ),
                Reply(json=CREATED),
            )
        ],
    ),
    Case(
        "datalens.datasets.update",
        args=(DS,),
        kwargs={"data": DatasetUpdate.model_validate(CHANGE), "workbook_id": WB},
        cli=[
            *("datalens", "datasets", "update", DS, "--data", json.dumps(CHANGE)),
            *("--workbook-id", WB),
        ],
        mcp=("datalens_datasets_update", {"dataset_id": DS, "data": CHANGE, "workbook_id": WB}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateDataset",
                    json={"datasetId": DS, "data": CHANGE, "workbookId": WB},
                ),
                Reply(json=SAVED),
            )
        ],
    ),
    Case(
        "datalens.datasets.delete",
        args=(DS,),
        cli=["datalens", "datasets", "delete", DS],
        mcp=("datalens_datasets_delete", {"dataset_id": DS}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent("POST", "rpc/deleteDataset", json={"datasetId": DS}),
                Reply(),  # measured: 200 with no body
            )
        ],
    ),
    Case(
        "datalens.datasets.validate",
        args=(DS,),
        kwargs={
            "workbook_id": WB,
            "binded_dataset_id": "ds000000000002",
            "data": DatasetValidate.model_validate(TRIED),
        },
        cli=[
            *("datalens", "datasets", "validate", DS, "--workbook-id", WB),
            *("--binded-dataset-id", "ds000000000002", "--data", json.dumps(TRIED)),
        ],
        mcp=(
            "datalens_datasets_validate",
            {
                "dataset_id": DS,
                "workbook_id": WB,
                "binded_dataset_id": "ds000000000002",
                "data": TRIED,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/validateDataset",
                    json={
                        "datasetId": DS,
                        "workbookId": WB,
                        "bindedDatasetId": "ds000000000002",
                        "data": TRIED,
                    },
                ),
                Reply(json=CHECKED),
            )
        ],
    ),
    Case(
        "datalens.datasets.data_get",
        args=(DS,),
        kwargs={"columns": ["guid-1", "guid-2"]},
        cli=[
            *("datalens", "datasets", "data-get", DS),
            *("--columns", "guid-1", "--columns", "guid-2"),
        ],
        mcp=("datalens_datasets_data_get", {"dataset_id": DS, "columns": ["guid-1", "guid-2"]}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getDatasetData",
                    json={"datasetId": DS, "columns": ["guid-1", "guid-2"]},
                ),
                Reply(json=PAGE),
            )
        ],
    ),
    Case(
        "datalens.datasets.data_get",
        args=(DS,),
        kwargs={
            "columns": ["guid-1"],
            "workbook_id": WB,
            "filters": [DataFilter.model_validate(FILTER)],
            "params": [DataParameter.model_validate(PARAMETER)],
            "sort": [DataSort.model_validate(SORT)],
            "limit": 50,
            "offset": 50,
        },
        cli=[
            *("datalens", "datasets", "data-get", DS, "--columns", "guid-1"),
            *("--workbook-id", WB, "--filters", json.dumps(FILTER)),
            *("--params", json.dumps(PARAMETER), "--sort", json.dumps(SORT)),
            *("--limit", "50", "--offset", "50"),
        ],
        mcp=(
            "datalens_datasets_data_get",
            {
                "dataset_id": DS,
                "columns": ["guid-1"],
                "workbook_id": WB,
                "filters": [FILTER],
                "params": [PARAMETER],
                "sort": [SORT],
                "limit": 50,
                "offset": 50,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getDatasetData",
                    json={
                        "datasetId": DS,
                        "workbookId": WB,
                        "columns": ["guid-1"],
                        "filters": [FILTER],
                        "params": [PARAMETER],
                        "sort": [SORT],
                        "limit": 50,
                        "offset": 50,
                    },
                ),
                Reply(json=PAGE),
            )
        ],
    ),
]
