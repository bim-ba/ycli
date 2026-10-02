"""`forms access` commands: who may edit and who may fill a form."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.yandex.forms.access.models import (
    AccessGrant,
    AccessRevoke,
    AccessUpdate,
    GroupIdentity,
    PermissionList,
    UserIdentity,
)
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.typedefs import SurveyIdArg

app = typer.Typer(name="access", help="Forms survey permissions.", no_args_is_help=True)

ActionOpt = Annotated[
    str, typer.Option(help="Action: change (edit, read answers) or submit (fill in).")
]
UidOpt = Annotated[str, typer.Option("--uid", help="User's Yandex ID uid.")]
CloudUidOpt = Annotated[str, typer.Option("--cloud-uid", help="User's Yandex Cloud uid.")]
GroupSrcOpt = Annotated[
    str, typer.Option("--group-src", help="Group source: dir, cloud, com or staff.")
]
GroupIdOpt = Annotated[str, typer.Option("--group-id", help="Group id within its source.")]


def _principal(
    uid: str, cloud_uid: str, group_src: str, group_id: str
) -> tuple[UserIdentity | None, GroupIdentity | None]:
    """The user and the group the options name (``None`` for the one not given)."""
    user = UserIdentity(uid=uid or None, cloud_uid=cloud_uid or None) if uid or cloud_uid else None
    group = (
        GroupIdentity(src=group_src or None, id=group_id or None) if group_src or group_id else None
    )
    return user, group


@app.command()
def get(survey_id: SurveyIdArg, *, forms: FormsClient) -> PermissionList:
    """Print who may edit and who may fill form SURVEY_ID (one entry per action)."""
    return forms.access.get(survey_id)


@app.command("set")
def set_(
    survey_id: SurveyIdArg,
    action: ActionOpt,
    access: Annotated[str, typer.Option(help="Level: owner, restricted, common or public.")],
    *,
    forms: FormsClient,
) -> PermissionList:
    """Set the access level of one action on form SURVEY_ID (POST …/access)."""
    body = AccessUpdate.model_validate({"action": action, "access": access}).model_dump()
    return forms.access.set(survey_id, body)


@app.command()
def grant(
    survey_id: SurveyIdArg,
    action: ActionOpt,
    uid: UidOpt = "",
    cloud_uid: CloudUidOpt = "",
    group_src: GroupSrcOpt = "",
    group_id: GroupIdOpt = "",
    *,
    forms: FormsClient,
) -> PermissionList:
    """Let a user (--uid / --cloud-uid) or a group (--group-src + --group-id) perform ACTION."""
    user, group = _principal(uid, cloud_uid, group_src, group_id)
    body = AccessGrant.model_validate({"action": action, "user": user, "group": group})
    return forms.access.grant(survey_id, body.model_dump(exclude_none=True))


@app.command()
def revoke(
    survey_id: SurveyIdArg,
    action: ActionOpt,
    uid: UidOpt = "",
    cloud_uid: CloudUidOpt = "",
    group_src: GroupSrcOpt = "",
    group_id: GroupIdOpt = "",
    *,
    forms: FormsClient,
) -> PermissionList:
    """Stop a user (--uid / --cloud-uid) or a group (--group-src + --group-id) performing ACTION."""
    user, group = _principal(uid, cloud_uid, group_src, group_id)
    body = AccessRevoke.model_validate({"action": action, "user": user, "group": group})
    return forms.access.revoke(survey_id, body.model_dump(exclude_none=True))
