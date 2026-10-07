"""DataLens datasets client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.datasets import endpoints

if TYPE_CHECKING:
    from collections.abc import Sequence

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


class DatasetsClient(Resource):
    """Datasets: the fields, sources and joins that charts read their data through."""

    def get(
        self, dataset_id: str, *, workbook_id: str | None = None, rev_id: str | None = None
    ) -> Dataset:
        """``getDataset`` → one dataset: its sources, their joins and its fields.

        A source, a field or an action of a kind this version of ycli does not know is kept as
        it came (``OtherKind…``), so the dataset can be changed and sent back whole.

        Args:
            dataset_id: The dataset's id.
            workbook_id: The workbook the dataset lies in.
            rev_id: The revision to read; the current one when left out.

        Returns:
            The dataset.

        Examples:
            >>> datalens.datasets.get("ds000000000001").name
            'Sales'
        """
        return self._session.send(endpoints.get(dataset_id, workbook_id=workbook_id, rev_id=rev_id))

    def create(
        self,
        dataset: DatasetContent,
        *,
        collection_id: str | None = None,
        created_via: str | None = None,
        dir_path: str | None = None,
        name: str | None = None,
        options: DatasetOptions | None = None,
        preview: bool | None = None,
        published_id: str | None = None,
        rev_id: str | None = None,
        saved_id: str | None = None,
        workbook_id: str | None = None,
    ) -> Dataset:
        """``createDataset`` — create a dataset → it, with its id.

        A dataset with no source and no field is a valid one: fill it with ``update``.

        Args:
            dataset: What the dataset holds: sources, their joins, fields, filters.
            collection_id: The collection to create it in.
            created_via: How it is created: ``user`` or ``workbook_copy``.
            dir_path: The folder to create it in, where the old placement model is used.
            name: The dataset's name.
            options: What the editor may do with it, as DataLens answers them.
            preview: Whether the dataset is a preview.
            published_id: The published revision.
            rev_id: The revision.
            saved_id: The saved revision.
            workbook_id: The workbook to create it in.

        Returns:
            The created dataset.

        Examples:
            >>> from ycli.yandex.datalens.datasets.models import DatasetContent
            >>> empty = DatasetContent.model_validate({"sources": [], "result_schema": []})
            >>> created = datalens.datasets.create(
            ...     empty, name="Sales", workbook_id="wb000000000001"
            ... )
            >>> created.id
            'ds000000000001'
        """
        return self._session.send(
            endpoints.create(
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
        )

    def update(
        self,
        dataset_id: str,
        *,
        data: DatasetUpdate,
        workbook_id: str | None = None,
    ) -> Dataset:
        """``updateDataset`` — save a dataset as given in ``data`` → what was saved.

        Read the dataset, change what it holds and send it back whole: ``data.dataset`` replaces
        the content. The reply holds the content and the revisions; its ``id`` is ``null``
        (measured). Read the dataset again after every save: content of an older revision is refused
        (``400 ERR.DS_API.DATASET_REVISION_MISMATCH``), by ``validate`` too.

        Args:
            dataset_id: The dataset's id.
            data: The content to save and how: ``mode`` is ``save`` or ``publish``.
            workbook_id: The workbook the dataset lies in.

        Returns:
            The dataset as saved.

        Examples:
            >>> from ycli.yandex.datalens.datasets.models import DatasetUpdate
            >>> change = DatasetUpdate.model_validate({"dataset": {"description": "Q1"}})
            >>> datalens.datasets.update("ds000000000001", data=change).rev_id
            'rev2'
        """
        return self._session.send(endpoints.update(dataset_id, data=data, workbook_id=workbook_id))

    def delete(self, dataset_id: str) -> None:
        """``deleteDataset`` — delete a dataset (``200``, empty body).

        The charts built on it lose their data.

        Args:
            dataset_id: The dataset's id.

        Examples:
            >>> datalens.datasets.delete("ds000000000001")
        """
        self._session.send(endpoints.delete(dataset_id))

    def validate(
        self,
        dataset_id: str,
        *,
        data: DatasetValidate,
        workbook_id: str | None = None,
        binded_dataset_id: str | None = None,
    ) -> Dataset:
        """``validateDataset`` → the dataset as it would be, with what is wrong in it.

        Nothing is saved. ``data.updates`` are the changes to try (add a field, a source), over
        ``data.dataset``; the reply says ``code`` and ``message`` and lists ``dataset_errors``.

        Args:
            dataset_id: The dataset's id.
            data: The content to check and the changes to try on it.
            workbook_id: The workbook the dataset lies in.
            binded_dataset_id: A dataset bound to this one.

        Returns:
            The checked dataset.

        Examples:
            >>> from ycli.yandex.datalens.datasets.models import DatasetValidate
            >>> tried = DatasetValidate.model_validate({"dataset": {"description": "Q1"}})
            >>> datalens.datasets.validate("ds000000000001", data=tried).model_dump()["code"]
            'OK'
        """
        return self._session.send(
            endpoints.validate(
                dataset_id, workbook_id=workbook_id, binded_dataset_id=binded_dataset_id, data=data
            )
        )

    def data_get(
        self,
        dataset_id: str,
        *,
        columns: Sequence[str],
        workbook_id: str | None = None,
        filters: Sequence[DataFilter] | None = None,
        params: Sequence[DataParameter] | None = None,
        sort: Sequence[DataSort] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> DatasetData:
        """``getDatasetData`` → rows of a dataset: the columns asked for, one page.

        A column is named by the guid of its field (``get`` lists them in
        ``dataset.result_schema``), not by its title. One call is one page: ``limit`` rows
        (100 when left out) from ``offset``; an ``offset`` above zero needs ``sort``, or the
        API refuses the request.

        Args:
            dataset_id: The dataset's id.
            columns: The guids of the fields to return, in the order of the row's values.
            workbook_id: The workbook the dataset lies in.
            filters: The rows to keep, by a field's guid, an operation and its values.
            params: Values for the parameters of the dataset.
            sort: The order of the rows, by a field's guid and a direction.
            limit: The most rows to return.
            offset: How many rows to skip.

        Returns:
            The columns returned and the rows, each a list of values in that order.

        Examples:
            >>> page = datalens.datasets.data_get("ds000000000001", columns=["guid-1", "guid-2"])
            >>> page.rows
            [['Moscow', 120], ['Kazan', 80]]
        """
        return self._session.send(
            endpoints.data_get(
                dataset_id,
                columns=columns,
                workbook_id=workbook_id,
                filters=filters,
                params=params,
                sort=sort,
                limit=limit,
                offset=offset,
            )
        )
