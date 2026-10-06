"""Contract cases for DataLens keys for embedding (see tests/contract/)."""

from tests.contract import Case, Reply, Sent
from ycli.yandex.core.endpoint import Effect

# The keys of a live reply (2026-10-06): a key read back never carries its private key.
KEY = {
    "embeddingSecretId": "sec0000000001",
    "title": "Portal key",
    "workbookId": "wb000000000001",
    "createdBy": "user1",
    "createdAt": "2026-10-01T10:00:00.000Z",
}

CASES = [
    Case(
        "datalens.embeddingsecrets.get",
        args=("sec0000000001",),
        cli=["datalens", "embeddingsecrets", "get", "sec0000000001"],
        mcp=("datalens_embeddingsecrets_get", {"embedding_secret_id": "sec0000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/getEmbeddingSecret", json={"embeddingSecretId": "sec0000000001"}),
                Reply(json=KEY),
            )
        ],
    ),
    Case(
        "datalens.embeddingsecrets.list",
        args=("wb000000000001",),
        cli=["datalens", "embeddingsecrets", "list", "wb000000000001"],
        mcp=("datalens_embeddingsecrets_list", {"workbook_id": "wb000000000001"}),
        effect=Effect.READ,
        exchanges=[
            (
                Sent("POST", "rpc/listEmbeddingSecrets", json={"workbookId": "wb000000000001"}),
                Reply(json=[KEY]),
            )
        ],
    ),
    # The private key is the result of the call: it is printed as it came, on every surface.
    Case(
        "datalens.embeddingsecrets.create",
        kwargs={"title": "Portal key", "workbook_id": "wb000000000001"},
        cli=[
            *("datalens", "embeddingsecrets", "create", "--title", "Portal key"),
            *("--workbook-id", "wb000000000001"),
        ],
        mcp=(
            "datalens_embeddingsecrets_create",
            {"title": "Portal key", "workbook_id": "wb000000000001"},
        ),
        effect=Effect.WRITE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/createEmbeddingSecret",
                    json={"title": "Portal key", "workbookId": "wb000000000001"},
                ),
                Reply(
                    json={"embeddingSecretId": "sec0000000001", "privateKey": "example-private-key"}
                ),
            )
        ],
        output={"embeddingSecretId": "sec0000000001", "privateKey": "example-private-key"},
    ),
    Case(
        "datalens.embeddingsecrets.delete",
        args=("sec0000000001",),
        cli=["datalens", "embeddingsecrets", "delete", "sec0000000001"],
        mcp=("datalens_embeddingsecrets_delete", {"embedding_secret_id": "sec0000000001"}),
        effect=Effect.DESTRUCTIVE,
        exchanges=[
            (
                Sent(
                    "POST",
                    "rpc/deleteEmbeddingSecret",
                    json={"embeddingSecretId": "sec0000000001"},
                ),
                Reply(json={"embeddingSecretId": "sec0000000001"}),
            )
        ],
    ),
]
