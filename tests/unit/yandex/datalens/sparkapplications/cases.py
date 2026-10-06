"""Contract cases for DataLens Spark applications (see tests/contract/).

Written from the document: the owner's instance has no Spark cluster, so nothing here was
measured but the refusals (a missing cluster id: 400; a cluster nothing knows: 403).
"""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.sparkapplications.models import SparkApplicationCreate

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
JAR = {"mainJarFileUri": "s3a://bucket/jobs/etl.jar", "mainClass": "org.example.Etl"}
PYSPARK = {"mainPythonFileUri": "s3a://bucket/jobs/nightly.py", "args": ["--day", "2026-10-06"]}
CONNECT = {"properties": {"spark.executor.instances": "2"}}
NEW_JAR = {"clusterId": CLUSTER, "name": "etl", "sparkApplication": JAR}
NEW_PYSPARK = {
    "clusterId": "sc00000000003",
    "name": "nightly",
    "catalogs": [{"catalogId": "cat0000000001"}, {"catalogId": "cat0000000002"}],
    "pysparkApplication": PYSPARK,
}
NEW_CONNECT = {"clusterId": "sc00000000004", "sparkConnectApplication": CONNECT}


def _made(operation_id: str) -> Reply:
    return Reply(
        json={
            "id": operation_id,
            "description": "Create Spark application",
            "createdAt": STAMP,
            "createdBy": "user-1",
            "modifiedAt": STAMP,
            "done": False,
            "metadata": {},
        }
    )


CASES = [
    Case(
        "datalens.sparkapplications.create",
        args=(SparkApplicationCreate.model_validate(NEW_JAR),),
        cli=[
            *("datalens", "sparkapplications", "create", CLUSTER, "--name", "etl"),
            *("--spark-application", json.dumps(JAR)),
        ],
        mcp=("datalens_sparkapplications_create", {"body": NEW_JAR}),
        effect=Effect.WRITE,
        exchanges=[
            (Sent("POST", "rpc/createSparkApplication", json=NEW_JAR), _made("op0000000000022"))
        ],
    ),
    Case(
        "datalens.sparkapplications.create",
        args=(SparkApplicationCreate.model_validate(NEW_PYSPARK),),
        cli=[
            *("datalens", "sparkapplications", "create", "sc00000000003", "--name", "nightly"),
            *("--catalogs", '{"catalogId": "cat0000000001"}'),
            *("--catalogs", '{"catalogId": "cat0000000002"}'),
            *("--pyspark-application", json.dumps(PYSPARK)),
        ],
        mcp=("datalens_sparkapplications_create", {"body": NEW_PYSPARK}),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/createSparkApplication", json=NEW_PYSPARK),
                _made("op0000000000023"),
            )
        ],
    ),
    Case(
        "datalens.sparkapplications.create",
        args=(SparkApplicationCreate.model_validate(NEW_CONNECT),),
        cli=[
            *("datalens", "sparkapplications", "create", "sc00000000004"),
            *("--spark-connect-application", json.dumps(CONNECT)),
        ],
        mcp=("datalens_sparkapplications_create", {"body": NEW_CONNECT}),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/createSparkApplication", json=NEW_CONNECT),
                _made("op0000000000024"),
            )
        ],
    ),
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
