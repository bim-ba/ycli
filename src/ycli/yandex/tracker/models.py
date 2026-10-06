"""Tracker models that several resources share: one class per shape.

The API describes a related object the same way wherever it appears: a reference with its
``self`` link, ``id`` and ``display`` name, sometimes with a ``key`` (a queue, a status) or with
the account ids of a user. The plain reference is the base class and the other two add their
fields to it, whichever resource reads them.
"""

from pydantic import Field

from ycli.yandex.models import APIModel, DisplayStr, KeyStr, RequestBody


class Reference(APIModel):
    """A reference to a related object: its API link, id and display name.

    Examples:
        >>> Reference.model_validate({"id": "1", "display": "Open"}).display
        'Open'
    """

    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the referenced object."
    )
    id: str | None = Field(default=None, description="Identifier of the referenced object.")
    display: str | None = Field(default=None, description="Human-readable name of the object.")


class KeyedReference(Reference):
    """A reference to an object that has a key, such as a queue, a status or a priority.

    Examples:
        >>> KeyedReference.model_validate({"key": "DESIGN", "display": "Design"}).key
        'DESIGN'
    """

    key: str | None = Field(default=None, description="Key of the referenced object.")


class UserReference(Reference):
    """A reference to a user: the reference itself plus the user's account ids.

    Examples:
        >>> UserReference.model_validate({"id": "11", "display": "Ivan Ivanov"}).display
        'Ivan Ivanov'
    """

    cloud_uid: str | None = Field(
        default=None,
        alias="cloudUid",
        description="Unique identifier of the user in Yandex Cloud Organization.",
    )
    passport_uid: int | None = Field(
        default=None,
        alias="passportUid",
        description="Unique identifier of the account in Yandex 360 for Business and Yandex ID.",
    )


class LocalizedName(APIModel):
    """A localized name (the ``name`` object): Russian and/or English text.

    Examples:
        >>> LocalizedName(ru="Поле", en="Field").model_dump(exclude_none=True)
        {'ru': 'Поле', 'en': 'Field'}
    """

    ru: str | None = Field(default=None, description="Name in Russian.")
    en: str | None = Field(default=None, description="Name in English.")


class AttachmentMetadata(APIModel):
    """The ``metadata`` sub-object of an attachment: extra file metadata.

    Present for graphic files, where it carries the image's pixel dimensions.

    Examples:
        >>> AttachmentMetadata.model_validate({"size": "550x175"}).size
        '550x175'
    """

    size: str | None = Field(
        default=None,
        description="Image dimensions in pixels (``WIDTHxHEIGHT``); graphic files only.",
    )


class CommentCreate(RequestBody):
    """Typed request body for adding a comment to an issue or an entity.

    Examples:
        >>> CommentCreate(text="Готово ✅").model_dump(exclude_none=True)
        {'text': 'Готово ✅'}
    """

    text: str = Field(description="Comment text (YFM markdown supported; required).")
    summonees: list[str] | None = Field(
        default=None, description="User ids/logins to summon in the comment."
    )
    attachment_ids: list[str] | None = Field(
        default=None, alias="attachmentIds", description="Temp-file ids to attach as files."
    )
    maillist_summonees: list[str] | None = Field(
        default=None, alias="maillistSummonees", description="Mailing lists to summon."
    )


class OptionsProviderInput(RequestBody):
    """Typed ``optionsProvider`` block for a field create/edit body (a fixed drop-down).

    Examples:
        >>> OptionsProviderInput(type="FixedListOptionsProvider", values=["a", "b"]).model_dump()
        {'type': 'FixedListOptionsProvider', 'values': ['a', 'b']}
    """

    type: str = Field(
        description="Drop-down provider type, e.g. FixedListOptionsProvider or "
        "FixedUserListOptionsProvider."
    )
    values: list[str] = Field(description="Allowed values offered by the drop-down.")


