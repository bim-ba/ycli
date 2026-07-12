"""`forms answers` commands (reads + the async export action; export is CLI/SDK only)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import typer

from ycli.cli.binary import write_output
from ycli.cli.context import AppContext
from ycli.cli.output import Serializer
from ycli.cli.progress import wait_for
from ycli.cli.typedefs import AllOption, LimitOption  # noqa: TC001
from ycli.yandex.forms.answers.models import AnswerExport
from ycli.yandex.forms.typedefs import (
    SurveyIdArg,  # noqa: TC001  # typer evaluates Annotated args at runtime via get_type_hints()
)
from ycli.yandex.pagination import resolve_cap

if TYPE_CHECKING:
    from ycli.yandex.forms.answers.models import ExportResult

app = typer.Typer(name="answers", help="Forms answers.", no_args_is_help=True)


@app.callback()
def _group() -> None:
    """Group anchor — forces subcommand dispatch (no eager DI, so --help stays cred-free)."""


@app.command()
def get(
    ctx: typer.Context,
    answer_id: Annotated[
        int,
        typer.Option("--answer-id", help="Numeric answer id (needs form-edit access; 0 = unset)."),
    ] = 0,
    answer_key: Annotated[
        str,
        typer.Option("--answer-key", help="Answer key hash (works without form-edit access)."),
    ] = "",
) -> None:
    """Fetch one answer (GET /answers). Pass exactly one of --answer-id / --answer-key.

    The single-answer read is a flat query-param route, so no survey id is needed.
    """
    if bool(answer_id) == bool(answer_key):
        raise typer.BadParameter("pass exactly one of --answer-id / --answer-key")
    app_ctx = AppContext.from_typer_context(ctx)
    Serializer.serialize(
        app_ctx.forms.answers.get(answer_id=answer_id or None, answer_key=answer_key or None),
        app_ctx.strategy,
        app_ctx.console,
    )


@app.command("list")
def list_(
    ctx: typer.Context,
    survey_id: SurveyIdArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
) -> None:
    """List a form's responses (auto-paginated; --all for everything)."""
    app_ctx = AppContext.from_typer_context(ctx)
    cap = resolve_cap(limit, app_ctx.config.max_items, all_=all_)
    Serializer.serialize(
        app_ctx.forms.answers.list_all(survey_id, limit=cap), app_ctx.strategy, app_ctx.console
    )


def _finish_export(
    app_ctx: AppContext, survey_id: str, op: ExportResult, wait: bool, output: str | None
) -> None:
    """Print the export operation, or (``--wait``) poll it to a terminal state and save the file.

    ``--no-wait`` prints the just-started ``{id, status}`` so the caller can poll later with
    ``operations get`` / ``answers export-results``. ``--wait`` polls the export-results status
    via :func:`ycli.cli.progress.wait_for` (stderr spinner on a terminal) until terminal; on
    success it downloads the exported file to ``--output`` (or stdout), otherwise it prints the
    failed status.
    """
    if not (wait and op.id):
        Serializer.serialize(op, app_ctx.strategy, app_ctx.console)
        return
    task_id = op.id  # narrowed to str — the poll re-reads this operation's status
    final = wait_for(
        lambda: app_ctx.forms.answers.export_results(survey_id, task_id),
        lambda result: result.is_terminal,
        message="Waiting for answers export…",
        console=app_ctx.stderr_console,
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
