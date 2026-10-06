"""DataLens permission operations, declared once (sans-IO).

Examples:
    >>> get_bulk(entry_ids=None, workbook_ids=["w1"], collection_ids=None).body
    {'workbookIds': ['w1']}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint
from ycli.yandex.datalens.permissions.models import PermissionsBulk
from ycli.yandex.datalens.schemas.permissions import GetPermissionsBulkArgs


def _listed(ids: Sequence[str] | None) -> list[str] | None:
    return None if ids is None else list(ids)


def get_bulk(
    *,
    entry_ids: Sequence[str] | None,
    workbook_ids: Sequence[str] | None,
    collection_ids: Sequence[str] | None,
) -> Endpoint[PermissionsBulk]:
    body = GetPermissionsBulkArgs(
        entryIds=_listed(entry_ids),
        workbookIds=_listed(workbook_ids),
        collectionIds=_listed(collection_ids),
    )
    return RPC("getPermissionsBulk", PermissionsBulk, json=body, effect=Effect.READ)
