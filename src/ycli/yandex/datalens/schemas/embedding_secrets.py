# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class CreateEmbeddingSecretResult(APIModel):
    embedding_secret_id: str | None = Field(
        default=None,
        alias="embeddingSecretId",
        description="ID of the newly created key for embedding.",
    )
    private_key: str | None = Field(
        default=None,
        alias="privateKey",
        description="Private key for accessing the embedding.",
    )


class CreateEmbeddingSecretArgs(RequestBody):
    title: str = Field(..., description="Name of the key for embedding to be created.")
    workbook_id: str = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook to associate with the key for embedding.",
    )


class EmbeddingSecret(APIModel):
    embedding_secret_id: str | None = Field(
        default=None,
        alias="embeddingSecretId",
        description="Unique identifier of the key for embedding.",
    )
    title: str | None = Field(default=None, description="Name of the key for embedding.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook associated with the key for embedding.",
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the key for embedding.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the key for embedding was created.",
    )


class ListEmbeddingSecretsArgs(RequestBody):
    workbook_id: str = Field(
        ...,
        alias="workbookId",
        description="ID of the workbook to list its keys for embedding.",
    )


class DeleteEmbeddingSecretResult(APIModel):
    embedding_secret_id: str | None = Field(
        default=None,
        alias="embeddingSecretId",
        description="ID of the deleted key for embedding.",
    )


class DeleteEmbeddingSecretArgs(RequestBody):
    embedding_secret_id: str = Field(
        ...,
        alias="embeddingSecretId",
        description="ID of the key for embedding to delete.",
    )


class GetEmbeddingSecretArgs(RequestBody):
    embedding_secret_id: str = Field(
        ...,
        alias="embeddingSecretId",
        description="ID of the key for embedding to retrieve.",
    )


class ListEmbeddingSecretsResponse(RootModel[list[EmbeddingSecret]]):
    root: list[EmbeddingSecret]
