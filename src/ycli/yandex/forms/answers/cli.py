"""`forms answers` commands (reads, delete and restore, and the async export action)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.cli.progress import wait_for
from ycli.cli.typedefs import AllOption, LimitOption, values_option
from ycli.settings import AppConfig
from ycli.yandex.forms.answers.models import (
    AnswerDetails,
    AnswerExport,
    AnswerFormat,
    AnswerIntegration,
    AnswersResponse,
    ExportFormat,
    ExportUpload,
)
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.models import OperationResult
from ycli.yandex.forms.typedefs import AnswerIDArg, SurveyIDArg
from ycli.yandex.models import Ack, ItemList, SortDirection

app = typer.Typer(name="answers", help="Forms answers.", no_args_is_help=True)


@app.command()
def get(
    answer_id: Annotated[
        int | None,
        typer.Option("--answer-id", help="Numeric answer id (needs form-edit access)."),
    ] = None,
    answer_key: Annotated[
        str | None,
        typer.Option("--answer-key", help="Answer key hash (works without form-edit access)."),
    ] = None,
    *,
    forms: FormsClient,
) -> AnswerDetails:
    """Fetch one answer (GET /answers). The API takes one of --answer-id / --answer-key.

    The single-answer read is a flat query-param route, so no survey id is needed.
    """
    return forms.answers.get(answer_id=answer_id, answer_key=answer_key)


@app.command("list")
def list_(
    survey_id: SurveyIDArg,
    limit: LimitOption = None,
    all_: AllOption = False,
    questions: Annotated[
        str | None, typer.Option(help="Comma-separated question ids to return answers for.")
    ] = None,
    use_slugs: Annotated[
        bool, typer.Option("--use-slugs", help="Name questions and options by slug, not id.")
    ] = False,
    date_from: Annotated[
        str | None, typer.Option(help="ISO-8601: answers given at or after.")
    ] = None,
    date_to: Annotated[
        str | None, typer.Option(help="ISO-8601: answers given at or before.")
    ] = None,
    ordering: Annotated[
        str | None, values_option(SortDirection, help="asc is oldest first; the default is desc.")
    ] = None,
    page_size: Annotated[
        int | None, typer.Option(help="Answers per request (the API's default is 25).")
    ] = None,
    answer_format: Annotated[
        str | None,
        values_option(
            AnswerFormat, "--answer-format", help="default is cells by column, raw is as stored."
        ),
    ] = None,
    *,
    config: AppConfig,
    forms: FormsClient,
) -> AnswersResponse:
    """List a form's responses, filtered (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return forms.answers.list(
        survey_id,
        limit=cap,
        questions=questions,
        use_slugs=use_slugs,
        date_from=date_from,
        date_to=date_to,
        ordering=ordering,
        page_size=page_size,
        answer_format=answer_format,
    )


def _finish_export(
    forms: FormsClient,
    config: AppConfig,
    survey_id: str,
    op: OperationResult,
    wait: bool,
    output: str | None,
) -> OperationResult | BinaryResult:
    """The export operation, or (``--wait``) poll it to a terminal state and return the file.

    ``--no-wait`` prints the just-started ``{id, status}`` so the caller can poll later with
    ``operations get`` / ``answers export-results``. ``--wait`` polls the export-results status
    via :func:`ycli.cli.progress.wait_for` (stderr spinner on a terminal) until terminal; on
    success it downloads the exported file to ``--output`` (or stdout), otherwise it prints the
    failed status.
    """
    if not (wait and op.id):
        return op
    task_id = op.id  # narrowed to str — the poll re-reads this operation's status
    final = wait_for(
        lambda: forms.answers.export_results(survey_id, task_id),
        lambda result: result.is_terminal,
        message="Waiting for answers export…",
        max_wait_seconds=config.http.max_wait_seconds,
    )
    if final.is_ready:
        return BinaryResult(forms.answers.download_export(survey_id, task_id), output)
    return final


@app.command()
def export(
    survey_id: SurveyIDArg,
    export_format: Annotated[
        str, values_option(ExportFormat, "--format", help="Export format.")
    ] = "xlsx",
    upload: Annotated[
        str, values_option(ExportUpload, help="Where the result goes; disk is Yandex Disk.")
    ] = "default",
    started_at: Annotated[
        str | None, typer.Option(help="ISO-8601 start of the answer range (inclusive).")
    ] = None,
    finished_at: Annotated[
        str | None, typer.Option(help="ISO-8601 end of the answer range (inclusive).")
    ] = None,
    limit: Annotated[int | None, typer.Option(help="Max answers to export (default: all).")] = None,
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
    *,
    config: AppConfig,
    forms: FormsClient,
) -> OperationResult | BinaryResult:
    """Export a form's answers (POST /answers/export) — async; --wait downloads the file."""
    body = AnswerExport(
        format=export_format,
        upload=upload,
        started_at=started_at,
        finished_at=finished_at,
        pks=pk or None,
        columns=column or None,
        limit=limit,
        upload_files=upload_files,
    )
    op = forms.answers.export(survey_id, body=body)
    return _finish_export(forms, config, survey_id, op, wait, output)


@app.command()
def integrations_list(
    answer_id: Annotated[
        int | None,
        typer.Option("--answer-id", help="Numeric answer id (needs form-edit access)."),
    ] = None,
    answer_key: Annotated[
        str | None,
        typer.Option("--answer-key", help="Answer key hash (works without form-edit access)."),
    ] = None,
    *,
    forms: FormsClient,
) -> ItemList[AnswerIntegration]:
    """List the integration runs an answer triggered (one of --answer-id / --answer-key)."""
    return forms.answers.integrations_list(answer_id=answer_id, answer_key=answer_key)


@app.command()
def delete(survey_id: SurveyIDArg, answer_id: AnswerIDArg, *, forms: FormsClient) -> Ack:
    """Delete an answer (DELETE /surveys/{id}/answers/{answer_id}); `answers restore` undoes it."""
    forms.answers.delete(survey_id, answer_id)
    return Ack.deleted("answer", answer_id, from_=f"survey {survey_id}")


@app.command()
def restore(survey_id: SurveyIDArg, answer_id: AnswerIDArg, *, forms: FormsClient) -> Ack:
    """Bring a deleted answer back (POST /surveys/{id}/answers/{answer_id}/restore)."""
    forms.answers.restore(survey_id, answer_id)
    return Ack.restored("answer", answer_id, in_=f"survey {survey_id}")
