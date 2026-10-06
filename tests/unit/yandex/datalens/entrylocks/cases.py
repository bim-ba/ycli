"""Contract cases for DataLens entry locks (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.entrylocks.models import LockExtension, LockRelease, LockTerms

# The six keys of a live reply (2026-10-06).
LOCK = {
    "entryId": "ent00000000001",
    "lockId": "lock-1",
    "startDate": "2026-10-06T12:00:00.000Z",
    "lockToken": "lock-token-1",
    "expiryDate": "2026-10-06T12:10:00.000Z",
    "login": "alice",
}
TERMS = {"duration": 300000, "force": False}
EXTENSION = {"lockToken": "lock-token-1", "duration": 600000}
RELEASE = {"lockToken": "lock-token-1"}

CASES = [
    Case(
        "datalens.entrylocks.create",
        args=("ent00000000001",),
        kwargs={"data": LockTerms.model_validate(TERMS)},
        cli=["datalens", "entrylocks", "create", "ent00000000001", "--data", json.dumps(TERMS)],
        mcp=("datalens_entrylocks_create", {"entry_id": "ent00000000001", "data": TERMS}),
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createEntryLock",
                    json={"entryId": "ent00000000001", "data": TERMS},
                ),
                Reply(json={"lockToken": "lock-token-1"}),
            )
        ],
    ),
    Case(
        "datalens.entrylocks.extend",
        args=("ent00000000001",),
        kwargs={"data": LockExtension.model_validate(EXTENSION)},
        cli=[
            *("datalens", "entrylocks", "extend", "ent00000000001"),
            *("--data", json.dumps(EXTENSION)),
        ],
        mcp=("datalens_entrylocks_extend", {"entry_id": "ent00000000001", "data": EXTENSION}),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/extendEntryLock",
                    json={"entryId": "ent00000000001", "data": EXTENSION},
                ),
                Reply(json=LOCK),
            )
        ],
    ),
    Case(
        "datalens.entrylocks.delete",
        args=("ent00000000001",),
        kwargs={"params": LockRelease.model_validate(RELEASE)},
        cli=[
            *("datalens", "entrylocks", "delete", "ent00000000001"),
            *("--params", json.dumps(RELEASE)),
        ],
        mcp=("datalens_entrylocks_delete", {"entry_id": "ent00000000001", "params": RELEASE}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/deleteEntryLock",
                    json={"entryId": "ent00000000001", "params": RELEASE},
                ),
                Reply(json=LOCK),
            )
        ],
    ),
]
