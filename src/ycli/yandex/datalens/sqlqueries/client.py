"""DataLens saved SQL queries client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.sqlqueries import endpoints

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ycli.yandex.datalens.sqlqueries.models import (
        SqlQueryCreated,
        SqlQueryDetails,
        SqlQueryNewParam,
        SqlQueryRun,
        SqlQuerySaved,
        SqlQuerySavedParam,
        SqlQueryValue,
    )


class SqlQueriesClient(Resource):
    """Saved SQL queries: a text of SQL kept in a workbook and run over a connection.

    Experimental in the DataLens API, and written from its document: no reply was measured. An
    organization whose SQL editor is off answers ``403 SQL_EDITOR_NOT_ALLOWED``.
    """

    def get(
        self,
        sql_query_id: str,
        *,
        rev_id: str | None = None,
        include_permissions: bool | None = None,
        include_favorite: bool | None = None,
    ) -> SqlQueryDetails:
        """``getSqlQuery`` → one saved SQL query (experimental, not measured).

        Args:
            sql_query_id: The query's id.
            rev_id: The revision to read; the current one when left out.
            include_permissions: Also say what the caller may do with it.
            include_favorite: Also say whether it is a favourite.

        Returns:
            The query: ``entry.data`` holds its text, its connection and its parameters.

        Examples:
            >>> found = datalens.sqlqueries.get("sq00000000001").entry
            >>> found.data.query
            'select count(*) from orders where day >= {{since}}'
        """
        return self._session.send(
            endpoints.get(
                sql_query_id,
                rev_id=rev_id,
                include_permissions=include_permissions,
                include_favorite=include_favorite,
            )
        )

    def create(
        self,
        *,
        workbook_id: str,
        name: str,
        connection_id: str,
        query: str,
        description: str | None = None,
        params: Sequence[SqlQueryNewParam] | None = None,
    ) -> SqlQueryCreated:
        """``createSqlQuery`` — save a SQL query in a workbook (experimental, not measured).

        Args:
            workbook_id: The workbook to keep it in.
            name: The query's name in the workbook.
            connection_id: The connection it runs over: PostgreSQL, ClickHouse, MySQL,
                Greenplum or Trino.
            query: The text of the query.
            description: A description.
            params: The parameters the text takes, each with a name, a type and a default.

        Returns:
            The query as saved.

        Examples:
            >>> made = datalens.sqlqueries.create(
            ...     workbook_id="wb000000000001",
            ...     name="Orders a day",
            ...     connection_id="con00000000001",
            ...     query="select count(*) from orders",
            ... )
            >>> made.entry.entry_id
            'sq00000000001'
        """
        return self._session.send(
            endpoints.create(
                workbook_id=workbook_id,
                name=name,
                connection_id=connection_id,
                query=query,
                description=description,
                params=params,
            )
        )

    def update(
        self,
        sql_query_id: str,
        *,
        connection_id: str,
        query: str,
        description: str | None = None,
        params: Sequence[SqlQuerySavedParam] | None = None,
    ) -> SqlQuerySaved:
        """``updateSqlQuery`` — save a SQL query anew (experimental, not measured).

        The document requires the connection and the text every time.

        Args:
            sql_query_id: The query's id.
            connection_id: The connection it runs over.
            query: The text of the query.
            description: A new description.
            params: The parameters the text takes.

        Returns:
            The query as saved.

        Examples:
            >>> saved = datalens.sqlqueries.update(
            ...     "sq00000000001",
            ...     connection_id="con00000000001",
            ...     query="select count(*) from orders where paid",
            ... )
            >>> saved.entry.data.query
            'select count(*) from orders where paid'
        """
        return self._session.send(
            endpoints.update(
                sql_query_id,
                connection_id=connection_id,
                query=query,
                description=description,
                params=params,
            )
        )

    def delete(self, sql_query_id: str) -> None:
        """``deleteSqlQuery`` — delete a saved SQL query (experimental, not measured).

        Args:
            sql_query_id: The query's id.

        Examples:
            >>> datalens.sqlqueries.delete("sq00000000001")
        """
        self._session.send(endpoints.delete(sql_query_id))

    def run(
        self, sql_query_id: str, *, params: Mapping[str, SqlQueryValue] | None = None
    ) -> SqlQueryRun:
        """``runSqlQuery`` — run a saved SQL query → its result (experimental, not measured).

        The query runs on its connection as it is saved: a text that changes data changes it.
        A parameter left out takes its default.

        Args:
            sql_query_id: The query's id.
            params: The values of the parameters, by name.

        Returns:
            The run: its ``status`` and, for each statement, the columns and the rows, or the
            error.

        Examples:
            >>> ran = datalens.sqlqueries.run("sq00000000001", params={"since": "2026-10-01"})
            >>> ran.status, ran.results[0].rows
            ('success', [[42]])
        """
        return self._session.send(endpoints.run(sql_query_id, params=params))