class FieldCreate(RequestBody):
    """Typed request body for creating an issue field, global or local to a queue.

    Examples:
        >>> FieldCreate(
        ...     name=LocalizedName(ru="Поле"), id="myField", category="1", type="StringFieldType"
        ... ).model_dump(exclude_none=True)
        {'name': {'ru': 'Поле'}, 'id': 'myField', 'category': '1', 'type': 'StringFieldType'}
    """

    name: LocalizedName = Field(description="Localized display name of the new field.")
    id: str = Field(description="Identifier (key) of the new field.")
    category: str = Field(
        description="Identifier of the field's category (from GET /fields/categories)."
    )
    type: str = Field(
        description="Field type, e.g. ru.yandex.startrek.core.fields.StringFieldType."
    )
    options_provider: OptionsProviderInput | None = Field(
        default=None,
        serialization_alias="optionsProvider",
        description="Fixed drop-down values, when the field is a limited-choice list.",
    )
    order: int | None = Field(
        default=None, description="Position of the field in the organisation's list of fields."
    )
    description: str | None = Field(default=None, description="Description of the field.")
    readonly: bool | None = Field(
        default=None, description="Whether the value is read-only (true) or editable (false)."
    )


class FieldSchema(APIModel):
    """Data-type descriptor of a field's value (the ``schema`` object).

    Examples:
        >>> FieldSchema.model_validate({"type": "array", "items": "string"}).type
        'array'
    """

    type: str | None = Field(
        default=None,
        description="Value type: string for single-valued fields, array for multi-valued fields.",
    )
    items: str | None = Field(
        default=None, description="Element type; present only on multi-valued (array) fields."
    )
    required: bool | None = Field(
        default=None, description="Whether the field is mandatory (true) or optional (false)."
    )


class LinkType(APIModel):
    """A link type: its id and its names in the inward and outward direction.

    Examples:
        >>> LinkType.model_validate({"id": "relates", "inward": "x", "outward": "y"}).id
        'relates'
    """

    id: str | None = Field(default=None, description="Link type identifier, e.g. ``relates``.")
    inward: str | None = Field(
        default=None, description="Name of the link as seen from the linked issue."
    )
    outward: str | None = Field(
        default=None, description="Name of the link as seen from the requested issue."
    )
    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the link type."
    )


class AutomationAction(APIModel):
    """One action of a trigger or an autoaction (a ``type``-keyed object).

    ``type`` is one of Transition, Update, Move, CreateComment, Webhook, CalculateFormula, … ;
    the type-specific parameters (``status``, ``queue``, ``text`` …) ride along as extra fields
    preserved verbatim.

    Examples:
        >>> AutomationAction.model_validate({"type": "Transition", "status": {"key": "x"}}).type
        'Transition'
    """

    type: str = Field(description="Action type discriminator (e.g. Transition, Update, Webhook).")


class Deadline(APIModel):
    """A deadline block on a checklist item or key result.

    Examples:
        >>> Deadline.model_validate({"date": "2025-12-01", "deadlineType": "date"}).deadline_type
        'date'
    """

    date: str | None = Field(
        default=None, description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm."
    )
    deadline_type: str | None = Field(
        default=None, alias="deadlineType", description="Deadline kind: 'date' or 'quarter'."
    )
    is_exceeded: bool | None = Field(
        default=None, alias="isExceeded", description="Whether the deadline has already passed."
    )


