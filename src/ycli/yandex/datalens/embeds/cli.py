"""`datalens embeds` commands."""

import json
from typing import Annotated

import typer

from ycli.cli.body_fields import CallerFields
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.embeds.models import Embed, EmbedDeleted
from ycli.yandex.datalens.schemas.embeds import CreateEmbedArgs, UpdateEmbedArgs
from ycli.yandex.models import ItemList

app = typer.Typer(name="embeds", help="DataLens embeds.", no_args_is_help=True)

EmbedIDArg = Annotated[str, typer.Argument(metavar="EMBED_ID", help="Embed id.")]
TitleOption = Annotated[str | None, typer.Option("--title", help="The name of the embed.")]
SecretOption = Annotated[
    str | None,
    typer.Option("--embedding-secret-id", help="The key for embedding that signs its links."),
]
DepsOption = Annotated[
    list[str] | None,
    typer.Option("--deps-ids", help="An entry the embedded one depends on (repeatable)."),
]
UnsignedOption = Annotated[
    list[str] | None,
    typer.Option("--unsigned-params", help="A parameter a link may carry unsigned (repeatable)."),
]
PrivateOption = Annotated[
    list[str] | None,
    typer.Option(
        "--private-params", help="A parameter that goes signed, in the token (repeatable)."
    ),
]
PublicParamsModeOption = Annotated[
    bool | None,
    typer.Option(
        "--public-params-mode/--no-public-params-mode",
        help="Whether the default mode of parameters is on.",
    ),
]
SettingsOption = Annotated[
    str | None,
    typer.Option(
        "--settings", help='The settings, as a JSON object: {"enableExport": true}, or {}.'
    ),
]
# The three lists are required by the API; a list nobody named is an empty one.
NOTHING_NAMED = {"depsIds": [], "unsignedParams": [], "privateParams": []}


@app.command("list")
def list_(
    entry_id: Annotated[str, typer.Argument(metavar="ENTRY_ID", help="Entry id.")],
    *,
    datalens: DataLensClient,
) -> ItemList[Embed]:
    """List the embeds of an entry."""
    return datalens.embeds.list(entry_id)


@app.command()
def create(
    title: TitleOption = None,
    embedding_secret_id: SecretOption = None,
    entry_id: Annotated[str | None, typer.Option("--entry-id", help="The entry to embed.")] = None,
    public_params_mode: PublicParamsModeOption = None,
    settings: SettingsOption = None,
    deps_ids: DepsOption = None,
    unsigned_params: UnsignedOption = None,
    private_params: PrivateOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> Embed:
    """Embed an entry; the title, the key, the entry, the mode and the settings are required."""
    given = {
        "title": title,
        "embeddingSecretId": embedding_secret_id,
        "entryId": entry_id,
        "publicParamsMode": public_params_mode,
        "settings": None if settings is None else json.loads(settings),
        "depsIds": deps_ids or None,
        "unsignedParams": unsigned_params or None,
        "privateParams": private_params or None,
    }
    # Any of them may come from --body-file: merge before the model is built.
    flags = {key: value for key, value in given.items() if value is not None}
    body = CreateEmbedArgs.model_validate({**NOTHING_NAMED, **caller.over(flags)})
    return datalens.embeds.create(
        title=body.title,
        embedding_secret_id=body.embedding_secret_id,
        entry_id=body.entry_id,
        public_params_mode=body.public_params_mode,
        settings=body.settings,
        deps_ids=body.deps_ids,
        unsigned_params=body.unsigned_params,
        private_params=body.private_params,
    )


@app.command()
def update(
    embed_id: EmbedIDArg,
    title: TitleOption = None,
    embedding_secret_id: SecretOption = None,
    public_params_mode: PublicParamsModeOption = None,
    settings: SettingsOption = None,
    deps_ids: DepsOption = None,
    unsigned_params: UnsignedOption = None,
    private_params: PrivateOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> Embed:
    """Save an embed as given: the API takes it whole, so name everything that is to stay."""
    given = {
        "embedId": embed_id,
        "title": title,
        "embeddingSecretId": embedding_secret_id,
        "publicParamsMode": public_params_mode,
        "settings": None if settings is None else json.loads(settings),
        "depsIds": deps_ids or None,
        "unsignedParams": unsigned_params or None,
        "privateParams": private_params or None,
    }
    flags = {key: value for key, value in given.items() if value is not None}
    body = UpdateEmbedArgs.model_validate({**NOTHING_NAMED, **caller.over(flags)})
    return datalens.embeds.update(
        body.embed_id,
        title=body.title,
        embedding_secret_id=body.embedding_secret_id,
        public_params_mode=body.public_params_mode,
        settings=body.settings,
        deps_ids=body.deps_ids,
        unsigned_params=body.unsigned_params,
        private_params=body.private_params,
    )


@app.command()
def delete(embed_id: EmbedIDArg, *, datalens: DataLensClient) -> EmbedDeleted:
    """Delete an embed; its links stop working."""
    return datalens.embeds.delete(embed_id)
