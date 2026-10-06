"""DataLens members client on the httpx2 core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex.core.resource import Resource
from ycli.yandex.datalens.members import endpoints
from ycli.yandex.datalens.members.models import Member
from ycli.yandex.models import ItemList

if TYPE_CHECKING:
    from ycli.yandex.datalens.members.models import MemberKind, MemberLanguage


class MembersClient(Resource):
    """Members: the users, groups and service accounts a role can be given to."""

    def list(
        self,
        *,
        limit: int | None = None,
        language: MemberLanguage | None = None,
        search: str | None = None,
        tab_id: MemberKind | None = None,
        filter: str | None = None,  # noqa: A002  # the API's own name for it
    ) -> ItemList[Member]:
        """``batchListMembers`` → the members of the organization, draining ``nextPageToken``.

        Capped at ``limit`` (``None`` = every member). The ``sub`` of a member is the subject id
        a role is given to (``access_bindings_update``).

        Args:
            limit: The most members to return; ``None`` returns every member.
            language: The language of the names: ``en`` or ``ru``.
            search: Keep the members whose name or address has this text.
            tab_id: Keep one kind of subject, e.g. ``USER_ACCOUNT`` or ``GROUP``.
            filter: A filter expression of the API.

        Returns:
            The members found.

        Examples:
            >>> found = datalens.members.list(search="ann", limit=45).root
            >>> [(member.sub, member.email) for member in found]
            [('user-1', 'ann@example.com'), ('user-2', 'anna@example.com')]
        """
        paged = endpoints.list_(language=language, search=search, tab_id=tab_id, filter=filter)
        return ItemList[Member](list(self._session.iterate(paged, limit=limit)))
