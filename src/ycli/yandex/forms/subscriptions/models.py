"""Pydantic models for Forms integrations (subscriptions) of an integration group (hook).

A subscription is one concrete integration that runs on a new answer: an e-mail, a Tracker
issue or comment, a Wiki page, a JSON-RPC or HTTP call, or a Yandex Cloud function. The API
tags each one with ``type``, so :data:`Subscription` is a discriminated union over the seven
types. One class per type serves both directions: ``id`` and the attachment metadata come back
from the server, and :meth:`SubscriptionsClient.create` / ``modify`` never send ``id``.
"""

from typing import Annotated, Any, Literal

from pydantic import Field, SecretStr, TypeAdapter

from ycli.yandex.models import APIModel


class SubscriptionHeader(APIModel):
    """A name/value pair: an e-mail or HTTP header, a JSON-RPC or function parameter.

    Examples:
        >>> SubscriptionHeader(name="X-Source", value="forms").name
        'X-Source'
    """

    name: str | None = Field(default=None, description="Header or parameter name (max 255).")
    value: str | None = Field(
        default=None, description="Value; may embed variables such as {form.name} (max 500)."
    )
    only_with_value: bool | None = Field(
        default=None, description="Send it only when the value is not empty."
    )


class VariableQuestions(APIModel):
    """Which questions a variable covers (``all``, or the listed slugs).

    Examples:
        >>> VariableQuestions(all=False, items=["q1"]).items
        ['q1']
    """

    all: bool | None = Field(default=None, description="Cover every question of the form.")
    items: list[str] | None = Field(default=None, description="Slugs of the covered questions.")


class SubscriptionVariable(APIModel):
    """A variable configured on a subscription and referenced from its texts by ``id``.

    Examples:
        >>> SubscriptionVariable(id="v1", type="form.name").type
        'form.name'
    """

    id: str | None = Field(default=None, description="Variable id, referenced from the texts.")
    type: str | None = Field(
        default=None, description="Variable type, e.g. form.name or form.question_answer."
    )
    name: str | None = Field(default=None, description="Variable display name.")
    renderer: str | None = Field(
        default=None, description="How the value renders: txt, formatted, yfm, json, …."
    )
    filters: list[str] | None = Field(
        default=None, description="Filters applied to the value: md5, base64, lower, upper, …."
    )
    only_with_value: bool | None = Field(
        default=None, description="Render only answered questions."
    )
    show_filenames: bool | None = Field(
        default=None, description="Render file answers as file names."
    )
    question: str | None = Field(
        default=None, description="Question slug the variable reads (single-question types)."
    )
    questions: VariableQuestions | None = Field(
        default=None, description="Questions the variable reads (multi-question types)."
    )
    secret: SecretStr | None = Field(
        default=None, description="Secret value (write only): sent and never printed."
    )
    version: str | None = Field(default=None, description="Variable format version (write only).")


class AttachmentQuestions(APIModel):
    """File questions whose uploads a subscription attaches.

    Examples:
        >>> AttachmentQuestions(all=True).all
        True
    """

    all: bool | None = Field(default=None, description="Attach the files of every question.")
    items: list[str] | None = Field(default=None, description="Slugs of the file questions.")


class StaticAttachment(APIModel):
    """A fixed file attached to every run (sent by ``path``; read back with ``id`` and links).

    Examples:
        >>> StaticAttachment(path="/forms/1/a.pdf").path
        '/forms/1/a.pdf'
    """

    path: str | None = Field(
        default=None, description="Uploaded file path (from `subscriptions attach`)."
    )
    id: int | None = Field(default=None, description="Attachment id (read only).")
    name: str | None = Field(default=None, description="File name (read only).")
    links: dict[str, Any] | None = Field(default=None, description="Download links (read only).")
    check_status: str | None = Field(
        default=None, description="Scan status: check, ready, infected, error, deleted."
    )


