"""Contract cases for DataLens cloud environments (see tests/contract/).

Only the listing of an instance with no environment was measured (2026-10-06); the replies
with an environment in them, and every write, are written from the document.
"""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.cloudenvironments.models import (
    CloudEnvironmentNewStorage,
    CloudEnvironmentStorageChange,
)

STAMP = {"seconds": "1790000000", "nanos": 0}
ENVIRONMENT = {
    "id": "env0000000001",
    "name": "Analytics",
    "description": "",
    "createdAt": STAMP,
    "createdById": "user-1",
    "updatedAt": STAMP,
    "updatedById": "user-1",
    "status": "READY",
    "statusDetails": "",
    "cloudId": "b1g00000000000000001",
    "tenantId": "org_bpf00000000000000000",
    "subnetId": "e9b0000000001",
    "securityGroupIds": ["enp0000000001"],
    "storage": {"maxSize": "0"},
}


def _operation(number: int, description: str) -> dict:
    return {
        "id": f"op000000000000{number}",
        "description": description,
        "createdAt": STAMP,
        "createdBy": "user-1",
        "modifiedAt": STAMP,
        "done": False,
        "metadata": {},
    }


CASES = [
    Case(
        "datalens.cloudenvironments.list",
        kwargs={"filter": ['status="READY"']},
        cli=["datalens", "cloudenvironments", "list", "--filter", 'status="READY"'],
        mcp=("datalens_cloudenvironments_list", {"filter": ['status="READY"']}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listCloudEnvironments", json={"filter": ['status="READY"']}),
                Reply(json={"cloudEnvironments": [ENVIRONMENT], "nextPageToken": ""}),
            )
        ],
    ),
    # Measured: an instance with no environment answers an empty list and an empty token.
    Case(
        "datalens.cloudenvironments.list",
        kwargs={"include_permissions": True, "limit": 7},
        cli=["datalens", "cloudenvironments", "list", "--include-permissions", "--limit", "7"],
        mcp=("datalens_cloudenvironments_list", {"include_permissions": True, "limit": 7}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listCloudEnvironments", json={"includePermissions": True}),
                Reply(json={"cloudEnvironments": [], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironments.get",
        args=("env0000000001",),
        kwargs={"include_permissions": True},
        cli=["datalens", "cloudenvironments", "get", "env0000000001", "--include-permissions"],
        mcp=(
            "datalens_cloudenvironments_get",
            {"id": "env0000000001", "include_permissions": True},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getCloudEnvironment",
                    json={"id": "env0000000001", "includePermissions": True},
                ),
                Reply(json={**ENVIRONMENT, "permissions": {"update": True, "delete": False}}),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironments.create",
        kwargs={
            "name": "Analytics",
            "cloud_id": "b1g00000000000000001",
            "subnet_id": "e9b0000000001",
        },
        cli=[
            *("datalens", "cloudenvironments", "create", "--name", "Analytics"),
            *("--cloud-id", "b1g00000000000000001", "--subnet-id", "e9b0000000001"),
        ],
        mcp=(
            "datalens_cloudenvironments_create",
            {
                "name": "Analytics",
                "cloud_id": "b1g00000000000000001",
                "subnet_id": "e9b0000000001",
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createCloudEnvironment",
                    json={
                        "name": "Analytics",
                        "cloudId": "b1g00000000000000001",
                        "subnetId": "e9b0000000001",
                    },
                ),
                Reply(json=_operation(1, "Create cloud environment")),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironments.create",
        kwargs={
            "name": "Lake",
            "cloud_id": "b1g00000000000000002",
            "subnet_id": "e9b0000000002",
            "description": "With a bucket",
            "security_group_ids": ["enp0000000002", "enp0000000003"],
            "storage": CloudEnvironmentNewStorage.model_validate({"maxSize": "1073741824"}),
        },
        cli=[
            *("datalens", "cloudenvironments", "create", "--name", "Lake"),
            *("--cloud-id", "b1g00000000000000002", "--subnet-id", "e9b0000000002"),
            *("--description", "With a bucket", "--security-group-ids", "enp0000000002"),
            *("--security-group-ids", "enp0000000003"),
            *("--storage", json.dumps({"maxSize": "1073741824"})),
        ],
        mcp=(
            "datalens_cloudenvironments_create",
            {
                "name": "Lake",
                "cloud_id": "b1g00000000000000002",
                "subnet_id": "e9b0000000002",
                "description": "With a bucket",
                "security_group_ids": ["enp0000000002", "enp0000000003"],
                "storage": {"maxSize": "1073741824"},
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createCloudEnvironment",
                    json={
                        "name": "Lake",
                        "cloudId": "b1g00000000000000002",
                        "subnetId": "e9b0000000002",
                        "description": "With a bucket",
                        "securityGroupIds": ["enp0000000002", "enp0000000003"],
                        "storage": {"maxSize": "1073741824"},
                    },
                ),
                Reply(json=_operation(4, "Create cloud environment")),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironments.update",
        args=("env0000000001",),
        kwargs={"name": "Analytics, EU"},
        cli=["datalens", "cloudenvironments", "update", "env0000000001", "--name", "Analytics, EU"],
        mcp=(
            "datalens_cloudenvironments_update",
            {"id": "env0000000001", "name": "Analytics, EU"},
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateCloudEnvironment",
                    json={"id": "env0000000001", "name": "Analytics, EU"},
                ),
                Reply(json=_operation(2, "Update cloud environment")),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironments.update",
        args=("env0000000002",),
        kwargs={
            "description": "Bigger bucket",
            "security_group_ids": ["enp0000000004"],
            "storage": CloudEnvironmentStorageChange.model_validate({"maxSize": "2147483648"}),
        },
        cli=[
            *("datalens", "cloudenvironments", "update", "env0000000002"),
            *("--description", "Bigger bucket", "--security-group-ids", "enp0000000004"),
            *("--storage", json.dumps({"maxSize": "2147483648"})),
        ],
        mcp=(
            "datalens_cloudenvironments_update",
            {
                "id": "env0000000002",
                "description": "Bigger bucket",
                "security_group_ids": ["enp0000000004"],
                "storage": {"maxSize": "2147483648"},
            },
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/updateCloudEnvironment",
                    json={
                        "id": "env0000000002",
                        "description": "Bigger bucket",
                        "securityGroupIds": ["enp0000000004"],
                        "storage": {"maxSize": "2147483648"},
                    },
                ),
                Reply(json=_operation(5, "Update cloud environment")),
            )
        ],
    ),
    Case(
        "datalens.cloudenvironments.delete",
        args=("env0000000001",),
        cli=["datalens", "cloudenvironments", "delete", "env0000000001"],
        mcp=("datalens_cloudenvironments_delete", {"id": "env0000000001"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent("POST", "rpc/deleteCloudEnvironment", json={"id": "env0000000001"}),
                Reply(json=_operation(3, "Delete cloud environment")),
            )
        ],
    ),
]
