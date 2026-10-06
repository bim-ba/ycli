"""DataLens connections client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.connections import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.connections.models import (
        Connection,
        ConnectionCreate,
        ConnectionCreated,
        ConnectionUpdate,
    )


class ConnectionsClient(Resource):
    """Connections: where a dataset takes its data from (a database, a file, an API)."""

    def get(
        self,
        connection_id: str,
        *,
        workbook_id: str | None = None,
        binded_dataset_id: str | None = None,
        rev_id: str | None = None,
    ) -> Connection:
        """``getConnection`` → one connection, without its secrets.

        The kind of the connection comes in ``db_type`` (the reply has no ``type``), and the
        fields of that kind come with it as DataLens sends them; a password or a token is never
        in the reply.

        Args:
            connection_id: The connection's id.
            workbook_id: The workbook the connection lies in.
            binded_dataset_id: A dataset bound to the connection, to read it through.
            rev_id: The revision to read; the current one when left out.

        Returns:
            The connection.

        Examples:
            >>> connection = datalens.connections.get("con00000000001").root
            >>> connection.name, connection.db_type
            ('Sales DB', 'clickhouse')
        """
        return self._session.send(
            endpoints.get(
                connection_id,
                workbook_id=workbook_id,
                binded_dataset_id=binded_dataset_id,
                rev_id=rev_id,
            )
        )

    def create(self, connection: ConnectionCreate) -> ConnectionCreated:
        """``createConnection`` — create a connection → its id.

        ``type`` says which kind it is and which fields it takes; give ``workbook_id`` or
        ``dir_path`` for where it lies. Not every kind can be created through the API: a
        connection to Google Sheets (``gsheets``) answers ``400 This connection type is not
        editable``. Such a connection is made in the interface and is read here like any other.

        Args:
            connection: The new connection.

        Returns:
            The id of the connection.

        Examples:
            >>> from ycli.yandex.datalens.connections.models import ConnectionCreate
            >>> new = ConnectionCreate.model_validate(
            ...     {
            ...         "type": "clickhouse",
            ...         "name": "Sales DB",
            ...         "workbook_id": "wb000000000001",
            ...         "host": "db.example.net",
            ...         "port": 8443,
            ...         "username": "reader",
            ...         "password": "example-password",
            ...     }
            ... )
            >>> datalens.connections.create(new).id
            'con00000000001'
        """
        return self._session.send(endpoints.create(connection))

    def update(self, connection_id: str, *, data: ConnectionUpdate) -> None:
        """``updateConnection`` — change the fields given in ``data`` (``200``, empty body).

        Args:
            connection_id: The connection's id.
            data: The fields to change, of the connection's own kind.

        Examples:
            >>> from ycli.yandex.datalens.connections.models import ConnectionUpdate
            >>> change = ConnectionUpdate.model_validate({"host": "db2.example.net"})
            >>> datalens.connections.update("con00000000001", data=change)
        """
        self._session.send(endpoints.update(connection_id, data=data))

    def delete(self, connection_id: str) -> None:
        """``deleteConnection`` — delete a connection (``200``, empty body).

        The datasets built on it lose their source.

        Args:
            connection_id: The connection's id.

        Examples:
            >>> datalens.connections.delete("con00000000001")
        """
        self._session.send(endpoints.delete(connection_id))
