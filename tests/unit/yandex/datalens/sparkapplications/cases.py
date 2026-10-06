"""Contract cases for DataLens Spark applications (see tests/contract/).

Written from the document: the owner's instance has no Spark cluster, so nothing here was
measured but the refusals (a missing cluster id: 400; a cluster nothing knows: 403).
"""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

STAMP = {"seconds": "1790000000", "nanos": 0}
CLUSTER = "sc00000000001"
APP = "app0000000001"
APPLICATION = {
    "id": APP,
    "clusterId": CLUSTER,
    "createdAt": STAMP,
    "startedAt": STAMP,
    "name": "nightly",
    "createdBy": "user-1",
    "status": "RUNNING",
    "catalogs": [{"catalogId": "cat0000000001"}],
    "applicationSpec": "pysparkApplication",
    "pysparkApplication": {
        "mainPythonFileUri": "s3a://bucket/jobs/nightly.py",
        "args": ["--day", "2026-10-06"],
        "properties": {"spark.executor.instances": "2"},
    },
}

CASES = [
    Case(
        "datalens.sparkapplications.list",
        args=(CLUSTER,),
        cli=["datalens", "sparkapplications", "list", CLUSTER],
        mcp=("datalens_sparkapplications_list", {"cluster_id": CLUSTER}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listSparkApplications", json={"clusterId": CLUSTER}),
                Reply(json={"applications": [APPLICATION], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.sparkapplications.list",
        args=("sc00000000002",),
        kwargs={"filter": ['name="nightly"', 'created_by="user-1"'], "limit": 2},
        cli=[
            *("datalens", "sparkapplications", "list", "sc00000000002"),
            *("--filter", 'name="nightly"', "--filter", 'created_by="user-1"', "--limit", "2"),
        ],
        mcp=(
            "datalens_sparkapplications_list",
            {
                "cluster_id": "sc00000000002",
                "filter": ['name="nightly"', 'created_by="user-1"'],
                "limit": 2,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listSparkApplications",
                    json={
                        "clusterId": "sc00000000002",
                        "filter": ['name="nightly"', 'created_by="user-1"'],
                    },
                ),
                Reply(json={"applications": [APPLICATION], "nextPageToken": "p2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/listSparkApplications",
                    json={
                        "clusterId": "sc00000000002",
                        "filter": ['name="nightly"', 'created_by="user-1"'],
                        "pageToken": "p2",
                    },
                ),
                Reply(json={"applications": [{**APPLICATION, "id": "app0000000002"}]}),
            ),
        ],
    ),
    Case(
        "datalens.sparkapplications.get",
        args=(CLUSTER,),
        kwargs={"application_id": APP},
        cli=["datalens", "sparkapplications", "get", CLUSTER, "--application-id", APP],
        mcp=("datalens_sparkapplications_get", {"cluster_id": CLUSTER, "application_id": APP}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getSparkApplication",
                    json={"clusterId": CLUSTER, "applicationId": APP},
                ),
                Reply(json=APPLICATION),
            )
        ],
    ),
    Case(
        "datalens.sparkapplications.cancel",
        args=(CLUSTER,),
        kwargs={"application_id": APP},
        cli=["datalens", "sparkapplications", "cancel", CLUSTER, "--application-id", APP],
        mcp=("datalens_sparkapplications_cancel", {"cluster_id": CLUSTER, "application_id": APP}),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/cancelSparkApplication",
                    json={"clusterId": CLUSTER, "applicationId": APP},
                ),
                Reply(
                    json={
                        "id": "op0000000000021",
                        "description": "Cancel Spark application",
                        "createdAt": STAMP,
                        "createdBy": "user-1",
                        "modifiedAt": STAMP,
                        "done": False,
                        "metadata": {},
                    }
                ),
            )
        ],
    ),
    Case(
        "datalens.sparkapplications.log_list",
        args=(CLUSTER,),
        kwargs={"application_id": APP},
        cli=["datalens", "sparkapplications", "log-list", CLUSTER, "--application-id", APP],
        mcp=(
            "datalens_sparkapplications_log_list",
            {"cluster_id": CLUSTER, "application_id": APP},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listSparkApplicationLog",
                    json={"clusterId": CLUSTER, "applicationId": APP},
                ),
                Reply(json={"content": "driver started", "nextPageToken": "l2"}),
            )
        ],
    ),
    # The next fragment, by the token of the one before.
    Case(
        "datalens.sparkapplications.log_list",
        args=(CLUSTER,),
        kwargs={"application_id": APP, "page_size": 4096, "page_token": "l2"},
        cli=[
            *("datalens", "sparkapplications", "log-list", CLUSTER, "--application-id", APP),
            *("--page-size", "4096", "--page-token", "l2"),
        ],
        mcp=(
            "datalens_sparkapplications_log_list",
            {"cluster_id": CLUSTER, "application_id": APP, "page_size": 4096, "page_token": "l2"},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listSparkApplicationLog",
                    json={
                        "clusterId": CLUSTER,
                        "applicationId": APP,
                        "pageSize": 4096,
                        "pageToken": "l2",
                    },
                ),
                Reply(json={"content": "job finished", "nextPageToken": ""}),
            )
        ],
    ),
]
