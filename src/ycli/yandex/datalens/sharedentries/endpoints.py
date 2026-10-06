"""DataLens shared entry operations, declared once (sans-IO).

Examples:
    >>> access_bindings_list("ent1", get_inherited_bindings=None).endpoint.body
    {'entryId': 'ent1'}
"""

from collections.abc import Sequence

from ycli.yandex.core.endpoint import RPC, Effect, Endpoint, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.models import (
    AccessBindingDelta,
    AccessBindingsPage,
    Operation,
    SubjectWithBindings,
)
from ycli.yandex.datalens.schemas.shared_entry import (
    ListSharedEntryAccessBindingsArgs,
    UpdateSharedEntryAccessBindingsArgs,
)


def access_bindings_list(
    entry_id: str, *, get_inherited_bindings: bool | None
) -> Paged[AccessBindingsPage, SubjectWithBindings]:
    body = ListSharedEntryAccessBindingsArgs(
        entryId=entry_id, getInheritedBindings=get_inherited_bindings
    )
    return Paged(
        RPC("listSharedEntryAccessBindings", AccessBindingsPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.subjects_with_bindings or [],
    )


def access_bindings_update(
    entry_id: str, *, deltas: Sequence[AccessBindingDelta]
) -> Endpoint[Operation]:
    body = UpdateSharedEntryAccessBindingsArgs(entryId=entry_id, deltas=list(deltas))
    return RPC("updateSharedEntryAccessBindings", Operation, json=body, effect=Effect.WRITE)
