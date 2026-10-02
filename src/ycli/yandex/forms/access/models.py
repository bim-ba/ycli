"""Pydantic models for Forms access (survey permissions).

A form has one permission per ``action``: ``change`` (edit the form, read its answers) and
``submit`` (fill it in). Each carries an ``access`` level — ``owner`` (the owner only),
``restricted`` (the listed users and groups), ``common`` (everyone in the organization) or
``public`` (anyone with the link).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel

AccessAction = Literal["change", "submit"]
AccessLevel = Literal["owner", "restricted", "common", "public"]


class UserIdentity(APIModel):
    """A user by Yandex ID ``uid`` or Yandex Cloud ``cloud_uid``.

    Examples:
        >>> UserIdentity(uid="101523906").uid
        '101523906'
    """

    uid: str | None = Field(default=None, description="Yandex ID user id.")
    cloud_uid: str | None = Field(default=None, description="Yandex Cloud user id.")


class UserRef(APIModel):
    """A user as Forms lists them: identity, login and display name.

    Examples:
        >>> UserRef.model_validate({"identity": {"uid": "1"}, "username": "ivan"}).username
        'ivan'
    """

    identity: UserIdentity | None = Field(default=None, description="The user's ids.")
    username: str | None = Field(default=None, description="Login.")
    display_name: str | None = Field(default=None, description="Display name.")


class GroupIdentity(APIModel):
    """A group by source and id.

    Examples:
        >>> GroupIdentity(src="dir", id="5").src
        'dir'
    """

    src: str | None = Field(default=None, description="Group source: dir, cloud, com or staff.")
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


class PermissionList(RootModel[list[Permission]]):
    """A bare JSON array of :class:`Permission` — one per action.

    Examples:
        >>> PermissionList.model_validate([{"action": "change"}]).root[0].action
        'change'
    """


class AccessUpdate(APIModel):
    """Typed body for ``POST /surveys/{id}/access``: set one action's access level.

    Examples:
        >>> AccessUpdate(action="submit", access="common").model_dump()
        {'action': 'submit', 'access': 'common'}
    """

    action: AccessAction = Field(description="Action: change or submit.")
    access: AccessLevel = Field(description="Access level: owner, restricted, common or public.")


class AccessGrant(APIModel):
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
