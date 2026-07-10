"""Pydantic models for Tracker issue types (IssueType + IssueTypeList + write bodies)."""

from __future__ import annotations

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel


class IssueType(APIModel):
    """An issue type descriptor (``/issuetypes`` item).

    Example:
        >>> IssueType.model_validate({"key": "task", "display": "Task"}).key
        'task'
    """

    key: str | None = None
    display: str | None = None


class IssueTypeList(RootModel[list[IssueType]]):
    """A bare JSON array of issue types.

    Example:
        >>> IssueTypeList.model_validate([{"key": "bug"}]).root[0].key
        'bug'
    """


class LocalizedName(APIModel):
    """A localized display name (the ``name`` object) — Russian and/or English text.

    Example:
        >>> LocalizedName(ru="Клиент", en="Customer").model_dump(exclude_none=True)
        {'ru': 'Клиент', 'en': 'Customer'}
    """

    ru: str | None = Field(default=None, description="Name in Russian.")
    en: str | None = Field(default=None, description="Name in English.")


class IssueTypeCreate(APIModel):
    """Typed request body for ``POST /issuetypes/`` (create an issue type).

    Example:
        >>> IssueTypeCreate(key="client", name=LocalizedName(ru="Клиент")).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'key': 'client', 'name': {'ru': 'Клиент'}}
    """

    key: str = Field(description="Key of the new issue type.")
    name: LocalizedName = Field(description="Localized display name of the issue type.")


class IssueTypeUpdate(APIModel):
    """Typed request body for ``PATCH /issuetypes/{id}?version=`` (edit an issue type).

    Only the fields that are set are sent, so omitted fields stay unchanged.

    Example:
        >>> IssueTypeUpdate(name=LocalizedName(ru="Покупатель")).model_dump(
        ...     by_alias=True, exclude_none=True
        ... )
        {'name': {'ru': 'Покупатель'}}
    """

    name: LocalizedName | None = Field(
        default=None, description="New localized display name of the issue type."
    )
