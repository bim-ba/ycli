"""DataLens embedding secrets client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.embeddingsecrets import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.embeddingsecrets.models import (
        EmbeddingSecret,
        EmbeddingSecretCreated,
        EmbeddingSecretDeleted,
    )
    from ycli.yandex.models import ItemList


class EmbeddingSecretsClient(Resource):
    """Keys for embedding: a workbook's key pairs that sign the links of its embeds."""

    def get(self, embedding_secret_id: str) -> EmbeddingSecret:
        """``getEmbeddingSecret`` → one key for embedding, without its private key.

        Args:
            embedding_secret_id: The key's id.

        Returns:
            The key's name, its workbook, and who made it when.

        Examples:
            >>> datalens.embeddingsecrets.get("sec0000000001").title
            'Portal key'
        """
        return self._session.send(endpoints.get(embedding_secret_id))

    def list(self, workbook_id: str) -> ItemList[EmbeddingSecret]:
        """``listEmbeddingSecrets`` → the keys for embedding of a workbook, without private keys.

        Args:
            workbook_id: The workbook's id.

        Returns:
            The keys of the workbook.

        Examples:
            >>> keys = datalens.embeddingsecrets.list("wb000000000001").root
            >>> [key.embedding_secret_id for key in keys]
            ['sec0000000001']
        """
        return self._session.send(endpoints.list_(workbook_id))

    def create(self, *, title: str, workbook_id: str) -> EmbeddingSecretCreated:
        """``createEmbeddingSecret`` — make a key for embedding → its id and its private key.

        The private key is given once, here: :meth:`get` and :meth:`list` do not return it, so
        keep it at once.

        Args:
            title: The name of the key.
            workbook_id: The workbook the key belongs to.

        Returns:
            The id of the key and its private key.

        Examples:
            >>> made = datalens.embeddingsecrets.create(
            ...     title="Portal key", workbook_id="wb000000000001"
            ... )
            >>> made.embedding_secret_id, made.private_key
            ('sec0000000001', 'example-private-key')
        """
        return self._session.send(endpoints.create(title=title, workbook_id=workbook_id))

    def delete(self, embedding_secret_id: str) -> EmbeddingSecretDeleted:
        """``deleteEmbeddingSecret`` — delete a key for embedding → its id.

        Deleting again answers ``404``.

        Args:
            embedding_secret_id: The key's id.

        Returns:
            The id of the deleted key.

        Examples:
            >>> datalens.embeddingsecrets.delete("sec0000000001").embedding_secret_id
            'sec0000000001'
        """
        return self._session.send(endpoints.delete(embedding_secret_id))
