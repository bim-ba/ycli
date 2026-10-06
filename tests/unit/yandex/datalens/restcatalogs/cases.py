"""Contract cases for DataLens REST catalogs (see tests/contract/).

Only the listing of an instance with no catalog was measured (2026-10-06); a catalog in a
reply, and making one, are written from the document.
"""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.restcatalogs.models import RestCatalogBucketSettings

STAMP = {"seconds": "1790000000", "nanos": 0}
CATALOG = {
    "id": "cat0000000001",
    "organizationId": "bpf00000000000000000",
    "tenantId": "org_bpf00000000000000000",
    "cloudEnvironmentId": "env0000000001",
    "name": "lake",
    "description": "",
    "labels": {"team": "analytics"},
    "createdAt": STAMP,
    "createdById": "user-1",
    "updatedAt": STAMP,
    "bucket": {
        "settings": {"storageClass": "STANDARD", "maxSize": "1073741824"},
        "details": {"usedSize": "2048", "maxSize": "1073741824", "updatedAt": STAMP},
    },
}
SETTINGS = {"storageClass": "COLD", "maxSize": "2147483648", "alias": "cold-lake"}
STARTED = {
    "id": "op0000000000006",
    "description": "Create REST catalog",
    "createdAt": STAMP,
    "createdBy": "user-1",
    "modifiedAt": STAMP,
    "done": False,
    "metadata": {},
}

CASES = [
    Case(
        "datalens.restcatalogs.list",
        kwargs={"cloud_environment_id": "env0000000001"},
        cli=["datalens", "restcatalogs", "list", "--cloud-environment-id", "env0000000001"],
        mcp=("datalens_restcatalogs_list", {"cloud_environment_id": "env0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listCatalogs", json={"cloudEnvironmentId": "env0000000001"}),
                Reply(json={"restCatalogs": [CATALOG], "nextPageToken": ""}),
            )
        ],
    ),
    # Measured: an instance with no catalog answers an empty list and an empty token.
    Case(
        "datalens.restcatalogs.list",
        kwargs={
            "filter": ['name="lake"'],
            "sort_by": "updatedAt",
            "reverse_order": True,
            "include_permissions": True,
            "limit": 9,
        },
        cli=[
            *("datalens", "restcatalogs", "list", "--filter", 'name="lake"'),
            *("--sort-by", "updatedAt", "--reverse-order", "--include-permissions"),
            *("--limit", "9"),
        ],
        mcp=(
            "datalens_restcatalogs_list",
            {
                "filter": ['name="lake"'],
                "sort_by": "updatedAt",
                "reverse_order": True,
                "include_permissions": True,
                "limit": 9,
            },
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/listCatalogs",
                    json={
                        "filter": ['name="lake"'],
                        "sortBy": "updatedAt",
                        "reverseOrder": True,
                        "includePermissions": True,
                    },
                ),
                Reply(json={"restCatalogs": [], "nextPageToken": ""}),
            )
        ],
    ),
    Case(
        "datalens.restcatalogs.create",
        kwargs={
            "cloud_environment_id": "env0000000001",
            "name": "lake",
            "bucket_settings": RestCatalogBucketSettings(),
        },
        cli=[
            *("datalens", "restcatalogs", "create", "--cloud-environment-id", "env0000000001"),
            *("--name", "lake", "--bucket-settings", "{}"),
        ],
        mcp=(
            "datalens_restcatalogs_create",
            {"cloud_environment_id": "env0000000001", "name": "lake", "bucket_settings": {}},
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createRestCatalog",
                    json={
                        "cloudEnvironmentId": "env0000000001",
                        "name": "lake",
                        "bucketSettings": {},
                    },
                ),
                Reply(json=STARTED),
            )
        ],
    ),
    Case(
        "datalens.restcatalogs.create",
        kwargs={
            "cloud_environment_id": "env0000000002",
            "name": "cold",
            "bucket_settings": RestCatalogBucketSettings.model_validate(SETTINGS),
            "description": "Rarely read",
            "labels": {"team": "analytics"},
        },
        cli=[
            *("datalens", "restcatalogs", "create", "--cloud-environment-id", "env0000000002"),
            *("--name", "cold", "--bucket-settings", json.dumps(SETTINGS)),
            *("--description", "Rarely read", "--labels", json.dumps({"team": "analytics"})),
        ],
        mcp=(
            "datalens_restcatalogs_create",
            {
                "cloud_environment_id": "env0000000002",
                "name": "cold",
                "bucket_settings": SETTINGS,
                "description": "Rarely read",
                "labels": {"team": "analytics"},
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createRestCatalog",
                    json={
                        "cloudEnvironmentId": "env0000000002",
                        "name": "cold",
                        "bucketSettings": SETTINGS,
                        "description": "Rarely read",
                        "labels": {"team": "analytics"},
                    },
                ),
                Reply(json={**STARTED, "id": "op0000000000007"}),
            )
        ],
    ),
]
