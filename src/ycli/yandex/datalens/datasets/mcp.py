"""DataLens datasets FastMCP tools (read + write) — Depends DI, native error handling."""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.yandex.datalens.client import DataLensClient
from ycli.yandex.datalens.datasets.models import (
    DataFilter,
    DataParameter,
    Dataset,
    DatasetContent,
    DatasetData,
    DatasetOptions,
    DatasetUpdate,
    DatasetValidate,
    DataSort,
)
from ycli.yandex.datalens.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    OverBudget,
    datalens_client,
)
from ycli.yandex.models import Ack

mcp = FastMCP("datalens-datasets")

DatasetID = Annotated[str, Field(description="Dataset id.")]
InWorkbook = Annotated[str | None, Field(description="The workbook the dataset lies in.")]
MODELS = "ycli.yandex.datalens.datasets.models"


@mcp.tool(name="datasets_get", annotations={**RO, "title": "Get DataLens dataset"})
def get(
    dataset_id: DatasetID,
    workbook_id: InWorkbook = None,
    rev_id: Annotated[
        str | None, Field(description="The revision to read; the current one when left out.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Dataset:
    """One dataset by id: its sources, their joins and its fields.

    ``dataset.result_schema`` lists the fields with their guids, which ``datasets_data_get``
    takes as columns. A source or a field of a kind this server does not know comes as it is.
    """
    return client.datasets.get(dataset_id, workbook_id=workbook_id, rev_id=rev_id)


@mcp.tool(name="datasets_create", annotations={**WRITE, "title": "Create DataLens dataset"})
def create(
    dataset: Annotated[
        DatasetContent,
        OverBudget(
            f"{MODELS}:DatasetContent",
            "What the dataset holds: sources, their joins, fields. An empty one is valid.",
        ),
    ],
    collection_id: Annotated[
        str | None, Field(description="The collection to create it in.")
    ] = None,
    created_via: Annotated[
        str | None, Field(description="How it is created: `user` or `workbook_copy`.")
    ] = None,
    dir_path: Annotated[
        str | None, Field(description="The folder to create it in (old placement model).")
    ] = None,
    name: Annotated[str | None, Field(description="The dataset's name.")] = None,
    options: Annotated[
        DatasetOptions | None, Field(description="What the editor may do with it.")
    ] = None,
    preview: Annotated[bool | None, Field(description="Whether it is a preview.")] = None,
    published_id: Annotated[str | None, Field(description="The published revision.")] = None,
    rev_id: Annotated[str | None, Field(description="The revision.")] = None,
    saved_id: Annotated[str | None, Field(description="The saved revision.")] = None,
    workbook_id: Annotated[str | None, Field(description="The workbook to create it in.")] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Dataset:
    """Create a dataset in a workbook and return it with its id.

    A dataset with no source and no field is valid: create it empty, then fill it with
    ``datasets_update``.
    """
    return client.datasets.create(
        dataset,
        collection_id=collection_id,
        created_via=created_via,
        dir_path=dir_path,
        name=name,
        options=options,
        preview=preview,
        published_id=published_id,
        rev_id=rev_id,
        saved_id=saved_id,
        workbook_id=workbook_id,
    )


@mcp.tool(
    name="datasets_update", annotations={**WRITE_IDEMPOTENT, "title": "Update DataLens dataset"}
)
def update(
    dataset_id: DatasetID,
    data: Annotated[
        DatasetUpdate,
        OverBudget(
            f"{MODELS}:DatasetUpdate",
            "The content to save (`dataset`) and how (`mode`: `save` or `publish`).",
        ),
    ],
    workbook_id: InWorkbook = None,
    client: DataLensClient = Depends(datalens_client),
) -> Dataset:
    """Save a dataset as given: read it, change what it holds, send it back whole.

    ``data.dataset`` replaces the content. Check a change first with ``datasets_validate``.
    Read the dataset again after every save: content of an older revision is refused.
    The reply holds the content and the revisions; its ``id`` is ``null`` (measured).
    """
    return client.datasets.update(dataset_id, data=data, workbook_id=workbook_id)


@mcp.tool(name="datasets_delete", annotations={**DESTRUCTIVE, "title": "Delete DataLens dataset"})
def delete(dataset_id: DatasetID, client: DataLensClient = Depends(datalens_client)) -> Ack:
    """Delete a dataset; the charts built on it lose their data.

    The API has no way to bring it back, and a chart built on it keeps naming its id (measured).
    """
    client.datasets.delete(dataset_id)
    return Ack.deleted("dataset", dataset_id)


@mcp.tool(name="datasets_validate", annotations={**RO, "title": "Validate DataLens dataset"})
def validate(
    dataset_id: DatasetID,
    data: Annotated[
        DatasetValidate,
        OverBudget(
            f"{MODELS}:DatasetValidate",
            "The content to check (`dataset`) and the changes to try on it (`updates`).",
        ),
    ],
    workbook_id: InWorkbook = None,
    binded_dataset_id: Annotated[
        str | None, Field(description="A dataset bound to this one.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> Dataset:
    """Check a dataset, or changes to it, without saving anything.

    The reply is the dataset as it would be, with ``code``, ``message`` and ``dataset_errors``.
    Give the content as last read: after a save, content of an older revision is refused.
    """
    return client.datasets.validate(
        dataset_id, workbook_id=workbook_id, binded_dataset_id=binded_dataset_id, data=data
    )


@mcp.tool(name="datasets_data_get", annotations={**RO, "title": "Read rows of a DataLens dataset"})
def data_get(
    dataset_id: DatasetID,
    columns: Annotated[
        list[str],
        Field(description="The guids of the fields to return (`dataset.result_schema[].guid`)."),
    ],
    workbook_id: InWorkbook = None,
    filters: Annotated[
        list[DataFilter] | None,
        Field(description="The rows to keep: a field's guid, an operation and its values."),
    ] = None,
    params: Annotated[
        list[DataParameter] | None, Field(description="Values for the dataset's parameters.")
    ] = None,
    sort: Annotated[
        list[DataSort] | None,
        Field(description="The order of the rows: a field's guid and `asc` or `desc`."),
    ] = None,
    limit: Annotated[
        int | None, Field(description="The most rows to return; 100 when left out.")
    ] = None,
    offset: Annotated[
        int | None, Field(description="How many rows to skip; above zero it needs `sort`.")
    ] = None,
    client: DataLensClient = Depends(datalens_client),
) -> DatasetData:
    """Rows of a dataset: the columns asked for, one page per call.

    Columns are named by the guid of a field, not by its title: read them with
    ``datasets_get``. For the next page give ``offset`` together with ``sort``.
    """
    return client.datasets.data_get(
        dataset_id,
        columns=columns,
        workbook_id=workbook_id,
        filters=filters,
        params=params,
        sort=sort,
        limit=limit,
        offset=offset,
    )
