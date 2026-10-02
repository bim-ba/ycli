"""Pydantic models for Forms notifications: the runs of a form's integrations.

A notification is one run of one integration for one answer. It is ``pending`` until the
integration finishes, then ``success``, ``error`` or ``canceled``.
"""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class Notification(APIModel):
    """One run of an integration, as the listing shows it.

    Examples:
        >>> Notification.model_validate({"id": 7, "status": "error", "type": "http"}).status
        'error'
    """

    id: int | None = Field(default=None, description="Notification id (integer).")
    status: str | None = Field(
        default=None, description="Run state: pending, success, error or canceled."
    )
    created: str | None = Field(default=None, description="ISO-8601 time the run was queued.")
    finished: str | None = Field(default=None, description="ISO-8601 time the run ended.")
    survey_id: str | None = Field(default=None, description="Form id.")
    survey_name: str | None = Field(default=None, description="Form name.")
    hook_id: int | None = Field(default=None, description="Integration group id.")
    hook_name: str | None = Field(default=None, description="Integration group name.")
    subscription_id: int | None = Field(default=None, description="Integration id.")
    answer_id: int | None = Field(default=None, description="Id of the answer that triggered it.")
    user_id: int | None = Field(default=None, description="Id of the user who answered.")
    type: str | None = Field(
        default=None,
        description="Integration type: email, tracker, tracker_comment, wiki, jsonrpc, http or "
        "function.",
    )
    comment: str | None = Field(default=None, description="Note on the run.")


class NotificationField(APIModel):
    """One named value in a notification's context, response or error.

    Examples:
        >>> NotificationField.model_validate({"name": "url", "value": "x", "type": "url"}).type
        'url'
    """

    name: str | None = Field(default=None, description="Field name.")
    value: str | None = Field(default=None, description="Field value.")
    type: str | None = Field(
        default=None, description="Display type: text, textarea, code, json, xml or url."
    )


class NotificationDetails(Notification):
    """A notification with what the integration was given, answered and failed with.

    Examples:
        >>> NotificationDetails.model_validate(
        ...     {"id": 7, "error": [{"name": "detail", "value": "timeout"}]}
        ... ).error[0].value
        'timeout'
    """

    context: list[NotificationField] | None = Field(
        default=None, description="What the integration was given."
    )
    response: list[NotificationField] | None = Field(
        default=None, description="What the integration answered."
    )
    error: list[NotificationField] | None = Field(
        default=None, description="Why the run failed (error runs only)."
    )


class NotificationLinks(APIModel):
    """The paging links of a notification listing (internal).

    Examples:
        >>> NotificationLinks.model_validate({"next": "/v1/notifications/?id=9"}).next
        '/v1/notifications/?id=9'
    """

    next: str | None = Field(default=None, description="Link to the next page.")


class NotificationPage(APIModel):
    """One page of ``GET /notifications`` (internal).

    Examples:
        >>> NotificationPage.model_validate({"links": {}, "result": [{"id": 7}]}).result[0].id
        7
    """

    links: NotificationLinks = Field(
        default_factory=NotificationLinks, description="Link to the next page."
    )
    result: list[Notification] = Field(default_factory=list, description="The page's runs.")


class NotificationList(RootModel[list[Notification]]):
    """A flat list of :class:`Notification` — the return type of ``NotificationsClient.list``.

    Examples:
        >>> NotificationList.model_validate([{"id": 7}]).root[0].id
        7
    """


class NotificationStatus(APIModel):
    """A notification's id and run state.

    Examples:
        >>> NotificationStatus.model_validate({"id": 7, "status": "pending"}).status
        'pending'
    """

    id: int | None = Field(default=None, description="Notification id.")
    status: str | None = Field(
        default=None, description="Run state: pending, success, error or canceled."
    )


class NotificationActionResult(APIModel):
    """How a restart or a cancel went: ``ok``, ``skip``, ``fail`` or ``operation``.

    Examples:
        >>> NotificationActionResult.model_validate({"status": "operation", "operation_id": "a"})
        NotificationActionResult(status='operation', detail=None, operation_id='a')
    """

    status: str | None = Field(
        default=None,
        description="ok (done), skip (nothing to do), fail (see detail) or operation (queued: "
        "operation_id may be 'not-supported', read the run's state instead).",
    )
    detail: str | None = Field(default=None, description="Why it failed (fail only).")
    operation_id: str | None = Field(
        default=None, description="Background operation id (operation only)."
    )


class NotificationAction(APIModel):
    """The answer to a restart or a cancel of a notification.

    Examples:
        >>> NotificationAction.model_validate(
        ...     {"id": 7, "survey_id": "686d", "result": {"status": "ok"}}
        ... ).result.status
        'ok'
    """

    id: int | None = Field(default=None, description="Notification id.")
    survey_id: str | None = Field(default=None, description="Form id.")
    subscription_id: int | None = Field(default=None, description="Integration id.")
    result: NotificationActionResult | None = Field(
        default=None, description="How the action went."
    )


class NotificationIdList(RootModel[list[int]]):
    """A bare JSON array of notification ids — the failed runs of a form.

    Examples:
        >>> NotificationIdList.model_validate([7, 9]).root
        [7, 9]
    """
