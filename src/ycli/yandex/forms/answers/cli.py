"""`forms answers` commands (reads, delete and restore, and the async export action)."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.output import BinaryResult
from ycli.cli.progress import wait_for
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.forms.answers.models import (
    AnswerDetails,
    AnswerExport,
    AnswerIntegration,
    AnswersResponse,
)
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.models import OperationResult
from ycli.yandex.forms.typedefs import AnswerIdArg, SurveyIdArg
from ycli.yandex.models import Ack, ItemList

app = typer.Typer(name="answers", help="Forms answers.", no_args_is_help=True)


@app.command()
def get(
    answer_id: Annotated[
        int,
        typer.Option("--answer-id", help="Numeric answer id (needs form-edit access; 0 = unset)."),
    ] = 0,
    answer_key: Annotated[
        str,
        typer.Option("--answer-key", help="Answer key hash (works without form-edit access)."),
    ] = "",
    *,
    forms: FormsClient,
) -> AnswerDetails:
    """Fetch one answer (GET /answers). Pass exactly one of --answer-id / --answer-key.

    The single-answer read is a flat query-param route, so no survey id is needed.
    """
    if bool(answer_id) == bool(answer_key):
        raise typer.BadParameter("pass exactly one of --answer-id / --answer-key")
    return forms.answers.get(answer_id=answer_id or None, answer_key=answer_key or None)


@app.command("list")
def list_(
    survey_id: SurveyIdArg,
    limit: LimitOption = 0,
    all_: AllOption = False,
    *,
    config: AppConfig,
    forms: FormsClient,
) -> AnswersResponse:
    """List a form's responses (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return forms.answers.list_all(survey_id, limit=cap)


def _finish_export(
    forms: FormsClient, survey_id: str, op: OperationResult, wait: bool, output: str | None
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
    )
    if final.is_ready:
        return BinaryResult(forms.answers.download_export(survey_id, task_id), output)
    return final


@app.command()
def export(
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
    *,
    forms: FormsClient,
) -> OperationResult | BinaryResult:
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
    op = forms.answers.export(survey_id, body=body)
    return _finish_export(forms, survey_id, op, wait, output)


@app.command()
def integrations_list(
    answer_id: Annotated[
        int,
        typer.Option("--answer-id", help="Numeric answer id (needs form-edit access; 0 = unset)."),
    ] = 0,
    answer_key: Annotated[
        str,
        typer.Option("--answer-key", help="Answer key hash (works without form-edit access)."),
    ] = "",
    *,
    forms: FormsClient,
) -> ItemList[AnswerIntegration]:
    """List the integration runs an answer triggered (exactly one of --answer-id / --answer-key)."""
    if bool(answer_id) == bool(answer_key):
        raise typer.BadParameter("pass exactly one of --answer-id / --answer-key")
    return forms.answers.integrations_list(
        answer_id=answer_id or None, answer_key=answer_key or None
    )


@app.command()
def delete(survey_id: SurveyIdArg, answer_id: AnswerIdArg, *, forms: FormsClient) -> Ack:
    """Delete an answer (DELETE /surveys/{id}/answers/{answer_id}); `answers restore` undoes it."""
    forms.answers.delete(survey_id, answer_id)
    return Ack.deleted("answer", answer_id, from_=f"survey {survey_id}")


@app.command()
def restore(survey_id: SurveyIdArg, answer_id: AnswerIdArg, *, forms: FormsClient) -> Ack:
    """Bring a deleted answer back (POST /surveys/{id}/answers/{answer_id}/restore)."""
    forms.answers.restore(survey_id, answer_id)
    return Ack.restored("answer", answer_id, in_=f"survey {survey_id}")