class DeadlineInput(RequestBody):
    """Typed ``deadline`` block for a checklist item or key result write body.

    Examples:
        >>> DeadlineInput(date="2025-12-01T00:00:00.000+0000", deadline_type="date").model_dump()
        {'date': '2025-12-01T00:00:00.000+0000', 'deadlineType': 'date'}
    """

    date: str = Field(description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    deadline_type: str = Field(
        alias="deadlineType", description="Deadline kind: 'date' or 'quarter'."
    )


class AccessHolders(APIModel):
    """Who holds one permission: users, groups and roles (an empty kind is left out by the API).

    Examples:
        >>> AccessHolders.model_validate({"groups": [{"id": "5"}]}).groups[0].id
        '5'
    """

    users: list[UserReference] = Field(
        default_factory=list, description="Users holding the permission personally."
    )
    groups: list[Reference] = Field(
        default_factory=list, description="Groups holding the permission."
    )
    roles: list[Reference] = Field(
        default_factory=list, description="Roles (queue-lead, author, …) holding the permission."
    )


class AccessPermissions(APIModel):
    """The permissions of one subject, keyed by kind; a kind the subject lacks is absent.

    ``grant`` (queue settings) exists on a queue only; a component has create/read/write/deny.

    Examples:
        >>> AccessPermissions.model_validate(
        ...     {"CREATE": {"roles": [{"id": "author"}]}}
        ... ).create.roles[0].id
        'author'
    """

    grant: AccessHolders | None = Field(
        default=None, alias="GRANT", description="Who may change the queue's settings."
    )
    create: AccessHolders | None = Field(
        default=None, alias="CREATE", description="Who may create issues."
    )
    read: AccessHolders | None = Field(
        default=None, alias="READ", description="Who may view issues."
    )
    write: AccessHolders | None = Field(
        default=None, alias="WRITE", description="Who may edit issues."
    )
    deny: AccessHolders | None = Field(
        default=None, alias="DENY", description="Who is denied access."
    )


class IssueChecklistItem(APIModel):
    """A single checklist item (``GET /issues/{key}/checklistItems`` element).

    Examples:
        >>> IssueChecklistItem.model_validate({"id": "5f", "text": "do it", "checked": False}).text
        'do it'
    """

    id: str | None = Field(default=None, description="Checklist item id.")
    text: str | None = Field(default=None, description="Item text.")
    text_html: str | None = Field(
        default=None, alias="textHtml", description="Item text rendered to HTML."
    )
    checked: bool | None = Field(default=None, description="Whether the item is marked done.")
    assignee: DisplayStr = Field(
        default=None, description="Display name of the item assignee, if any."
    )
    deadline: Deadline | None = Field(default=None, description="Per-item deadline, if set.")
    checklist_item_type: str | None = Field(
        default=None, alias="checklistItemType", description="Item type, e.g. 'standard'."
    )


class Issue(APIModel):
    """A Yandex Tracker issue (``/issues/{key}`` response).

    Examples:
        >>> Issue.model_validate({"key": "DE-1", "type": {"key": "task"}}).type
        'task'
    """

    key: str | None = Field(default=None, description="Issue key, e.g. ``TEST-1``.")
    summary: str | None = Field(default=None, description="Issue title.")
    type: KeyStr = Field(default=None, description="Key of the issue type, e.g. ``task``.")
    status: KeyStr = Field(default=None, description="Key of the current status.")
    priority: KeyStr = Field(default=None, description="Key of the priority.")
    epic: KeyStr = Field(default=None, description="Key of the epic the issue belongs to.")
    parent: KeyStr = Field(default=None, description="Key of the parent issue.")
    queue: KeyStr = Field(default=None, description="Key of the queue the issue belongs to.")
    assignee: DisplayStr = Field(default=None, description="Display name of the assignee.")
    tags: list[str] = Field(default_factory=list, description="Tags set on the issue.")
    description: str | None = Field(default=None, description="Issue description (YFM markdown).")
    created_at: str | None = Field(
        default=None, alias="createdAt", description="When the issue was created (ISO 8601)."
    )
    created_by: DisplayStr = Field(
        default=None, alias="createdBy", description="Display name of the issue author."
    )
    self_url: str | None = Field(
        default=None, alias="self", description="API resource URL of the issue."
    )
    id: str | None = Field(default=None, description="Issue identifier.")
    version: int | None = Field(
        default=None, description="Issue version; each change of a field increases it."
    )
    updated_at: str | None = Field(
        default=None, alias="updatedAt", description="When the issue was last changed (ISO 8601)."
    )
    updated_by: UserReference | None = Field(
        default=None, alias="updatedBy", description="The user who last changed the issue."
    )
    status_start_time: str | None = Field(
        default=None,
        alias="statusStartTime",
        description="When the issue entered its current status (ISO 8601).",
    )
    status_type: KeyedReference | None = Field(
        default=None, alias="statusType", description="The type of the current status."
    )
    previous_status: KeyedReference | None = Field(
        default=None, alias="previousStatus", description="The previous status of the issue."
    )
    last_comment_updated_at: str | None = Field(
        default=None,
        alias="lastCommentUpdatedAt",
        description="When the last comment was updated (ISO 8601).",
    )
    comment_with_external_message_count: int | None = Field(
        default=None,
        alias="commentWithExternalMessageCount",
        description="Number of comments with external messages (emails sent from the issue).",
    )
    comment_without_external_message_count: int | None = Field(
        default=None,
        alias="commentWithoutExternalMessageCount",
        description="Number of comments without external messages.",
    )
    followers: list[UserReference] = Field(
        default_factory=list, description="The users following the issue."
    )
    resolution: KeyedReference | None = Field(
        default=None, description="The resolution of the issue, once it has one."
    )
    resolved_at: str | None = Field(
        default=None, alias="resolvedAt", description="When the issue was resolved (ISO 8601)."
    )
    resolved_by: UserReference | None = Field(
        default=None, alias="resolvedBy", description="The user who set the resolution."
    )
    estimation: str | None = Field(
        default=None, description="The estimate of the issue, an ISO 8601 duration."
    )
    original_estimation: str | None = Field(
        default=None,
        alias="originalEstimation",
        description="The original estimate of the issue, an ISO 8601 duration.",
    )
    spent: str | None = Field(
        default=None, description="Time spent on the issue, an ISO 8601 duration."
    )
    votes: int | None = Field(default=None, description="Number of votes for the issue.")
    favorite: bool | None = Field(
        default=None, description="Whether the issue is in the caller's favourites."
    )
    checklist_items: list[IssueChecklistItem] = Field(
        default_factory=list,
        alias="checklistItems",
        description="The items of the issue's checklist (empty once cleared).",
    )
    checklist_total: int | None = Field(
        default=None, alias="checklistTotal", description="Number of checklist items."
    )
    checklist_done: int | str | None = Field(
        default=None, alias="checklistDone", description="Number of checklist items marked done."
    )


class Application(APIModel):
    """An external application that issues can be linked to (``/applications`` item).

    Examples:
        >>> Application.model_validate({"id": "my-app", "name": "My app"}).id
        'my-app'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the application.",
    )
    id: str | None = Field(default=None, description="Unique identifier of the application.")
    type: str | None = Field(
        default=None, description="Type of the application; matches the value of the id parameter."
    )
    name: str | None = Field(default=None, description="Display name of the application.")


class User(APIModel):
    """An organisation user account (``/users/{login_or_id}`` and ``/users/_relative`` item).

    Examples:
        >>> User.model_validate({"uid": 12, "login": "username", "display": "Ivan Ivanov"}).login
        'username'
    """

    self_url: str | None = Field(
        default=None,
        alias="self",
        description="API resource URL that returns full information about the user account.",
    )
    uid: int | None = Field(
        default=None,
        description="Unique identifier of the user account in Tracker (the default id type).",
    )
    login: str | None = Field(default=None, description="Login (username) of the user.")
    tracker_uid: int | None = Field(
        default=None,
        alias="trackerUid",
        description="Unique identifier of the user's account in Tracker.",
    )
    passport_uid: int | None = Field(
        default=None,
        alias="passportUid",
        description="Unique identifier of the account in Yandex 360 for Business and Yandex ID.",
    )
    cloud_uid: str | None = Field(
        default=None,
        alias="cloudUid",
        description="Unique identifier of the user in Yandex Cloud Organization.",
    )
    first_name: str | None = Field(
        default=None, alias="firstName", description="Given name of the user."
    )
    last_name: str | None = Field(
        default=None, alias="lastName", description="Family name of the user."
    )
    display: str | None = Field(default=None, description="Display name of the user.")
    email: str | None = Field(default=None, description="Email address of the user.")
    groups: list[Reference] = Field(
        default_factory=list,
        description="Groups the user belongs to; populated only when expand=groups is requested.",
    )
    external: bool | None = Field(default=None, description="Internal service flag.")
    has_license: bool | None = Field(
        default=None,
        alias="hasLicense",
        description="Whether the user has full Tracker access (true) or read-only access (false).",
    )
    dismissed: bool | None = Field(
        default=None,
        description="Membership status: true if removed from the organisation, false if active.",
    )
    use_new_filters: bool | None = Field(
        default=None, alias="useNewFilters", description="Internal service flag."
    )
    disable_notifications: bool | None = Field(
        default=None,
        alias="disableNotifications",
        description="Whether notifications are force-disabled for the user (true) or enabled.",
    )
    first_login_date: str | None = Field(
        default=None,
        alias="firstLoginDate",
        description="First Tracker sign-in timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    last_login_date: str | None = Field(
        default=None,
        alias="lastLoginDate",
        description="Most recent Tracker sign-in timestamp (YYYY-MM-DDThh:mm:ss.sss±hhmm).",
    )
    welcome_mail_sent: bool | None = Field(
        default=None,
        alias="welcomeMailSent",
        description="How the user was added: true via an email invitation, false another way.",
    )
    sources: list[str] = Field(
        default_factory=list,
        description="Origin of the account data, e.g. the corporate directory.",
    )
    position: str | None = Field(default=None, description="Job title of the user.")