class SubscriptionAttachments(APIModel):
    """What a subscription attaches: answer files and fixed files.

    Examples:
        >>> SubscriptionAttachments(question=AttachmentQuestions(all=True)).question.all
        True
    """

    question: AttachmentQuestions | None = Field(
        default=None, description="File questions whose uploads are attached."
    )
    static: list[StaticAttachment] | None = Field(
        default=None, description="Fixed files attached to every run."
    )


class TrackerFieldKey(APIModel):
    """A Tracker issue field addressed by slug.

    Examples:
        >>> TrackerFieldKey(slug="tags").slug
        'tags'
    """

    slug: str | None = Field(default=None, description="Tracker field key, e.g. tags.")
    name: str | None = Field(default=None, description="Field display name.")
    type: str | None = Field(default=None, description="Field type (default string).")


class TrackerField(APIModel):
    """One Tracker issue field a tracker subscription fills.

    Examples:
        >>> TrackerField(key="tags", value="forms").value
        'forms'
    """

    key: str | TrackerFieldKey | None = Field(
        default=None, description="Field key: a slug, or an object with slug/name/type."
    )
    value: str | None = Field(default=None, description="Field value; may embed variables.")
    only_with_value: bool | None = Field(
        default=None, description="Set the field only when the value is not empty."
    )


class WikiFieldKey(APIModel):
    """A Wiki grid column addressed by slug and type.

    Examples:
        >>> WikiFieldKey(slug="name", type="string").type
        'string'
    """

    slug: str | None = Field(default=None, description="Column slug.")
    type: str | None = Field(default=None, description="Column type.")


class WikiField(APIModel):
    """One Wiki grid cell a wiki subscription fills.

    Examples:
        >>> WikiField(key=WikiFieldKey(slug="name", type="string"), value="{form.name}").value
        '{form.name}'
    """

    key: WikiFieldKey | None = Field(default=None, description="The grid column.")
    value: str | None = Field(default=None, description="Cell value; may embed variables.")


class WikiGrid(APIModel):
    """A Wiki grid a wiki subscription appends rows to.

    Examples:
        >>> WikiGrid(grid_id="g1", cols=[]).grid_id
        'g1'
    """

    grid_id: str | None = Field(default=None, description="Grid id.")
    title: str | None = Field(default=None, description="Grid title.")
    cols: list[WikiField] | None = Field(default=None, description="The cells of a new row.")


class _SubscriptionBase(APIModel):
    """Fields every subscription type shares."""

    # violation(api-drift): one model builds the body and reads the reply, which carries `id`
    id: int | None = Field(default=None, description="Subscription id (integer, read only).")
    active: bool | None = Field(default=None, description="Whether the integration runs.")
    follow: bool | None = Field(
        default=None, description="Notify the form's followers about the run."
    )
    variables: list[SubscriptionVariable] | None = Field(
        default=None, description="Variables referenced from the subscription's texts."
    )


class EmailSubscription(_SubscriptionBase):
    """Send an e-mail.

    Examples:
        >>> EmailSubscription(email_to_address="team@example.com").type
        'email'
    """

    type: Literal["email"] = Field(default="email", description="Discriminator: email.")
    subject: str | None = Field(default=None, description="Message subject (max 255).")
    body: str | None = Field(default=None, description="Message body.")
    email_to_address: str | None = Field(default=None, description="Recipient (max 255).")
    email_from_title: str | None = Field(default=None, description="Sender name (max 255).")
    headers: list[SubscriptionHeader] | None = Field(
        default=None, description="Extra message headers."
    )
    attachments: SubscriptionAttachments | None = Field(
        default=None, description="Files to attach."
    )


