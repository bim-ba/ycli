"""`datalens datasets` commands."""

import json
from typing import Annotated

import typer
from pydantic import BaseModel

from ycli.cli.body_fields import CallerFields
from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.datasets.models import (
    DataFilter,
    DataParameter,
    Dataset,
    DatasetData,
    DatasetUpdate,
    DatasetValidate,
    DataSort,
)
from ycli.yandex.datalens.schemas.dataset import (
    DatasetCreate,
    UpdateDatasetRequest,
    ValidateDatasetRequest,
)
from ycli.yandex.models import Ack

app = typer.Typer(name="datasets", help="DataLens datasets.", no_args_is_help=True)

DatasetIDArg = Annotated[str, typer.Argument(metavar="DATASET_ID", help="Dataset id.")]
WorkbookOption = Annotated[
    str | None, typer.Option("--workbook-id", help="The workbook the dataset lies in.")
]


def _request[E: BaseModel, M: BaseModel](
    envelope: type[E], data: type[M], flags: dict[str, str | None], caller: CallerFields
) -> tuple[E, M]:
    """The request as ``envelope`` and its ``data``: the flags given, over -F, over --body-file.

    A flag is given under the API's name of its field, ``data`` as JSON. The file and ``-F``
    give the request itself, so ``workbookId`` in a file reaches it like ``--workbook-id``.
    ``data`` is asked for by itself: the specification leaves it optional, a save does not.
    """
    given = {
        name: json.loads(value) if name == "data" else value
        for name, value in flags.items()
        if value is not None
    }
    merged = caller.over(given)
    return envelope.model_validate(merged), data.model_validate(merged.get("data"))


@app.command()
def get(
    dataset_id: DatasetIDArg,
    workbook_id: WorkbookOption = None,
    rev_id: Annotated[
        str | None, typer.Option("--rev-id", help="The revision to read; the current by default.")
    ] = None,
    *,
    datalens: DataLensClient,
) -> Dataset:
    """Print one dataset: its sources, their joins and its fields with their guids."""
    return datalens.datasets.get(dataset_id, workbook_id=workbook_id, rev_id=rev_id)


@app.command()
def create(
    dataset: Annotated[
        str | None,
        typer.Option(
            "--dataset",
            help="What the dataset holds, as a JSON object; --body-file gives it under "
            '`dataset`. An empty one is valid: {"sources": [], "result_schema": []}.',
        ),
    ] = None,
    collection_id: Annotated[
        str | None, typer.Option("--collection-id", help="The collection to create it in.")
    ] = None,
    created_via: Annotated[
        str | None,
        typer.Option("--created-via", help="How it is created: user or workbook_copy."),
    ] = None,
    dir_path: Annotated[
        str | None,
        typer.Option("--dir-path", help="The folder to create it in (old placement model)."),
    ] = None,
    name: Annotated[str | None, typer.Option("--name", help="The dataset's name.")] = None,
    options: Annotated[
        str | None,
        typer.Option("--options", help="What the editor may do with it, as a JSON object."),
    ] = None,
    preview: Annotated[
        bool | None, typer.Option("--preview/--no-preview", help="Whether it is a preview.")
    ] = None,
    published_id: Annotated[
        str | None, typer.Option("--published-id", help="The published revision.")
    ] = None,
    rev_id: Annotated[str | None, typer.Option("--rev-id", help="The revision.")] = None,
    saved_id: Annotated[str | None, typer.Option("--saved-id", help="The saved revision.")] = None,
    workbook_id: Annotated[
        str | None, typer.Option("--workbook-id", help="The workbook to create it in.")
    ] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> Dataset:
    """Create a dataset; with no source and no field it is empty, to be filled by `update`."""
    given = {
        "dataset": None if dataset is None else json.loads(dataset),
        "collection_id": collection_id,
        "created_via": created_via,
        "dir_path": dir_path,
        "name": name,
        "options": None if options is None else json.loads(options),
        "preview": preview,
        "publishedId": published_id,
        "revId": rev_id,
        "savedId": saved_id,
        "workbook_id": workbook_id,
    }
    # `dataset` is required and usually comes from --body-file: merge before the model is built.
    flags = {key: value for key, value in given.items() if value is not None}
    body = DatasetCreate.model_validate(caller.over(flags))
    return datalens.datasets.create(
        body.dataset,
        collection_id=body.collection_id,
        created_via=body.created_via,
        dir_path=body.dir_path,
        name=body.name,
        options=body.options,
        preview=body.preview,
        published_id=body.published_id,
        rev_id=body.rev_id,
        saved_id=body.saved_id,
        workbook_id=body.workbook_id,
    )


@app.command()
def update(
    dataset_id: DatasetIDArg,
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            help='What to save, as a JSON object: {"dataset": {...}, "mode": "save"}. '
            "--body-file gives it under `data`.",
        ),
    ] = None,
    workbook_id: WorkbookOption = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> Dataset:
    """Save a dataset as given: read it, change what it holds, send it back whole.

    The reply holds the content and the revisions; its `id` is `null` (measured).
    """
    flags = {"datasetId": dataset_id, "data": data, "workbookId": workbook_id}
    body, given = _request(UpdateDatasetRequest, DatasetUpdate, flags, caller)
    return datalens.datasets.update(body.dataset_id, data=given, workbook_id=body.workbook_id)


