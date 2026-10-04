"""Pydantic models for Forms access (survey permissions).

A form has one permission per ``action``: ``change`` (edit the form, read its answers) and
``submit`` (fill it in). Each carries an ``access`` level — ``owner`` (the owner only),
``restricted`` (the listed users and groups), ``common`` (everyone in the organization) or
``public`` (anyone with the link).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.forms.models import UserIdentity, UserRef
from ycli.yandex.models import APIModel, GroupSource, RequestBody

AccessAction = Literal["change", "submit"] | str
AccessLevel = Literal["owner", "restricted", "common", "public"] | str


class GroupIdentity(APIModel):
    """A group by source and id.

    Examples:
        >>> GroupIdentity(src="dir", id="5").src
        'dir'
    """

    src: GroupSource | None = Field(default=None, description="Where the group is kept.")
    id: str | None = Field(default=None, description="Group id within its source.")


class PermissionGroup(APIModel):
    """A group a permission lists.

    Examples:
        >>> PermissionGroup.model_validate({"identity": {"src": "dir", "id": "5"}}).identity.id
        '5'
    """

    identity: GroupIdentity | None = Field(default=None, description="The group's ids.")
    name: str | None = Field(default=None, description="Group name.")
    type: str | None = Field(default=None, description="Group type.")


class Permission(APIModel):
    """Who may perform one action on a form.

    Examples:
        >>> Permission.model_validate({"access": "common", "action": "submit"}).access
        'common'
    """

    access: str | None = Field(
        default=None, description="Access level: owner, restricted, common or public."
    )
    action: str | None = Field(
        default=None, description="Action: change (edit, read answers) or submit (fill in)."
    )
    users: list[UserRef] | None = Field(
        default=None, description="Users granted the action (restricted access)."
    )
    groups: list[PermissionGroup] | None = Field(
        default=None, description="Groups granted the action (restricted access)."
    )


class AccessUpdate(RequestBody):
    """Typed body for ``POST /surveys/{id}/access``: set one action's access level.

    Examples:
        >>> AccessUpdate(action="submit", access="common").model_dump()
        {'action': 'submit', 'access': 'common'}
    """

    action: AccessAction = Field(description="Action: change or submit.")
    access: AccessLevel = Field(description="Access level: owner, restricted, common or public.")


class AccessGrant(RequestBody):
    """Typed body for ``POST /surveys/{id}/access/grant``: add a user or a group to an action.

    Unset fields are dropped before the request is sent.

    Examples:
        >>> AccessGrant(action="change", user=UserIdentity(uid="7")).model_dump(exclude_none=True)
        {'action': 'change', 'user': {'uid': '7'}}
    """

    action: AccessAction = Field(description="Action: change or submit.")
    user: UserIdentity | None = Field(default=None, description="The user to add.")
    group: GroupIdentity | None = Field(default=None, description="The group to add.")


class AccessRevoke(AccessGrant):
    """Typed body for ``POST /surveys/{id}/access/revoke``: remove a user or a group.

    Examples:
        >>> AccessRevoke(action="submit", group=GroupIdentity(src="dir", id="5")).group.id
        '5'
    """
