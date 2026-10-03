"""Tracker models that several resources share: one class per shape.

The API describes a related object the same way wherever it appears: a reference with its
``self`` link, ``id`` and ``display`` name, sometimes with a ``key`` (a queue, a status) or with
the account ids of a user. The plain reference is the base class and the other two add their
fields to it, whichever resource reads them.
"""

from __future__ import annotations

from pydantic import Field

from ycli.yandex.models import APIModel


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


class CommentCreate(APIModel):
    """Typed request body for adding a comment to an issue or an entity.

    Examples:
        >>> CommentCreate(text="Готово ✅").model_dump(by_alias=True, exclude_none=True)
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


class OptionsProviderInput(APIModel):
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
