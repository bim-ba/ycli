"""Wiki models that several resources share: one class per shape."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel

#: Kind of deferred Wiki operation: the ``type`` of the reference a trigger returns.
OperationType = Literal["move", "clone", "clone_inline_grid"]


class UserIdentity(APIModel):
    """A user by passport ``uid`` or ``cloud_uid``.

    Examples:
        >>> UserIdentity(uid="1000").model_dump(exclude_none=True)
        {'uid': '1000'}
    """

    uid: str | None = Field(default=None, description="Passport uid of the user.")
    cloud_uid: str | None = Field(default=None, description="Cloud uid of the user.")


class PageIdentity(APIModel):
    """A page by ``id`` or ``slug``; ``id`` takes priority when both are given.

    Examples:
        >>> PageIdentity(slug="data/x").slug
        'data/x'
    """

    id: int | None = Field(
        default=None, description="Numeric page id (wins over slug if both set)."
    )
    slug: str | None = Field(default=None, description="Permanent page slug, e.g. ``data/x``.")


class OperationIdentity(APIModel):
    """Reference to a deferred operation (``{type, id}``) returned by the call that started it.

    Examples:
        >>> OperationIdentity(type="clone_inline_grid", id="task-1").id
        'task-1'
    """

    type: OperationType | None = Field(
        default=None, description="Operation kind (``move`` / ``clone`` / ``clone_inline_grid``)."
    )
    id: str | None = Field(
        default=None, description="Task id to poll on the ``operations`` resource."
    )


class AsyncOperation(APIModel):
    """Reply of a call that works in the background (a page clone or move, a grid clone).

    It names the started ``operation`` and a ``status_url``; poll the ``operations`` resource
    with ``operation.id`` until it reaches a terminal state.

    Examples:
        >>> AsyncOperation.model_validate({"operation": {"type": "move", "id": "t1"}}).operation.id
        't1'
    """

    operation: OperationIdentity | None = Field(
        default=None, description="The started operation (``id`` is the task to poll)."
    )
    status_url: str | None = Field(
        default=None, description="URL that reports the operation's progress."
    )
    dry_run: bool | None = Field(
        default=None, description="Whether this was a validation-only dry run."
    )
