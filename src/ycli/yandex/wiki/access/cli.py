"""`wiki access` commands — who may read and edit a page."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import values_option
from ycli.yandex.models import Ack
from ycli.yandex.wiki.access.models import (
    AccessInheritance,
    AccessRole,
    GroupIdentity,
    GroupSource,
    PageAccess,
    PageAccessCreate,
    PageAccessUpdate,
)
from ycli.yandex.wiki.client import WikiClient
from ycli.yandex.wiki.models import UserIdentity
from ycli.yandex.wiki.typedefs import PageIDArg

app = typer.Typer(
    name="access",
    help="Wiki page access: grant, change, revoke (read back with `pages get-by-id --fields "
    "access_policy,access_lists`).",
    no_args_is_help=True,
)

AccessIDArg = Annotated[str, typer.Argument(metavar="ACCESS_ID", help="Id of the access entry.")]
InheritanceOption = Annotated[
    str | None,
    values_option(
        AccessInheritance,
        help="Whether the access also covers subpages.",
    ),
]
PreventSelflockOption = Annotated[
    bool | None,
    typer.Option(
        "--prevent-selflock/--no-prevent-selflock",
        help="Refuse the change if it would leave you without read access or the right to "
        "change accesses.",
    ),
]


@app.command()
def create(
    page_id: PageIDArg,
    role: Annotated[
        str,
        values_option(AccessRole, help="Role to grant."),
    ],
    user_uid: Annotated[
        str | None, typer.Option("--user-uid", help="Passport uid of the user to grant.")
    ] = None,
    user_cloud_uid: Annotated[
        str | None, typer.Option("--user-cloud-uid", help="Cloud uid of the user to grant.")
    ] = None,
    group_src: Annotated[
        str | None,
        values_option(
            GroupSource,
            "--group-src",
            help="Where the group is kept.",
        ),
    ] = None,
    group_id: Annotated[
        str | None, typer.Option("--group-id", help="Id of the group to grant in that directory.")
    ] = None,
    inheritance: InheritanceOption = None,
    *,
    wiki: WikiClient,
) -> PageAccess:
    """Grant a user or a group a role on a page (POST /pages/{id}/access).

    Name the user with --user-uid / --user-cloud-uid, or the group with --group-src and
    --group-id.
    """
    user = (
        UserIdentity(uid=user_uid, cloud_uid=user_cloud_uid)
        if user_uid is not None or user_cloud_uid is not None
        else None
    )
    given = {"src": group_src, "id": group_id}
    group = (
        GroupIdentity.model_validate({key: value for key, value in given.items() if value})
        if group_src or group_id is not None
        else None
    )
    body = PageAccessCreate(user=user, group=group, role=role, inheritance=inheritance)
    return wiki.access.create(page_id=page_id, body=body)


@app.command()
def update(
    page_id: PageIDArg,
    access_id: AccessIDArg,
    role: Annotated[
        str | None,
        values_option(AccessRole, help="New role."),
    ] = None,
    inheritance: InheritanceOption = None,
    prevent_selflock: PreventSelflockOption = None,
    *,
    wiki: WikiClient,
) -> PageAccess:
    """Change the role or reach of an access (POST /pages/{id}/access/{access_id})."""
    body = PageAccessUpdate(role=role, inheritance=inheritance)
    return wiki.access.update(
        page_id=page_id,
        access_id=access_id,
        body=body,
        prevent_selflock=prevent_selflock,
    )


@app.command()
def delete(
    page_id: PageIDArg,
    access_id: AccessIDArg,
    prevent_selflock: PreventSelflockOption = None,
    *,
    wiki: WikiClient,
) -> Ack:
    """Revoke one access (DELETE /pages/{id}/access/{access_id})."""
    wiki.access.delete(page_id=page_id, access_id=access_id, prevent_selflock=prevent_selflock)
    return Ack.deleted("access", access_id, from_=f"page {page_id}")


@app.command()
def clear(
    page_id: PageIDArg,
    prevent_selflock: PreventSelflockOption = None,
    *,
    wiki: WikiClient,
) -> Ack:
    """Revoke every personal access but the owner's (DELETE /pages/{id}/access)."""
    wiki.access.clear(page_id=page_id, prevent_selflock=prevent_selflock)
    return Ack.cleared(f"personal accesses on page {page_id}")
