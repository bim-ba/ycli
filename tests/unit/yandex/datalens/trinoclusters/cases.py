"""Contract cases for DataLens Trino clusters (see tests/contract/).

Only the listing of an instance with no cluster was measured (2026-10-06); a cluster or a
preset in a reply, and every write, are written from the document.
"""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.trinoclusters.models import (
    TrinoCatalogToAdd,
    TrinoNewCatalog,
    TrinoWorkerConfig,
)

STAMP = {"seconds": "1790000000", "nanos": 0}
WORKERS = {"resources": {"resourcePresetId": "c4-m16"}}
SCALED = {
    "resources": {"resourcePresetId": "c8-m32"},
    "scalePolicy": {"autoScale": {"minCount": "1", "maxCount": "4"}},
}
CLUSTER = {
    "id": "tc00000000001",
    "clusterId": "c9q0000000001",
    "collectionId": "col0000000001",
    "cloudEnvironmentId": "env0000000001",
    "name": "reports",
    "description": "",
    "labels": {},
    "config": {
        "trinoVersion": "468",
        "catalogsConfig": [{"catalogId": "cat0000000001"}],
        "coordinatorConfig": {"resources": {"resourcePresetId": "c4-m16"}},
        "workerConfig": {
            "resources": {"resourcePresetId": "c4-m16"},
            "scalePolicy": {
                "scaleType": "autoScale",
                "autoScale": {"minCount": "1", "maxCount": "4"},
            },
        },
    },
    "health": "ALIVE",
    "status": "RUNNING",
    "coordinatorUrl": "https://trino.example.net",
    "entryId": "ent0000000009",
}
PRESET = {"id": "c4-m16", "cores": "4", "memory": "17179869184"}


def _operation(number: int, description: str) -> dict:
    return {
        "id": f"op00000000000{number}",
        "description": description,
        "createdAt": STAMP,
        "createdBy": "user-1",
        "modifiedAt": STAMP,
        "done": False,
        "metadata": {},
    }


def _write(method: str, rpc: str, number: int, text: str, effect: Effect) -> Case:
    """A write that takes the cluster alone."""
    key = "id" if method == "delete" else "clusterId"
    argument = "id" if method == "delete" else "cluster_id"
    return Case(
        f"datalens.trinoclusters.{method}",
        args=("tc00000000001",),
        cli=["datalens", "trinoclusters", method, "tc00000000001"],
        mcp=(f"datalens_trinoclusters_{method}", {argument: "tc00000000001"}),
        effect=effect,
        exchanges=[
            (
                Sent("POST", f"rpc/{rpc}", json={key: "tc00000000001"}),
                Reply(json=_operation(number, text)),
            )
        ],
    )


