# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody


class EmbedSettings(APIModel):
    enable_export: bool | None = Field(
        default=None,
        alias="enableExport",
        description="Whether data export is enabled for the embedding.",
    )


class Embed(APIModel):
    embed_id: str | None = Field(
        default=None, alias="embedId", description="Unique identifier of the embedding."
    )
    title: str | None = Field(default=None, description="Name of the embedding.")
    embedding_secret_id: str | None = Field(
        default=None,
        alias="embeddingSecretId",
        description="ID of the key for embedding used for authentication.",
    )
    entry_id: str | None = Field(
        default=None,
        alias="entryId",
        description="ID of the entry being privately embedded.",
    )
    deps_ids: list[str] | None = Field(
        default=None, alias="depsIds", description="Array of dependency entry IDs."
    )
    unsigned_params: list[str] | None = Field(
        default=None,
        alias="unsignedParams",
        description="Array of unsigned parameters to be provided in the embedding link.",
    )
    private_params: list[str] | None = Field(
        default=None,
        alias="privateParams",
        description="Array of signed parameters that are provided as part of the token.",
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the embedding.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Timestamp when the embedding was created.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the embedding was last updated.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who was the last to update the embedding.",
    )
    public_params_mode: bool | None = Field(
        default=None,
        alias="publicParamsMode",
        description="Whether default parameters mode is enabled.",
    )
    settings: EmbedSettings | None = None


class CreateEmbedArgs(RequestBody):
    title: str = Field(..., description="Name of the embedding.")
    embedding_secret_id: str = Field(
        ...,
        alias="embeddingSecretId",
        description="ID of the key for embedding used for authentication.",
    )
    entry_id: str = Field(
        ..., alias="entryId", description="ID of the entry to be privately embedded."
    )
    deps_ids: list[str] = Field(..., alias="depsIds", description="Array of dependency entry IDs.")
    unsigned_params: list[str] = Field(
        ...,
        alias="unsignedParams",
        description="Array of unsigned parameters to be provided in the embedding link.",
    )
    private_params: list[str] = Field(
        ...,
        alias="privateParams",
        description="Array of signed parameters that are provided as part of the token.",
    )
    public_params_mode: bool = Field(
        ...,
        alias="publicParamsMode",
        description="Whether default parameters mode is enabled.",
    )
    settings: EmbedSettings


class ListEmbedsArgs(RequestBody):
    entry_id: str = Field(
        ..., alias="entryId", description="ID of the entry to list embeddings for."
    )


class DeleteEmbedResult(APIModel):
    embed_id: str | None = Field(
        default=None, alias="embedId", description="ID of the deleted embedding."
    )


class DeleteEmbedArgs(RequestBody):
    embed_id: str = Field(..., alias="embedId", description="ID of the embedding to delete.")


class UpdateEmbedArgs(RequestBody):
    embed_id: str = Field(..., alias="embedId", description="ID of the embedding to update.")
    title: str = Field(..., description="Name of the embedding.")
    embedding_secret_id: str = Field(
        ...,
        alias="embeddingSecretId",
        description="ID of the key for embedding used for authentication.",
    )
    deps_ids: list[str] = Field(..., alias="depsIds", description="Array of dependency entry IDs.")
    unsigned_params: list[str] = Field(
        ...,
        alias="unsignedParams",
        description="Array of unsigned parameters to be provided in the embedding link.",
    )
    private_params: list[str] = Field(
        ...,
        alias="privateParams",
        description="Array of signed parameters that are provided as part of the token.",
    )
    public_params_mode: bool = Field(
        ...,
        alias="publicParamsMode",
        description="Whether default parameters mode is enabled.",
    )
    settings: EmbedSettings


class ListEmbedsResponse(RootModel[list[Embed]], hide_input_in_errors=True):
    """Array of embeddings."""

    root: list[Embed] = Field(..., description="Array of embeddings.")
