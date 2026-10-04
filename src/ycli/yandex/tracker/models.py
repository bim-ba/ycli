"""Tracker models that several resources share: one class per shape.

The API describes a related object the same way wherever it appears: a reference with its
``self`` link, ``id`` and ``display`` name, sometimes with a ``key`` (a queue, a status) or with
the account ids of a user. The plain reference is the base class and the other two add their
fields to it, whichever resource reads them.
"""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel, RequestBody


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

    id: str | None = None
    inward: str | None = None
    outward: str | None = None


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
        >>> DeadlineInput(date="2025-12-01T00:00:00.000+0000").model_dump()
        {'date': '2025-12-01T00:00:00.000+0000', 'deadlineType': 'date'}
    """

    date: str = Field(description="Deadline date, YYYY-MM-DDThh:mm:ss.sss±hhmm.")
    deadline_type: str = Field(
        default="date", alias="deadlineType", description="Deadline kind: 'date' or 'quarter'."
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
