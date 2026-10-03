"""Pydantic models for Wiki page access (``/pages/{id}/access``) and the access fields of a page.

A page's access is a policy (who may open it at all) plus lists of personal grants; each grant
is a :class:`PageAccess` — a user or a group, with a role. ``GET /pages/{id}?fields=access_policy,
access_lists,owner`` reads them back (see :class:`~ycli.yandex.wiki.pages.models.PageDetails`).

``extra='ignore'`` via :class:`~ycli.yandex.models.APIModel`.
"""

from __future__ import annotations

from typing import Any, Literal, Self

from pydantic import Field, model_validator

from ycli.yandex.models import APIModel
from ycli.yandex.wiki.models import User, UserIdentity

#: What a grant lets its holder do, weakest first.
AccessRole = Literal["reader", "editor", "extra_editor", "author"]
#: The directory that owns a group.
GroupSource = Literal["dir", "cloud", "com", "staff"]
#: Whether a grant also applies to the page's subpages.
AccessInheritance = Literal["inherited", "not_inherited"]


class GroupIdentity(APIModel):
    """A group by the directory it lives in (``src``) and its id there.

    Examples:
        >>> GroupIdentity(src="dir", id="42").model_dump()
        {'src': 'dir', 'id': '42'}
    """

    src: GroupSource = Field(
        description="Directory that owns the group: ``dir``, ``cloud``, ``com`` or ``staff``."
    )
    id: str = Field(description="Group id inside that directory.")


class AccessGroup(APIModel):
    """A group in an access entry.

    Examples:
        >>> AccessGroup.model_validate({"name": "Docs", "type": "group"}).name
        'Docs'
    """

    id: str | None = Field(default=None, description="Group id (dir_id outside, staff_id inside).")
    identity: GroupIdentity | None = Field(default=None, description="Directory and id.")
    name: str | None = Field(default=None, description="Name of the group.")
    type: Literal["wiki", "service", "servicerole", "group", "department"] | None = Field(
        default=None, description="Kind of group."
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Directory-specific details (url, dir_id, externals_count)."
    )
    members_count: int | None = Field(default=None, description="Number of members.")


class PageAccess(APIModel):
    """One personal grant on a page: a user or a group with a role.

    Examples:
        >>> PageAccess.model_validate({"id": "9", "role": "reader"}).role
        'reader'
    """

    id: str = Field(description="Id of the grant, the ``access_id`` of update and delete.")
    created_at: str | None = Field(default=None, description="ISO-8601 time of the grant.")
    user: User | None = Field(default=None, description="The user, for a user grant.")
    group: AccessGroup | None = Field(default=None, description="The group, for a group grant.")
    role: AccessRole = Field(description="What the holder may do.")
    inheritance: AccessInheritance | None = Field(
        default=None, description="Whether the grant also covers subpages."
    )


class PageAccessCreate(APIModel):
    """Typed body for ``POST /pages/{id}/access`` — grant a user or a group a role on a page.

    Name exactly one of ``user`` and ``group``.

    Examples:
        >>> PageAccessCreate(user=UserIdentity(uid="1000"), role="editor").model_dump(
        ...     exclude_none=True
        ... )
        {'user': {'uid': '1000'}, 'role': 'editor'}
    """

    user: UserIdentity | None = Field(default=None, description="Grant this user the role.")
    group: GroupIdentity | None = Field(default=None, description="Grant this group the role.")
    role: AccessRole = Field(description="Role to grant.")
    inheritance: AccessInheritance | None = Field(
        default=None, description="Whether the grant also covers subpages."
    )

    @model_validator(mode="after")
    def _one_grantee(self) -> Self:
        if (self.user is None) == (self.group is None):
            raise ValueError("name exactly one of user and group")
        return self


class PageAccessUpdate(APIModel):
    """Typed body for ``POST /pages/{id}/access/{access_id}`` — change a grant's role or reach.

    Examples:
        >>> PageAccessUpdate(role="reader").model_dump(exclude_none=True)
        {'role': 'reader'}
    """

    role: AccessRole | None = Field(default=None, description="New role.")
    inheritance: AccessInheritance | None = Field(
        default=None, description="Whether the grant also covers subpages."
    )

    @model_validator(mode="after")
    def _something_to_change(self) -> Self:
        if self.role is None and self.inheritance is None:
            raise ValueError("give a role, an inheritance or both")
        return self


class PageAccessPolicy(APIModel):
    """Who may open a page at all (``fields=access_policy``).

    Examples:
        >>> PageAccessPolicy.model_validate({"access_type": "custom"}).access_type
        'custom'
    """

    access_type: Literal["inherited", "all_staff", "custom"] = Field(
        description="``inherited`` from the parent, ``all_staff``, or ``custom`` (grants only)."
    )
    inherited_access_type: Literal["all_staff", "custom"] | None = Field(
        default=None, description="The type inherited from the parent page."
    )
    all_staff_role: Literal["reader", "editor", "extra_editor"] | None = Field(
        default=None, description="Role every employee holds under ``all_staff``."
    )
    has_external: bool | None = Field(
        default=None, description="Whether external consultants can open the page."
    )
    invite: dict[str, Any] | None = Field(default=None, description="Status of the invitation.")


class PageAccessLists(APIModel):
    """The grants on a page by origin (``fields=access_lists``).

    Examples:
        >>> PageAccessLists.model_validate({"direct": [{"id": "9", "role": "author"}]}).direct[0].id
        '9'
    """

    direct: list[PageAccess] = Field(default_factory=list, description="Granted on this page.")
    by_link: list[PageAccess] = Field(default_factory=list, description="Granted by a link.")
    inherited: list[PageAccess] = Field(
        default_factory=list, description="Inherited from parent pages."
    )


class PageOwner(APIModel):
    """The owner of a page (``fields=owner``).

    Examples:
        >>> PageOwner.model_validate({"user": {"username": "ivan"}}).user.username
        'ivan'
    """

    user: User | None = Field(default=None, description="The owning user.")
    group: AccessGroup | None = Field(default=None, description="The owning group (not in use).")


AccessUser = User  # deprecated, removed in 0.39
