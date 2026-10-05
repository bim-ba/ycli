"""DataLens tenant client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.tenant import endpoints

if TYPE_CHECKING:
    from ycli.yandex.datalens.tenant.models import TenantDetails


class TenantClient(Resource):
    """The DataLens instance of the organization."""

    def details_get(self) -> TenantDetails:
        """``getTenantDetails`` → the instance the credentials reach (a safe auth probe).

        Returns:
            The tenant: its id, the organization it belongs to and its public settings.

        Examples:
            >>> datalens.tenant.details_get().tenant_id
            'org_bpf00000000000000000'
        """
        return self._session.send(endpoints.details_get())
