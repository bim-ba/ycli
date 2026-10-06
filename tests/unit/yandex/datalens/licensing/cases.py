"""Contract cases for DataLens licensing (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

# The keys of the live replies (2026-10-06); `isQuarantined`, `quarantineEndsAt` and
# `occupiedSeatsCount` are not in the document.
HELD = {
    "licenseId": "lic0000000001",
    "meta": {},
    "tenantId": "org_bpf00000000000000000",
    "userId": "user-1",
    "licenseType": "creator",
    "isActive": True,
    "isQuarantined": False,
    "quarantineEndsAt": None,
    "expiresAt": None,
    "createdBy": "user-1",
    "createdAt": "2026-09-01T10:00:00.000Z",
    "updatedBy": "user-1",
    "updatedAt": "2026-09-01T10:00:00.000Z",
    "lastLoginAt": "2026-10-06T09:00:00.000Z",
}
LIMITS = {
    "current": {
        "type": "regular",
        "value": 1,
        "startedAt": "2026-09-01T00:00:00.000Z",
        "activeLicensesCount": 1,
        "occupiedSeatsCount": 1,
    },
    "next": None,
}
# Written from the document: the two writes were never called.
GIVEN = {key: value for key, value in HELD.items() if key != "lastLoginAt"} | {"userId": "user-2"}

CASES = [
    Case(
        "datalens.licensing.licenses_list",
        kwargs={"status": "active"},
        cli=["datalens", "licensing", "licenses-list", "--status", "active"],
        mcp=("datalens_licensing_licenses_list", {"status": "active"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getLicenses", json={"status": "active"}),
                # Measured: the last page has no `nextPageToken` at all.
                Reply(json={"licenses": [HELD]}),
            )
        ],
    ),
    Case(
        "datalens.licensing.licenses_list",
        kwargs={
            "user_ids": ["user-1", "user-3"],
            "sort_by": "updatedAt",
            "order": "desc",
            "limit": 2,
        },
        cli=[
            *("datalens", "licensing", "licenses-list", "--user-ids", "user-1"),
            *("--user-ids", "user-3", "--sort-by", "updatedAt", "--order", "desc"),
            *("--limit", "2"),
        ],
        mcp=(
            "datalens_licensing_licenses_list",
            {"user_ids": ["user-1", "user-3"], "sort_by": "updatedAt", "order": "desc", "limit": 2},
        ),
        effect=Effect.READ,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/getLicenses",
                    json={"userIds": ["user-1", "user-3"], "sortBy": "updatedAt", "order": "desc"},
                ),
                Reply(json={"licenses": [HELD], "nextPageToken": "t2"}),
            ),
            (
                Sent(
                    "POST",
                    "rpc/getLicenses",
                    json={
                        "userIds": ["user-1", "user-3"],
                        "sortBy": "updatedAt",
                        "order": "desc",
                        "pageToken": "t2",
                    },
                ),
                Reply(json={"licenses": [{**HELD, "licenseId": "lic0000000003"}]}),
            ),
        ],
    ),
    Case(
        "datalens.licensing.licenses_assign",
        args=(["user-2"],),
        cli=["datalens", "licensing", "licenses-assign", "user-2"],
        mcp=("datalens_licensing_licenses_assign", {"user_ids": ["user-2"]}),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/assignLicenses", json={"userIds": ["user-2"]}),
                Reply(json=[GIVEN]),
            )
        ],
    ),
    Case(
        "datalens.licensing.limit_get",
        cli=["datalens", "licensing", "limit-get"],
        mcp=("datalens_licensing_limit_get", {}),
        effect=Effect.READ,
        exchanges=[(Sent("POST", "rpc/getLicensesLimit"), Reply(json=LIMITS))],
    ),
    Case(
        "datalens.licensing.limit_set",
        args=(3,),
        cli=["datalens", "licensing", "limit-set", "3"],
        mcp=("datalens_licensing_limit_set", {"value": 3}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/setLicenseLimit", json={"value": 3}),
                Reply(
                    json={
                        "current": {**LIMITS["current"], "value": 3},
                        "next": None,
                    }
                ),
            )
        ],
    ),
]
