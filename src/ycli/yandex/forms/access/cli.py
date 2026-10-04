"""`forms access` commands: who may edit and who may fill a form."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import values_option
from ycli.yandex.forms.access.models import (
    AccessGrant,
    AccessLevel,
    AccessRevoke,
    AccessUpdate,
    GroupIdentity,
    Permission,
)
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.models import UserIdentity
from ycli.yandex.forms.typedefs import SurveyIDArg
from ycli.yandex.models import GroupSource, ItemList

app = typer.Typer(name="access", help="Forms survey permissions.", no_args_is_help=True)

ActionOpt = Annotated[
    str, typer.Option(help="Action: change (edit, read answers) or submit (fill in).")
]
UIDOpt = Annotated[str | None, typer.Option("--uid", help="User's Yandex ID uid.")]
CloudUIDOpt = Annotated[str | None, typer.Option("--cloud-uid", help="User's Yandex Cloud uid.")]
GroupSrcOpt = Annotated[
    str | None, values_option(GroupSource, "--group-src", help="Where the group is kept.")
]
GroupIDOpt = Annotated[str | None, typer.Option("--group-id", help="Group id within its source.")]


def _principal(
    uid: str | None, cloud_uid: str | None, group_src: GroupSource | None, group_id: str | None
) -> tuple[UserIdentity | None, GroupIdentity | None]:
    """The user and the group the options name (``None`` for the one not given)."""
    user = (
        UserIdentity(uid=uid, cloud_uid=cloud_uid)
        if uid is not None or cloud_uid is not None
        else None
    )
    group = (
        GroupIdentity(src=group_src, id=group_id)
        if group_src is not None or group_id is not None
        else None
    )
    return user, group


@app.command()
def get(survey_id: SurveyIDArg, *, forms: FormsClient) -> ItemList[Permission]:
    """Print who may edit and who may fill form SURVEY_ID (one entry per action)."""
    return forms.access.get(survey_id)


@app.command("set")
def set_(
    survey_id: SurveyIDArg,
    action: ActionOpt,
    access: Annotated[str, values_option(AccessLevel, help="Level of access.")],
    *,
    forms: FormsClient,
) -> ItemList[Permission]:
    """Set the access level of one action on form SURVEY_ID (POST …/access)."""
    body = AccessUpdate.model_validate({"action": action, "access": access})
    return forms.access.set(survey_id, body)


@app.command()
def grant(
    survey_id: SurveyIDArg,
    action: ActionOpt,
    uid: UIDOpt = None,
    cloud_uid: CloudUIDOpt = None,
    group_src: GroupSrcOpt = None,
    group_id: GroupIDOpt = None,
    *,
    forms: FormsClient,
) -> ItemList[Permission]:
    """Let a user (--uid / --cloud-uid) or a group (--group-src + --group-id) perform ACTION."""
    user, group = _principal(uid, cloud_uid, group_src, group_id)
    body = AccessGrant.model_validate({"action": action, "user": user, "group": group})
    return forms.access.grant(survey_id, body)


@app.command()
def revoke(
    survey_id: SurveyIDArg,
    action: ActionOpt,
    uid: UIDOpt = None,
    cloud_uid: CloudUIDOpt = None,
    group_src: GroupSrcOpt = None,
    group_id: GroupIDOpt = None,
    *,
    forms: FormsClient,
) -> ItemList[Permission]:
    """Stop a user (--uid / --cloud-uid) or a group (--group-src + --group-id) performing ACTION."""
    user, group = _principal(uid, cloud_uid, group_src, group_id)
    body = AccessRevoke.model_validate({"action": action, "user": user, "group": group})
    return forms.access.revoke(survey_id, body)
