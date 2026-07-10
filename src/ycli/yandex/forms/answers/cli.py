"""`forms answers` commands (reads + the async export action; export is CLI/SDK only)."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Annotated

import typer

from ycli.cli.binary import write_output
from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.yandex.forms.answers.models import AnswerExport
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)
from ycli.yandex.polling import poll

if TYPE_CHECKING:
    from ycli.yandex.forms.answers.models import ExportResult

app = typer.Typer(name="answers", help="Forms answers.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command("list")
def list_(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    limit: Annotated[int, typer.Option(help="Max responses (auto-paginates).")] = 0,
    all_: Annotated[bool, typer.Option("--all", help="Fetch every response (no cap).")] = False,
) -> None:
    """List a form's responses (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = None if all_ else (limit or app_ctx.config.max_items)
    Serializer.serialize(
        app_ctx.forms.answers.list_all(survey_id, limit=cap), app_ctx.strategy, app_ctx.console
    )


def _finish_export(
    app_ctx: AppContext, survey_id: str, op: ExportResult, wait: bool, output: str | None
) -> None:
    """Print the export operation, or (``--wait``) poll it to a terminal state and save the file.

    ``--no-wait`` prints the just-started ``{id, status}`` so the caller can poll later with
    ``operations get`` / ``answers export-results``. ``--wait`` polls the export-results status
    via :func:`ycli.yandex.polling.poll` until terminal; on success it downloads the exported
    file to ``--output`` (or stdout), otherwise it prints the failed status.
    """
    if not (wait and op.id):
        Serializer.serialize(op, app_ctx.strategy, app_ctx.console)
        return
    task_id = op.id  # narrowed to str — the poll re-reads this operation's status
    final = poll(
        lambda: app_ctx.forms.answers.export_results(survey_id, task_id),
        lambda result: result.is_terminal,
        sleep=lambda seconds: time.sleep(seconds),
    )
    if final.is_ready:
        write_output(app_ctx.forms.answers.download_export(survey_id, task_id), output)
    else:
        Serializer.serialize(final, app_ctx.strategy, app_ctx.console)


@app.command()
def export(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    export_format: Annotated[
        str, typer.Option("--format", help="Export format: csv or xlsx.")
    ] = "xlsx",
    upload: Annotated[
        str, typer.Option(help="Where to upload the result: default or disk (Yandex Disk).")
    ] = "default",
    started_at: Annotated[
        str, typer.Option(help="ISO-8601 start of the answer range (inclusive).")
    ] = "",
    finished_at: Annotated[
        str, typer.Option(help="ISO-8601 end of the answer range (inclusive).")
    ] = "",
    limit: Annotated[int, typer.Option(help="Max answers to export (0 = all).")] = 0,
    column: Annotated[
        list[str] | None,
        typer.Option("--column", help="Column/question slug to include (repeatable)."),
    ] = None,
    pk: Annotated[
        list[int] | None, typer.Option("--pk", help="Answer id to include (repeatable).")
    ] = None,
    upload_files: Annotated[
        bool | None,
        typer.Option(
            "--upload-files/--no-upload-files", help="Also export uploaded files to Disk."
        ),
    ] = None,
    wait: Annotated[
        bool, typer.Option("--wait/--no-wait", help="Poll to a terminal status, then download.")
    ] = True,
    output: Annotated[
        str | None,
        typer.Option(
            "--output", help="Write the exported file here; omit / '-' streams to stdout."
        ),
    ] = None,
) -> None:
    """Export a form's answers (POST /answers/export) — async; --wait downloads the file."""
    body = AnswerExport(
        format=export_format,
        upload=upload,
        started_at=started_at or None,
        finished_at=finished_at or None,
        pks=pk or None,
        columns=column or None,
        limit=limit or None,
        upload_files=upload_files,
    ).model_dump(exclude_none=True)
    app_ctx = AppContext.from_typer_context(ctx)
    op = app_ctx.forms.answers.export(survey_id, body=body)
    _finish_export(app_ctx, survey_id, op, wait, output)
