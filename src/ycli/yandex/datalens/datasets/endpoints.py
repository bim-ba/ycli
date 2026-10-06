"""DataLens dataset operations, declared once (sans-IO).

Examples:
    >>> get("ds1", workbook_id=None, rev_id=None).body
    {'datasetId': 'ds1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
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
from ycli.yandex.datalens.schemas.data import GetDatasetDataRequest
from ycli.yandex.datalens.schemas.dataset import (
    DatasetCreate,
    DeleteDatasetRequest,
    GetDatasetRequest,
    UpdateDatasetRequest,
    ValidateDatasetRequest,
)


def get(dataset_id: str, *, workbook_id: str | None, rev_id: str | None) -> Endpoint[Dataset]:
    body = GetDatasetRequest(datasetId=dataset_id, workbookId=workbook_id, rev_id=rev_id)
    return RPC("getDataset", Dataset, json=body, effect=Effect.READ)


def create(
    dataset: DatasetContent,
    *,
    collection_id: str | None,
    created_via: str | None,
    dir_path: str | None,
    name: str | None,
    options: DatasetOptions | None,
    preview: bool | None,
    published_id: str | None,
    rev_id: str | None,
    saved_id: str | None,
    workbook_id: str | None,
) -> Endpoint[Dataset]:
    body = DatasetCreate(
        dataset=dataset,
        collection_id=collection_id,
        created_via=created_via,
        dir_path=dir_path,
        name=name,
        options=options,
        preview=preview,
        publishedId=published_id,
        revId=rev_id,
        savedId=saved_id,
        workbook_id=workbook_id,
    )
    return RPC("createDataset", Dataset, json=body, effect=Effect.WRITE)


def update(dataset_id: str, *, data: DatasetUpdate, workbook_id: str | None) -> Endpoint[Dataset]:
    body = UpdateDatasetRequest(datasetId=dataset_id, data=data, workbookId=workbook_id)
    return RPC("updateDataset", Dataset, json=body, effect=Effect.IDEMPOTENT_WRITE)


def delete(dataset_id: str) -> Endpoint[None]:
    # The document describes no reply; as with a connection, none is read.
    body = DeleteDatasetRequest(datasetId=dataset_id)
    return RPC("deleteDataset", json=body, effect=Effect.DESTRUCTIVE)


def validate(
    dataset_id: str,
    *,
    data: DatasetValidate,
    workbook_id: str | None,
    binded_dataset_id: str | None,
) -> Endpoint[Dataset]:
    body = ValidateDatasetRequest(
        datasetId=dataset_id, workbookId=workbook_id, bindedDatasetId=binded_dataset_id, data=data
    )
    # It changes nothing: the dataset given is checked and answered back, not saved.
    return RPC("validateDataset", Dataset, json=body, effect=Effect.READ)


def data_get(
    dataset_id: str,
    *,
    columns: Sequence[str],
    workbook_id: str | None,
    filters: Sequence[DataFilter] | None,
    params: Sequence[DataParameter] | None,
    sort: Sequence[DataSort] | None,
    limit: int | None,
    offset: int | None,
) -> Endpoint[DatasetData]:
    body = GetDatasetDataRequest(
        datasetId=dataset_id,
        workbookId=workbook_id,
        columns=list(columns),
        filters=None if filters is None else list(filters),
        params=None if params is None else list(params),
        sort=None if sort is None else list(sort),
        limit=limit,
        offset=offset,
    )
    return RPC("getDatasetData", DatasetData, json=body, effect=Effect.READ)
