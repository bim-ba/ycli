"""Contract cases for DataLens embeds (see tests/contract/)."""

import json

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect
from ycli.yandex.datalens.embeds.models import EmbedSettings

# The keys of a live reply (2026-10-06); `type` and `allowAllDeps` are not in the document.
EMBED = {
    "embedId": "emb0000000001",
    "title": "Sales on the portal",
    "embeddingSecretId": "sec0000000001",
    "entryId": "ent0000000001",
    "depsIds": [],
    "unsignedParams": [],
    "privateParams": [],
    "publicParamsMode": True,
    "type": None,
    "allowAllDeps": False,
    "createdBy": "user1",
    "createdAt": "2026-10-01T10:00:00.000Z",
    "updatedBy": "user1",
    "updatedAt": "2026-10-01T10:00:00.000Z",
    "settings": {},
}
NEW = {
    "title": "Sales on the portal",
    "embeddingSecretId": "sec0000000001",
    "entryId": "ent0000000001",
    "publicParamsMode": True,
    "settings": {},
    "depsIds": [],
    "unsignedParams": [],
    "privateParams": [],
}
FULL = {
    "title": "Stock for partners",
    "embeddingSecretId": "sec0000000002",
    "entryId": "ent0000000002",
    "publicParamsMode": False,
    "settings": {"enableExport": True},
    "depsIds": ["dep0000000001", "dep0000000002"],
    "unsignedParams": ["region"],
    "privateParams": ["tenant", "role"],
}
SAVED = {
    "embedId": "emb0000000001",
    "title": "Sales, renamed",
    "embeddingSecretId": "sec0000000001",
    "publicParamsMode": False,
    "settings": {"enableExport": True},
    "depsIds": [],
    "unsignedParams": ["region"],
    "privateParams": [],
}

CASES = [
    Case(
        "datalens.embeds.list",
        args=("ent0000000001",),
        cli=["datalens", "embeds", "list", "ent0000000001"],
        mcp=("datalens_embeds_list", {"entry_id": "ent0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (Sent("POST", "rpc/listEmbeds", json={"entryId": "ent0000000001"}), Reply(json=[EMBED]))
        ],
    ),
    # Only what the API requires: a list nobody named goes out empty.
    Case(
        "datalens.embeds.create",
        kwargs={
            "title": "Sales on the portal",
            "embedding_secret_id": "sec0000000001",
            "entry_id": "ent0000000001",
            "public_params_mode": True,
            "settings": EmbedSettings(),
        },
        cli=[
            *("datalens", "embeds", "create", "--title", "Sales on the portal"),
            *("--embedding-secret-id", "sec0000000001", "--entry-id", "ent0000000001"),
            *("--public-params-mode", "--settings", "{}"),
        ],
        mcp=(
            "datalens_embeds_create",
            {
                "title": "Sales on the portal",
                "embedding_secret_id": "sec0000000001",
                "entry_id": "ent0000000001",
                "public_params_mode": True,
                "settings": {},
            },
        ),
        effect=Effect.WRITE,
        exchanges=[(Sent("POST", "rpc/createEmbed", json=NEW), Reply(json=EMBED))],
    ),
    Case(
        "datalens.embeds.create",
        kwargs={
            "title": "Stock for partners",
            "embedding_secret_id": "sec0000000002",
            "entry_id": "ent0000000002",
            "public_params_mode": False,
            "settings": EmbedSettings.model_validate({"enableExport": True}),
            "deps_ids": ["dep0000000001", "dep0000000002"],
            "unsigned_params": ["region"],
            "private_params": ["tenant", "role"],
        },
        cli=[
            *("datalens", "embeds", "create", "--title", "Stock for partners"),
            *("--embedding-secret-id", "sec0000000002", "--entry-id", "ent0000000002"),
            *("--no-public-params-mode", "--settings", json.dumps({"enableExport": True})),
            *("--deps-ids", "dep0000000001", "--deps-ids", "dep0000000002"),
            *("--unsigned-params", "region"),
            *("--private-params", "tenant", "--private-params", "role"),
        ],
        mcp=(
            "datalens_embeds_create",
            {
                "title": "Stock for partners",
                "embedding_secret_id": "sec0000000002",
                "entry_id": "ent0000000002",
                "public_params_mode": False,
                "settings": {"enableExport": True},
                "deps_ids": ["dep0000000001", "dep0000000002"],
                "unsigned_params": ["region"],
                "private_params": ["tenant", "role"],
            },
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent("POST", "rpc/createEmbed", json=FULL),
                Reply(json={**EMBED, **FULL, "embedId": "emb0000000002"}),
            )
        ],
    ),
    Case(
        "datalens.embeds.update",
        args=("emb0000000001",),
        kwargs={
            "title": "Sales, renamed",
            "embedding_secret_id": "sec0000000001",
            "public_params_mode": False,
            "settings": EmbedSettings.model_validate({"enableExport": True}),
            "unsigned_params": ["region"],
        },
        cli=[
            *("datalens", "embeds", "update", "emb0000000001", "--title", "Sales, renamed"),
            *("--embedding-secret-id", "sec0000000001", "--no-public-params-mode"),
            *("--settings", json.dumps({"enableExport": True}), "--unsigned-params", "region"),
        ],
        mcp=(
            "datalens_embeds_update",
            {
                "embed_id": "emb0000000001",
                "title": "Sales, renamed",
                "embedding_secret_id": "sec0000000001",
                "public_params_mode": False,
                "settings": {"enableExport": True},
                "unsigned_params": ["region"],
            },
        ),
        effect=Effect.IDEMPOTENT_WRITE,
        exchanges=[(Sent("POST", "rpc/updateEmbed", json=SAVED), Reply(json={**EMBED, **SAVED}))],
    ),
    Case(
        "datalens.embeds.delete",
        args=("emb0000000001",),
        cli=["datalens", "embeds", "delete", "emb0000000001"],
        mcp=("datalens_embeds_delete", {"embed_id": "emb0000000001"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent("POST", "rpc/deleteEmbed", json={"embedId": "emb0000000001"}),
                Reply(json={"embedId": "emb0000000001"}),
            )
        ],
    ),
]