CASES = [
    Case(
        "datalens.trinoclusters.list",
        kwargs={"collection_id": "col0000000001"},
        cli=["datalens", "trinoclusters", "list", "--collection-id", "col0000000001"],
        mcp=("datalens_trinoclusters_list", {"collection_id": "col0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listTrinoClusters", json={"collectionId": "col0000000001"}),
                Reply(json={"clusters": [CLUSTER], "nextPageToken": ""}),
            )
        ],
    ),
    # Measured: an instance with no cluster answers an empty list and an empty token.
    Case(
        "datalens.trinoclusters.list",
        kwargs={"filter": ['name="reports"'], "catalog_id": "cat0000000001", "limit": 6},
        cli=[
            *("datalens", "trinoclusters", "list", "--filter", 'name="reports"'),
            *("--catalog-id", "cat0000000001", "--limit", "6"),
        ],
        mcp=(
            "datalens_trinoclusters_list",
            {"filter": ['name="reports"'], "catalog_id": "cat0000000001", "limit": 6},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listTrinoClusters",
                    json={"filter": ['name="reports"'], "catalogId": "cat0000000001"},
                ),
                Reply(json={"clusters": [], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.trinoclusters.get",
        args=("tc00000000001",),
        cli=["datalens", "trinoclusters", "get", "tc00000000001"],
        mcp=("datalens_trinoclusters_get", {"id": "tc00000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getTrinoCluster", json={"id": "tc00000000001"}),
                Reply(json=CLUSTER),
            )
        ],
    ),
    Case(
        "datalens.trinoclusters.create",
        kwargs={
            "collection_id": "col0000000001",
            "cloud_environment_id": "env0000000001",
            "name": "reports",
            "worker_config": TrinoWorkerConfig.model_validate(WORKERS),
        },
        cli=[
            *("datalens", "trinoclusters", "create", "--collection-id", "col0000000001"),
            *("--cloud-environment-id", "env0000000001", "--name", "reports"),
            *("--worker-config", json.dumps(WORKERS)),
        ],
        mcp=(
            "datalens_trinoclusters_create",
            {
                "collection_id": "col0000000001",
                "cloud_environment_id": "env0000000001",
                "name": "reports",
                "worker_config": WORKERS,
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createTrinoCluster",
                    json={
                        "collectionId": "col0000000001",
                        "cloudEnvironmentId": "env0000000001",
                        "name": "reports",
                        "workerConfig": WORKERS,
                    },
                ),
                Reply(json=_operation(11, "Create Trino cluster")),
            )
        ],
    ),
    Case(
        "datalens.trinoclusters.create",
        kwargs={
            "collection_id": "col0000000002",
            "cloud_environment_id": "env0000000002",
            "name": "adhoc",
            "worker_config": TrinoWorkerConfig.model_validate(SCALED),
            "description": "For analysts",
            "labels": {"team": "analytics"},
            "catalogs_config": [TrinoNewCatalog.model_validate({"catalogId": "cat0000000002"})],
            "trino_version": "468",
        },
        cli=[
            *("datalens", "trinoclusters", "create", "--collection-id", "col0000000002"),
            *("--cloud-environment-id", "env0000000002", "--name", "adhoc"),
            *("--worker-config", json.dumps(SCALED), "--description", "For analysts"),
            *("--labels", json.dumps({"team": "analytics"})),
            *("--catalogs-config", json.dumps({"catalogId": "cat0000000002"})),
            *("--trino-version", "468"),
        ],
        mcp=(
            "datalens_trinoclusters_create",
            {
                "collection_id": "col0000000002",
                "cloud_environment_id": "env0000000002",
                "name": "adhoc",
                "worker_config": SCALED,
                "description": "For analysts",
                "labels": {"team": "analytics"},
                "catalogs_config": [{"catalogId": "cat0000000002"}],
                "trino_version": "468",
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createTrinoCluster",
                    json={
                        "collectionId": "col0000000002",
                        "cloudEnvironmentId": "env0000000002",
                        "name": "adhoc",
                        "workerConfig": SCALED,
                        "description": "For analysts",
                        "labels": {"team": "analytics"},
                        "catalogsConfig": [{"catalogId": "cat0000000002"}],
                        "trinoVersion": "468",
                    },
                ),
                Reply(json=_operation(17, "Create Trino cluster")),
            )
        ],
    ),
    _write("delete", "deleteTrinoCluster", 12, "Delete Trino cluster", Effect.DESTRUCTIVE),
    _write("start", "startTrinoCluster", 13, "Start Trino cluster", Effect.WRITE),
    _write("stop", "stopTrinoCluster", 14, "Stop Trino cluster", Effect.WRITE),
    Case(
        "datalens.trinoclusters.catalog_create",
        args=("tc00000000001",),
        kwargs={"catalog": TrinoCatalogToAdd.model_validate({"catalogId": "cat0000000001"})},
        cli=[
            *("datalens", "trinoclusters", "catalog-create", "tc00000000001"),
            *("--catalog", json.dumps({"catalogId": "cat0000000001"})),
        ],
        mcp=(
            "datalens_trinoclusters_catalog_create",
            {"cluster_id": "tc00000000001", "catalog": {"catalogId": "cat0000000001"}},
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/addTrinoClusterCatalog",
                    json={"clusterId": "tc00000000001", "catalog": {"catalogId": "cat0000000001"}},
                ),
                Reply(json=_operation(15, "Add catalog")),
            )
        ],
    ),
    Case(
        "datalens.trinoclusters.catalog_delete",
        args=("tc00000000001",),
        kwargs={"catalog_id": "cat0000000001"},
        cli=[
            *("datalens", "trinoclusters", "catalog-delete", "tc00000000001"),
            *("--catalog-id", "cat0000000001"),
        ],
        mcp=(
            "datalens_trinoclusters_catalog_delete",
            {"cluster_id": "tc00000000001", "catalog_id": "cat0000000001"},
        ),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/deleteTrinoClusterCatalog",
                    json={"clusterId": "tc00000000001", "catalogId": "cat0000000001"},
                ),
                Reply(json=_operation(16, "Delete catalog")),
            )
        ],
    ),
    Case(
        "datalens.trinoclusters.resource_presets_list",
        args=("env0000000001",),
        cli=["datalens", "trinoclusters", "resource-presets-list", "env0000000001"],
        mcp=(
            "datalens_trinoclusters_resource_presets_list",
            {"cloud_environment_id": "env0000000001"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listTrinoResourcePresets",
                    json={"cloudEnvironmentId": "env0000000001"},
                ),
                Reply(json={"resourcePresets": [PRESET], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.trinoclusters.resource_preset_get",
        args=("c4-m16",),
        kwargs={"cloud_environment_id": "env0000000001"},
        cli=[
            *("datalens", "trinoclusters", "resource-preset-get", "c4-m16"),
            *("--cloud-environment-id", "env0000000001"),
        ],
        mcp=(
            "datalens_trinoclusters_resource_preset_get",
            {"resource_preset_id": "c4-m16", "cloud_environment_id": "env0000000001"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getTrinoResourcePreset",
                    json={"resourcePresetId": "c4-m16", "cloudEnvironmentId": "env0000000001"},
                ),
                Reply(json=PRESET),
            )
        ],
    ),
]
