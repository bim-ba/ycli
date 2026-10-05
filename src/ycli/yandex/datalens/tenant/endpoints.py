"""DataLens tenant operations, declared once (sans-IO).

Examples:
    >>> details_get().path
    'rpc/getTenantDetails'
"""

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.tenant.models import TenantDetails


def details_get() -> Endpoint[TenantDetails]:
    return RPC("getTenantDetails", TenantDetails, effect=Effect.READ)
