"""DataLens audit models: the public names of the generated classes this resource uses."""

from ycli.yandex.datalens.schemas.audit import AuditEntry
from ycli.yandex.datalens.schemas.audit import GetAuditEntriesUpdatesResult as AuditEntriesPage
from ycli.yandex.datalens.schemas.audit import (
    GetAuditEntryPermissionsForUserResult as UserEntryPermissions,
)

__all__ = ["AuditEntriesPage", "AuditEntry", "UserEntryPermissions"]
