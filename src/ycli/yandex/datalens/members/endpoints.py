"""DataLens member operations, declared once (sans-IO).

Examples:
    >>> list_(language=None, search="ann", tab_id=None, filter=None).endpoint.body
    {'search': 'ann'}
"""

from ycli.yandex.core.endpoint import RPC, Effect, Paged
from ycli.yandex.datalens.cursor import DATALENS_CURSOR
from ycli.yandex.datalens.members.models import Member, MemberKind, MemberLanguage, MembersPage
from ycli.yandex.datalens.schemas.access import AccessExtBatchListMembersArgs


def list_(
    *,
    language: MemberLanguage | None,
    search: str | None,
    tab_id: MemberKind | None,
    filter: str | None,  # noqa: A002  # the API's own name for it
) -> Paged[MembersPage, Member]:
    body = AccessExtBatchListMembersArgs(
        language=language, search=search, tabId=tab_id, filter=filter
    )
    return Paged(
        RPC("batchListMembers", MembersPage, json=body, effect=Effect.READ),
        DATALENS_CURSOR,
        lambda page: page.members or [],
    )
