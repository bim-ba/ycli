"""Contract cases for DataLens Spark clusters (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.sparkclusters.models import NewClusterConfig

SC = "sc000000000001"
COL = "col00000000001"
ENV = "env00000000001"
CONFIG = {"sparkVersion": "3.5"}
LABELS = {"team": "bi"}
# No reply here is measured (#455): the API is experimental and a cluster is paid for, so
# these follow the document.
CLUSTER = {
    "id": SC,
    "clusterId": "managed-1",
    "collectionId": COL,
    "cloudEnvironmentId": ENV,
    "name": "etl",
    "config": CONFIG,
    "health": "ALIVE",
    "status": "RUNNING",
}
OPERATION = {"id": "op000000000001", "description": "Spark cluster", "done": False}
PRESET = {"id": "c2-m8", "cores": "2", "memory": "8589934592"}


def _write(name: str, rpc: str, key: str, effect: Effect) -> Case:
    argument = "id" if key == "id" else "cluster_id"
    return Case(
        f"datalens.sparkclusters.{name}",
        args=(SC,),
        cli=["datalens", "sparkclusters", name, SC],
        mcp=(f"datalens_sparkclusters_{name}", {argument: SC}),
        effect=effect,
        exchanges=[(Sent("POST", f"rpc/{rpc}", json={key: SC}), Reply(json=OPERATION))],
    )


CASES = [
    Case(
        "datalens.sparkclusters.list",
        kwargs={"limit": 45},
        cli=["datalens", "sparkclusters", "list", "--limit", "45"],
        mcp=("datalens_sparkclusters_list", {"limit": 45}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listSparkClusters", json={}),
                Reply(json={"sparkClusters": [CLUSTER], "nextPageToken": "t2"}),
            ),
            (
                Sent("POST", "rpc/listSparkClusters", json={"pageToken": "t2"}),
                Reply(json={"sparkClusters": [{**CLUSTER, "id": "sc2", "name": "adhoc"}]}),
            ),
        ],
    ),
    Case(
        "datalens.sparkclusters.list",
        kwargs={"limit": 45, "collection_id": COL, "filter": ["name:etl"]},
        cli=[
            *("datalens", "sparkclusters", "list", "--limit", "45"),
            *("--collection-id", COL, "--filter", "name:etl"),
        ],
        mcp=(
            "datalens_sparkclusters_list",
            {"limit": 45, "collection_id": COL, "filter": ["name:etl"]},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listSparkClusters",
                    json={"collectionId": COL, "filter": ["name:etl"]},
                ),
                Reply(json={"sparkClusters": []}),
            )
        ],
    ),
    Case(
        "datalens.sparkclusters.get",
        args=(SC,),
        cli=["datalens", "sparkclusters", "get", SC],
        mcp=("datalens_sparkclusters_get", {"id": SC}),
        effect=Effect.READ,
        exchanges=[(Sent("POST", "rpc/getSparkCluster", json={"id": SC}), Reply(json=CLUSTER))],
    ),
    Case(
        "datalens.sparkclusters.create",
        kwargs={
            "collection_id": COL,
            "cloud_environment_id": ENV,
            "name": "etl",
            "config": NewClusterConfig.model_validate(CONFIG),
        },
        cli=[
            *("datalens", "sparkclusters", "create", "--collection-id", COL),
            *("--cloud-environment-id", ENV, "--name", "etl", "--config", json.dumps(CONFIG)),
        ],
        mcp=(
            "datalens_sparkclusters_create",
            {"collection_id": COL, "cloud_environment_id": ENV, "name": "etl", "config": CONFIG},
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createSparkCluster",
                    json={
                        "collectionId": COL,
                        "cloudEnvironmentId": ENV,
                        "name": "etl",
                        "config": CONFIG,
                    },
                ),
                Reply(json=OPERATION),
            )
        ],
    ),
    Case(
        "datalens.sparkclusters.create",
        kwargs={
            "collection_id": COL,
            "cloud_environment_id": ENV,
            "name": "etl",
            "config": NewClusterConfig.model_validate(CONFIG),
            "description": "Nightly loads",
            "labels": LABELS,
        },
        cli=[
            *("datalens", "sparkclusters", "create", "--collection-id", COL),
            *("--cloud-environment-id", ENV, "--name", "etl", "--config", json.dumps(CONFIG)),
            *("--description", "Nightly loads", "--labels", json.dumps(LABELS)),
        ],
        mcp=(
            "datalens_sparkclusters_create",
            {
                "collection_id": COL,
                "cloud_environment_id": ENV,
                "name": "etl",
                "config": CONFIG,
                "description": "Nightly loads",
                "labels": LABELS,
            },
        ),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createSparkCluster",
                    json={
                        "collectionId": COL,
                        "cloudEnvironmentId": ENV,
                        "name": "etl",
                        "config": CONFIG,
                        "description": "Nightly loads",
                        "labels": LABELS,
                    },
                ),
                Reply(json=OPERATION),
            )
        ],
    ),
    _write("delete", "deleteSparkCluster", "id", Effect.DESTRUCTIVE),
    _write("start", "startSparkCluster", "clusterId", Effect.WRITE),
    _write("stop", "stopSparkCluster", "clusterId", Effect.WRITE),
    Case(
        "datalens.sparkclusters.resource_presets_list",
        args=(ENV,),
        kwargs={"limit": 45},
        cli=[
            *("datalens", "sparkclusters", "resource-presets-list"),
            *("--cloud-environment-id", ENV, "--limit", "45"),
        ],
        mcp=(
            "datalens_sparkclusters_resource_presets_list",
            {"cloud_environment_id": ENV, "limit": 45},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listSparkResourcePresets", json={"cloudEnvironmentId": ENV}),
                Reply(json={"resourcePresets": [PRESET], "nextPageToken": "t2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/listSparkResourcePresets",
                    json={"cloudEnvironmentId": ENV, "pageToken": "t2"},
                ),
                Reply(json={"resourcePresets": [{**PRESET, "id": "c4-m16", "cores": "4"}]}),
            ),
        ],
    ),
    Case(
        "datalens.sparkclusters.resource_presets_get",
        args=("c2-m8",),
        kwargs={"cloud_environment_id": ENV},
        cli=[
            *("datalens", "sparkclusters", "resource-presets-get", "c2-m8"),
            *("--cloud-environment-id", ENV),
        ],
        mcp=(
            "datalens_sparkclusters_resource_presets_get",
            {"resource_preset_id": "c2-m8", "cloud_environment_id": ENV},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getSparkResourcePreset",
                    json={"resourcePresetId": "c2-m8", "cloudEnvironmentId": ENV},
                ),
                Reply(json=PRESET),
            )
        ],
    ),
]
