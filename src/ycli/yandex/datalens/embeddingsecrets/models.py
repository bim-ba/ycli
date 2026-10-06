"""DataLens embedding secret models: the public names of the generated classes it uses."""

from ycli.yandex.datalens.schemas.embedding_secrets import (
    CreateEmbeddingSecretResult as EmbeddingSecretCreated,
)
from ycli.yandex.datalens.schemas.embedding_secrets import (
    DeleteEmbeddingSecretResult as EmbeddingSecretDeleted,
)
from ycli.yandex.datalens.schemas.embedding_secrets import EmbeddingSecret

__all__ = ["EmbeddingSecret", "EmbeddingSecretCreated", "EmbeddingSecretDeleted"]