@app.command()
def delete(dataset_id: DatasetIDArg, *, datalens: DataLensClient) -> Ack:
    """Delete a dataset; the charts built on it lose their data.

    The API has no way to bring it back, and a chart built on it keeps naming its id (measured).

    The interface lists what was deleted under Service settings, Deleted objects, with a
    Restore button (measured: the entry appears there; restoring was not tried).
    """
    datalens.datasets.delete(dataset_id)
    return Ack.deleted("dataset", dataset_id)


@app.command()
def validate(
    dataset_id: DatasetIDArg,
    workbook_id: WorkbookOption = None,
    binded_dataset_id: Annotated[
        str | None, typer.Option("--binded-dataset-id", help="A dataset bound to this one.")
    ] = None,
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            help='What to check, as a JSON object: {"dataset": {...}, "updates": [...]}. '
            "--body-file gives it under `data`.",
        ),
    ] = None,
    *,
    caller: CallerFields,
    datalens: DataLensClient,
) -> Dataset:
    """Check a dataset, or changes to it, without saving anything."""
    flags = {
        "datasetId": dataset_id,
        "data": data,
        "workbookId": workbook_id,
        "bindedDatasetId": binded_dataset_id,
    }
    body, given = _request(ValidateDatasetRequest, DatasetValidate, flags, caller)
    return datalens.datasets.validate(
        body.dataset_id,
        data=given,
        workbook_id=body.workbook_id,
        binded_dataset_id=body.binded_dataset_id,
    )


@app.command("data-get")
def data_get(
    dataset_id: DatasetIDArg,
    columns: Annotated[
        list[str],
        typer.Option(
            "--columns", help="The guid of a field to return, as `get` lists them (repeatable)."
        ),
    ],
    workbook_id: WorkbookOption = None,
    filters: Annotated[
        list[str] | None,
        typer.Option(
            "--filters",
            help='A filter, as a JSON object: {"guid": "...", "operation": "eq", '
            '"values": ["x"]} (repeatable).',
        ),
    ] = None,
    params: Annotated[
        list[str] | None,
        typer.Option(
            "--params",
            help='A value of a parameter, as a JSON object: {"guid": "...", "value": 1} '
            "(repeatable).",
        ),
    ] = None,
    sort: Annotated[
        list[str] | None,
        typer.Option(
            "--sort",
            help='A sorting rule, as a JSON object: {"guid": "...", "direction": "asc"} '
            "(repeatable).",
        ),
    ] = None,
    limit: Annotated[
        int | None, typer.Option("--limit", help="The most rows to return; 100 by default.")
    ] = None,
    offset: Annotated[
        int | None,
        typer.Option("--offset", help="How many rows to skip; above zero it needs --sort."),
    ] = None,
    *,
    datalens: DataLensClient,
) -> DatasetData:
    """Print rows of a dataset: the columns asked for, one page per call."""
    return datalens.datasets.data_get(
        dataset_id,
        columns=columns,
        workbook_id=workbook_id,
        filters=None if filters is None else [DataFilter.model_validate_json(f) for f in filters],
        params=None if params is None else [DataParameter.model_validate_json(p) for p in params],
        sort=None if sort is None else [DataSort.model_validate_json(s) for s in sort],
        limit=limit,
        offset=offset,
    )
