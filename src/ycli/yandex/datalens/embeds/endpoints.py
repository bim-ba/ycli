"""DataLens embed operations, declared once (sans-IO).

Examples:
    >>> list_("ent1").body
    {'entryId': 'ent1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.embeds.models import Embed, EmbedDeleted, EmbedSettings
from ycli.yandex.datalens.schemas.embeds import (
    CreateEmbedArgs,
    DeleteEmbedArgs,
    ListEmbedsArgs,
    UpdateEmbedArgs,
)
from ycli.yandex.models import ItemList


def list_(entry_id: str) -> Endpoint[ItemList[Embed]]:
    body = ListEmbedsArgs(entryId=entry_id)
    return RPC("listEmbeds", ItemList[Embed], json=body, effect=Effect.READ)


def create(
    *,
    title: str,
    embedding_secret_id: str,
    entry_id: str,
    public_params_mode: bool,
    settings: EmbedSettings,
    deps_ids: Sequence[str],
    unsigned_params: Sequence[str],
    private_params: Sequence[str],
) -> Endpoint[Embed]:
    body = CreateEmbedArgs(
        title=title,
        embeddingSecretId=embedding_secret_id,
        entryId=entry_id,
        publicParamsMode=public_params_mode,
        settings=settings,
        depsIds=list(deps_ids),
        unsignedParams=list(unsigned_params),
        privateParams=list(private_params),
    )
    return RPC("createEmbed", Embed, json=body, effect=Effect.WRITE)


def update(
    embed_id: str,
    *,
    title: str,
    embedding_secret_id: str,
    public_params_mode: bool,
    settings: EmbedSettings,
    deps_ids: Sequence[str],
    unsigned_params: Sequence[str],
    private_params: Sequence[str],
) -> Endpoint[Embed]:
    # Measured: every field is required, the embed is saved as given.
    body = UpdateEmbedArgs(
        embedId=embed_id,
        title=title,
        embeddingSecretId=embedding_secret_id,
        publicParamsMode=public_params_mode,
        settings=settings,
        depsIds=list(deps_ids),
        unsignedParams=list(unsigned_params),
        privateParams=list(private_params),
    )
    return RPC("updateEmbed", Embed, json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(embed_id: str) -> Endpoint[EmbedDeleted]:
    body = DeleteEmbedArgs(embedId=embed_id)
    return RPC("deleteEmbed", EmbedDeleted, json=body, effect=Effect.DESTRUCTIVE)
