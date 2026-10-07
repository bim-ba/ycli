"""`datalens htmlpages` commands."""

import json
from collections.abc import Mapping
from typing import Annotated

import typer
from pydantic import BaseModel

from ycli.cli.body_fields import CallerFields
from ycli.cli.typedefs import values_option
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.htmlpages.models import (
    HTMLPage,
    HTMLPageCreated,
    HTMLPagePreview,
    HTMLPageSaved,
    HTMLPageUpdate,
    PreviewLanguage,
    PreviewTheme,
)
from ycli.yandex.datalens.models import RevisionBranch, SaveMode
from ycli.yandex.datalens.schemas.html_pages import CreateHtmlPageArgs
from ycli.yandex.datalens.typedefs import EntryIDArg
from ycli.yandex.models import Ack

app = typer.Typer(name="htmlpages", help="DataLens HTML pages.", no_args_is_help=True)

ContentOption = Annotated[
    str | None,
    typer.Option("--content", help="The HTML of the page; --body-file gives it under `content`."),
]
PageNoteOption = Annotated[
    str | None,
    typer.Option("--annotation", help='A description of the page, as JSON: {"description": "…"}.'),
]
PageBranchOption = Annotated[
    str | None,
    values_option(
        RevisionBranch,
        "--branch",
        help="The version to read when no revision is named: saved or published.",
    ),
]
PageRevisionOption = Annotated[
    str | None,
    typer.Option("--rev-id", help="One revision, as it is; give it or --branch, not both."),
]


def _body[M: BaseModel](model: type[M], caller: CallerFields, flags: Mapping[str, str | None]) -> M:
    """The request as ``model``: the flags given, over -F, over --body-file.

    A flag is given under the API's name of its field; ``annotation`` is JSON. The file and
    ``-F`` give the request itself, and a field that is not of it is refused, not dropped.
    """
    given = {
        name: json.loads(value) if name == "annotation" else value
        for name, value in flags.items()
        if value is not None
    }
    return model.model_validate(caller.over(given))


@app.command()
def get(
    entry_id: EntryIDArg,
    rev_id: PageRevisionOption = None,
    branch: PageBranchOption = None,
    include_permissions: Annotated[
        bool | None,
        typer.Option(
            "--include-permissions/--no-include-permissions",
            help="Also say what you may do with the page.",
        ),
    ] = None,
    include_favorite: Annotated[
        bool | None,
        typer.Option(
            "--include-favorite/--no-include-favorite",
            help="Also say whether the page is a favourite.",
        ),
    ] = None,
    *,
    datalens: DataLensClient,
) -> HTMLPage:
    """Print one HTML page: where it lies and its revisions (its HTML is not in the reply)."""
    return datalens.htmlpages.get(
        entry_id,
        rev_id=rev_id,
        branch=branch,
        include_permissions=include_permissions,
        include_favorite=include_favorite,
    )


@app.command()
def create(
    content: ContentOption = None,
    annotation: PageNoteOption = None,
    key: Annotated[str | None, typer.Option("--key", help="The page's key, in a folder.")] = None,
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook to create the page in.")
    ] = None,
    name: Annotated[str | None, typer.Option("--name", help="The page's name.")] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> HTMLPageCreated:
    """Create an HTML page; `content` is required, from --content or --body-file."""
    flags = {
        "content": content,
        "annotation": annotation,
        "key": key,
        "workbookId": workbook_id,
        "name": name,
    }
    body = _body(CreateHtmlPageArgs, caller, flags)
    return datalens.htmlpages.create(
        content=body.content,
        annotation=body.annotation,
        key=body.key,
        workbook_id=body.workbook_id,
        name=body.name,
    )


@app.command()
def update(
    entry_id: EntryIDArg,
    mode: Annotated[
        str | None,
        values_option(SaveMode, "--mode", help="Keep it as a draft, or show it to everyone."),
    ] = None,
    content: ContentOption = None,
    rev_id: Annotated[
        str | None,
        typer.Option("--rev-id", help="A revision to make current, in place of new content."),
    ] = None,
    annotation: PageNoteOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> HTMLPageSaved:
    """Save new HTML (--content), or make a revision the current one (--rev-id with --mode).

    Give one of the two, not both. With --rev-id, `--mode publish` shows that revision to
    everyone and `--mode save` copies it as the current draft.
    """
    flags = {
        "entryId": entry_id,
        "mode": mode,
        "content": content,
        "revId": rev_id,
        "annotation": annotation,
    }
    return datalens.htmlpages.update(_body(HTMLPageUpdate, caller, flags))


@app.command()
def delete(entry_id: EntryIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete an HTML page."""
    datalens.htmlpages.delete(entry_id)
    return Ack.deleted("HTML page", entry_id)


@app.command("preview-url-get")
def preview_url_get(
    entry_id: EntryIDArg,
    branch: PageBranchOption = None,
    rev_id: PageRevisionOption = None,
    lang: Annotated[
        str | None, values_option(PreviewLanguage, "--lang", help="Language of the preview.")
    ] = None,
    theme: Annotated[
        str | None, values_option(PreviewTheme, "--theme", help="Theme of the preview.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> HTMLPagePreview:
    """Print a temporary signed link that shows the page."""
    return datalens.htmlpages.preview_url_get(
        entry_id, branch=branch, rev_id=rev_id, lang=lang, theme=theme
    )