class TrackerSubscription(_SubscriptionBase):
    """Create a Tracker issue.

    Examples:
        >>> TrackerSubscription(queue="SUPPORT").type
        'tracker'
    """

    type: Literal["tracker"] = Field(default="tracker", description="Discriminator: tracker.")
    subject: str | None = Field(default=None, description="Issue summary.")
    body: str | None = Field(default=None, description="Issue description.")
    queue: str | None = Field(default=None, description="Queue key (max 255).")
    parent: str | None = Field(default=None, description="Parent issue key.")
    author: str | None = Field(default=None, description="Issue author login.")
    assignee: str | None = Field(default=None, description="Assignee login.")
    issue_type: int | None = Field(default=None, description="Issue type id.")
    priority: int | None = Field(default=None, description="Priority id.")
    fields: list[TrackerField] | None = Field(default=None, description="Other issue fields.")
    attachments: SubscriptionAttachments | None = Field(
        default=None, description="Files to attach."
    )


class TrackerCommentSubscription(_SubscriptionBase):
    """Comment on a Tracker issue.

    Examples:
        >>> TrackerCommentSubscription(issue="SUPPORT-1").type
        'tracker_comment'
    """

    type: Literal["tracker_comment"] = Field(
        default="tracker_comment", description="Discriminator: tracker_comment."
    )
    issue: str | None = Field(default=None, description="Issue key to comment on.")
    body: str | None = Field(default=None, description="Comment text.")
    fields: list[TrackerField] | None = Field(default=None, description="Issue fields to set.")
    attachments: SubscriptionAttachments | None = Field(
        default=None, description="Files to attach."
    )


class WikiSubscription(_SubscriptionBase):
    """Write to a Wiki page (text, or a row of a grid).

    Examples:
        >>> WikiSubscription(supertag="team/answers").type
        'wiki'
    """

    type: Literal["wiki"] = Field(default="wiki", description="Discriminator: wiki.")
    supertag: str | None = Field(default=None, description="Wiki page slug (max 255).")
    body: str | None = Field(default=None, description="Text to write.")
    insert_to_begin: bool | None = Field(
        default=None, description="Insert at the top of the page instead of the bottom."
    )
    grid_data: list[WikiField] | WikiGrid | None = Field(
        default=None, description="Grid row to add: a list of cells, or a grid with its cells."
    )


class JSONRPCSubscription(_SubscriptionBase):
    """Call a JSON-RPC method.

    Examples:
        >>> JSONRPCSubscription(method="answers.add").type
        'jsonrpc'
    """

    type: Literal["jsonrpc"] = Field(default="jsonrpc", description="Discriminator: jsonrpc.")
    url: str | None = Field(default=None, description="Endpoint URL (max 255).")
    method: str | None = Field(default=None, description="JSON-RPC method name (max 255).")
    params: list[SubscriptionHeader] | None = Field(default=None, description="Call parameters.")
    headers: list[SubscriptionHeader] | None = Field(default=None, description="HTTP headers.")


class HTTPSubscription(_SubscriptionBase):
    """Send an HTTP request.

    Examples:
        >>> HTTPSubscription(url="https://example.com/hook", method="post").method
        'post'
    """

    type: Literal["http"] = Field(default="http", description="Discriminator: http.")
    url: str | None = Field(default=None, description="Request URL (max 255).")
    method: Literal["get", "post", "patch", "put", "delete"] | str | None = Field(
        default=None, description="HTTP method: get, post, patch, put or delete."
    )
    body: str | None = Field(default=None, description="Request body; may embed variables.")
    headers: list[SubscriptionHeader] | None = Field(default=None, description="HTTP headers.")


class FunctionSubscription(_SubscriptionBase):
    """Call a Yandex Cloud function.

    Examples:
        >>> FunctionSubscription(function_id="d4e1").type
        'function'
    """

    type: Literal["function"] = Field(default="function", description="Discriminator: function.")
    function_id: str | None = Field(default=None, description="Cloud function id (max 255).")
    params: list[SubscriptionHeader] | None = Field(
        default=None, description="Function parameters."
    )


Subscription = Annotated[
    EmailSubscription
    | TrackerSubscription
    | TrackerCommentSubscription
    | WikiSubscription
    | JSONRPCSubscription
    | HTTPSubscription
    | FunctionSubscription,
    Field(discriminator="type"),
]
SubscriptionAdapter: TypeAdapter[Subscription] = TypeAdapter(Subscription)
