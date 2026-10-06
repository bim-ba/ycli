"""DataLens connection models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.connection import ConnectionCreate, ConnectionUpdate
from ycli.yandex.datalens.schemas.connection import ConnectionCreateResponse as ConnectionCreated
from ycli.yandex.datalens.schemas.connection import ConnectionRead as Connection

__all__ = ["Connection", "ConnectionCreate", "ConnectionCreated", "ConnectionUpdate"]
