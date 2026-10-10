"""DataLens embedding secret operations, declared once (sans-IO).

Examples:
    >>> get("sec1").body
    {'embeddingSecretId': 'sec1'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.embeddingsecrets.models import (
    EmbeddingSecret,
    EmbeddingSecretCreated,
    EmbeddingSecretDeleted,
)
from ycli.yandex.datalens.schemas.embedding_secrets import (
    CreateEmbeddingSecretArgs,
    DeleteEmbeddingSecretArgs,
    GetEmbeddingSecretArgs,
    ListEmbeddingSecretsArgs,
)
from ycli.yandex.models import ItemList


def get(embedding_secret_id: str) -> Endpoint[EmbeddingSecret]:
    body = GetEmbeddingSecretArgs(embeddingSecretId=embedding_secret_id)
    return RPC("getEmbeddingSecret", EmbeddingSecret, json=body, effect=Effect.READ)


def list_(workbook_id: str) -> Endpoint[ItemList[EmbeddingSecret]]:
    body = ListEmbeddingSecretsArgs(workbookId=workbook_id)
    return RPC("listEmbeddingSecrets", ItemList[EmbeddingSecret], json=body, effect=Effect.READ)


def create(*, title: str, workbook_id: str) -> Endpoint[EmbeddingSecretCreated]:
    # The private key in the reply is the result of the call, given once: it is read as the
    # string it is, not masked (#448).
    body = CreateEmbeddingSecretArgs(title=title, workbookId=workbook_id)
    return RPC(
        "createEmbeddingSecret",
        EmbeddingSecretCreated,
        json=body,
        effect=Effect.WRITE,
        grants_access=True,
    )


def delete(embedding_secret_id: str) -> Endpoint[EmbeddingSecretDeleted]:
    body = DeleteEmbeddingSecretArgs(embeddingSecretId=embedding_secret_id)
    return RPC(
        "deleteEmbeddingSecret", EmbeddingSecretDeleted, json=body, effect=Effect.DESTRUCTIVE
    )
