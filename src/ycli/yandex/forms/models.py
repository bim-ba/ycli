"""Forms models that several resources share: one class per shape."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ycli.yandex.models import APIModel

#: Statuses at which a background operation has stopped running.
TERMINAL_STATUSES = frozenset({"ok", "fail"})

#: How a quiz result is shown to the respondent.
QuizShowFormat = Literal["score_with_total", "score", "percent", "text", "off"] | str
#: Where the virus scan of an uploaded file stands.
FileCheckStatus = Literal["check", "ready", "infected", "error", "deleted"] | str
#: The state of one run of an integration.
RunStatus = Literal["pending", "success", "error", "canceled"] | str
#: The kind of integration a run belongs to.
IntegrationType = (
    Literal[
        "email", "tracker", "tracker_comment", "wiki", "jsonrpc", "post", "put", "http", "function"
    ]
    | str
)


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


class OperationOutcome(APIModel):
    """What a finished operation produced (``result`` of an operation).

    Examples:
        >>> OperationOutcome(status=302, href="https://forms.test/file").status
        302
    """

    status: int | None = Field(default=None, description="HTTP status the operation ended with.")
    href: str | None = Field(default=None, description="URL to follow for the result.")


class OperationResult(APIModel):
    """The status of a Forms background operation: ``{id, status, message, result}``.

    A long-running action (an answers export) answers with an operation ``id``; re-read its
    status until :attr:`is_terminal`. ``status`` is one of ``ok`` (finished, result ready),
    ``fail``, ``wait`` (still running) or ``not_running``.

    Examples:
        >>> OperationResult.model_validate({"id": "op-1", "status": "ok"}).is_ready
        True
    """

    id: str | None = Field(
        default=None, description="Operation id (echoes the id an async trigger returned)."
    )
    status: str | None = Field(
        default=None,
        description="Operation status: one of ``ok``, ``fail``, ``wait``, ``not_running``.",
    )
    message: str | None = Field(default=None, description="Human-readable operation message.")
    result: OperationOutcome | None = Field(
        default=None, description="What a finished operation produced."
    )

    @property
    def is_terminal(self) -> bool:
        """``True`` once ``status`` reached a terminal value (see :data:`TERMINAL_STATUSES`)."""
        return self.status in TERMINAL_STATUSES

    @property
    def is_ready(self) -> bool:
        """``True`` when the operation finished successfully (``status == "ok"``)."""
        return self.status == "ok"


ConditionOperatorType = Literal["and", "or"] | str
ConditionItemKind = Literal["question", "language", "origin", "quiz"] | str
ConditionComparison = Literal["eq", "neq", "lt", "gt"] | str


class ConditionItem(APIModel):
    """One clause inside a display-condition group.

    Examples:
        >>> ConditionItem(type="question", condition="eq", question="q1", value="yes").value
        'yes'
    """

    condition: ConditionComparison | None = Field(
        default=None, description="Comparison operator: eq, neq, lt, gt."
    )
    operator: ConditionOperatorType | None = Field(
        default=None, description="Boolean operator joining this clause to the next: and / or."
    )
    type: ConditionItemKind | None = Field(
        default=None, description="Clause subject: question, language, origin or quiz."
    )
    question: str | None = Field(
        default=None, description="Slug of the question this clause tests (for type=question)."
    )
    value: str | None = Field(default=None, description="Value the clause compares against.")


class Condition(APIModel):
    """A display-condition group (the question shows only when the group matches).

    Examples:
        >>> Condition(operator="and", items=[ConditionItem(question="q1")]).operator
        'and'
    """

    id: int | None = Field(default=None, description="Condition group ID.")
    operator: str | None = Field(default=None, description="Operator combining the group's items.")
    items: list[ConditionItem] | None = Field(
        default=None, description="Clauses evaluated within this group."
    )


class ConditionsResponse(APIModel):
    """The ``{operator, items}`` envelope of a target's condition groups.

    Returned by every ``*_list`` and ``*_set_operator`` operation. Unlike the transport
    envelopes that the resource conventions flatten, ``operator`` here is data (the boolean
    operator BETWEEN the groups), so the envelope itself is the public return type.

    Examples:
        >>> ConditionsResponse.model_validate(
        ...     {"operator": "and", "items": [{"id": 1, "operator": "or", "items": []}]}
        ... ).items[0].id
        1
    """

    operator: ConditionOperatorType | None = Field(
        default=None, description="Boolean operator joining the condition groups: and / or."
    )
    items: list[Condition] = Field(
        default_factory=list, description="The target's condition groups."
    )


class FileOut(APIModel):
    """A file stored for form filling (``upload`` result and each ``verify`` item).

    A ``File``-type form field is filled by first uploading the file here; the returned
    ``path`` / ``url`` then reference it in a form response. ``check_status`` reports the
    antivirus/upload scan.

    Examples:
        >>> FileOut.model_validate(
        ...     {"name": "cv.pdf", "path": "p", "size": 12, "url": "u", "check_status": "ready"}
        ... ).check_status
        'ready'
    """

    name: str | None = Field(default=None, description="File name.")
    path: str | None = Field(
        default=None, description="File download path (pass to download / verify / delete)."
    )
    size: int | None = Field(default=None, description="File size in bytes.")
    url: str | None = Field(default=None, description="File download URL.")
    check_status: FileCheckStatus | None = Field(
        default=None,
        description="Virus/upload scan status — one of: check, ready, infected, error, deleted.",
    )
