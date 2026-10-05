# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from .shared import EntryLocationIdentifiers


class GetHtmlPageArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId", description="ID of the HTML page to retrieve.")
    rev_id: str | None = Field(
        default=None,
        alias="revId",
        description="ID of the HTML page revision to retrieve.",
    )
    branch: Literal["saved", "published"] | str | None = Field(
        default=None, description="HTML page branch to retrieve."
    )
    include_permissions: bool | None = Field(
        default=None,
        alias="includePermissions",
        description="Whether to include HTML page permissions.",
    )
    include_favorite: bool | None = Field(
        default=None,
        alias="includeFavorite",
        description="Whether to include the favorite status.",
    )


class DeleteHtmlPageArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId", description="ID of the HTML page to delete.")


class GetHtmlPagePreviewUrlResult(APIModel):
    url: str | None = Field(default=None, description="Temporary URL for previewing the HTML page.")


class GetHtmlPagePreviewUrlArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId", description="ID of the HTML page to preview.")
    branch: Literal["saved", "published"] | str | None = Field(
        default=None, description="HTML page branch to preview. Defaults to published."
    )
    rev_id: str | None = Field(
        default=None,
        alias="revId",
        description="ID of the HTML page revision to preview.",
    )
    lang: Literal["ru", "en"] | str | None = Field(
        default=None, description="Language of the HTML page preview."
    )
    theme: Literal["light", "dark", "light-hc", "dark-hc", "system"] | str | None = Field(
        default=None, description="Theme of the HTML page preview."
    )


class DeleteHtmlPageResponse(APIModel):
    pass


class CreateHtmlPageResultEntryMeta(APIModel):
    """Metadata of the HTML page."""

    object_id: str | None = Field(
        default=None,
        alias="objectId",
        description="ID of the object containing the HTML content.",
    )
    policy_version: int | float | None = Field(
        default=None,
        alias="policyVersion",
        description="Version of the security policy injected into the HTML content.",
    )


class CreateHtmlPageResultEntryAnnotation(APIModel):
    """Annotation of the HTML page."""

    description: str | None = Field(default=None, description="Description of the entry.")


class CreateHtmlPageResultEntryPermissions(APIModel):
    """Permissions for the HTML page."""

    execute: bool | None = Field(
        default=None, description="Indicates if there are permissions to execute."
    )
    read: bool | None = Field(
        default=None, description="Indicates if there are permissions to read."
    )
    edit: bool | None = Field(
        default=None, description="Indicates if there are permissions to edit."
    )
    admin: bool | None = Field(
        default=None, description="Indicates if there are permissions for admin."
    )


class CreateHtmlPageArgsAnnotation(APIModel):
    """Annotation of the HTML page."""

    description: str | None = Field(default=None, description="Description of the entry.")


class GetHtmlPageResultMeta(APIModel):
    """Metadata of the HTML page."""

    object_id: str | None = Field(
        default=None,
        alias="objectId",
        description="ID of the object containing the HTML content.",
    )
    policy_version: int | float | None = Field(
        default=None,
        alias="policyVersion",
        description="Version of the security policy injected into the HTML content.",
    )


class GetHtmlPageResultAnnotation(APIModel):
    """Annotation of the HTML page."""

    description: str | None = Field(default=None, description="Description of the entry.")


class GetHtmlPageResultPermissions(APIModel):
    """Permissions for the HTML page."""

    execute: bool | None = Field(
        default=None, description="Indicates if there are permissions to execute."
    )
    read: bool | None = Field(
        default=None, description="Indicates if there are permissions to read."
    )
    edit: bool | None = Field(
        default=None, description="Indicates if there are permissions to edit."
    )
    admin: bool | None = Field(
        default=None, description="Indicates if there are permissions for admin."
    )


class UpdateHtmlPageResultEntryMeta(APIModel):
    """Metadata of the HTML page."""

    object_id: str | None = Field(
        default=None,
        alias="objectId",
        description="ID of the object containing the HTML content.",
    )
    policy_version: int | float | None = Field(
        default=None,
        alias="policyVersion",
        description="Version of the security policy injected into the HTML content.",
    )


class UpdateHtmlPageResultEntryAnnotation(APIModel):
    """Annotation of the HTML page."""

    description: str | None = Field(default=None, description="Description of the entry.")


class UpdateHtmlPageResultEntryPermissions(APIModel):
    """Permissions for the HTML page."""

    execute: bool | None = Field(
        default=None, description="Indicates if there are permissions to execute."
    )
    read: bool | None = Field(
        default=None, description="Indicates if there are permissions to read."
    )
    edit: bool | None = Field(
        default=None, description="Indicates if there are permissions to edit."
    )
    admin: bool | None = Field(
        default=None, description="Indicates if there are permissions for admin."
    )


class UpdateHtmlPageArgsVariant1Annotation(APIModel):
    """New annotation of the HTML page."""

    description: str | None = Field(default=None, description="Description of the entry.")


class UpdateHtmlPageArgsVariant2(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="ID of the HTML page to update."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="ID of the revision to use."
    )
    mode: Literal["save", "publish"] | str | None = Field(
        default=None, description="HTML page revision update mode."
    )


class CreateHtmlPageArgs(EntryLocationIdentifiers):
    content: str | None = Field(default=None, description="HTML content of the page.")
    annotation: CreateHtmlPageArgsAnnotation | None = None


class GetHtmlPageResult(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the HTML page."
    )
    scope: Literal["artifact"] = Field(..., description="Scope of the HTML page entry.")
    type: Literal["html-page"] = Field(..., description="Type of the HTML page entry.")
    key: str | None = Field(default=None, description="Key of the HTML page entry.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook containing the HTML page.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection containing the HTML page.",
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="ID of the current HTML page revision."
    )
    saved_id: str | None = Field(
        default=None, alias="savedId", description="ID of the saved HTML page revision."
    )
    published_id: str | None = Field(
        default=None,
        alias="publishedId",
        description="ID of the published HTML page revision.",
    )
    data: dict[str, Any] | None = Field(
        default=None, description="Versioned data of the HTML page entry."
    )
    meta: GetHtmlPageResultMeta | None = None
    annotation: GetHtmlPageResultAnnotation | None = None
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the HTML page.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the HTML page was created.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the HTML page.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the HTML page was last updated.",
    )
    rev_updated_by: str | None = Field(
        default=None,
        alias="revUpdatedBy",
        description="ID of the user who last updated the current revision.",
    )
    rev_updated_at: str | None = Field(
        default=None,
        alias="revUpdatedAt",
        description="Date and time when the current revision was last updated.",
    )
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the HTML page.",
    )
    hidden: bool | None = Field(default=None, description="Whether the HTML page is hidden.")
    version: Literal[1] = Field(..., description="Schema version of the HTML page.")
    public: bool | None = Field(default=None, description="Whether the HTML page is public.")
    links: dict[str, Any] | None = Field(
        default=None, description="Links associated with the HTML page."
    )
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Whether the HTML page is a favorite.",
    )
    permissions: GetHtmlPageResultPermissions | None = None


class CreateHtmlPageResultEntry(APIModel):
    """Created HTML page entry."""

    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the HTML page."
    )
    scope: Literal["artifact"] = Field(..., description="Scope of the HTML page entry.")
    type: Literal["html-page"] = Field(..., description="Type of the HTML page entry.")
    key: str | None = Field(default=None, description="Key of the HTML page entry.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook containing the HTML page.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection containing the HTML page.",
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="ID of the current HTML page revision."
    )
    saved_id: str | None = Field(
        default=None, alias="savedId", description="ID of the saved HTML page revision."
    )
    published_id: str | None = Field(
        default=None,
        alias="publishedId",
        description="ID of the published HTML page revision.",
    )
    data: dict[str, Any] | None = Field(
        default=None, description="Versioned data of the HTML page entry."
    )
    meta: CreateHtmlPageResultEntryMeta | None = None
    annotation: CreateHtmlPageResultEntryAnnotation | None = None
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the HTML page.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the HTML page was created.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the HTML page.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the HTML page was last updated.",
    )
    rev_updated_by: str | None = Field(
        default=None,
        alias="revUpdatedBy",
        description="ID of the user who last updated the current revision.",
    )
    rev_updated_at: str | None = Field(
        default=None,
        alias="revUpdatedAt",
        description="Date and time when the current revision was last updated.",
    )
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the HTML page.",
    )
    hidden: bool | None = Field(default=None, description="Whether the HTML page is hidden.")
    version: Literal[1] = Field(..., description="Schema version of the HTML page.")
    public: bool | None = Field(default=None, description="Whether the HTML page is public.")
    links: dict[str, Any] | None = Field(
        default=None, description="Links associated with the HTML page."
    )
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Whether the HTML page is a favorite.",
    )
    permissions: CreateHtmlPageResultEntryPermissions | None = None


class UpdateHtmlPageResultEntry(APIModel):
    """Updated HTML page entry."""

    entry_id: str | None = Field(
        default=None, alias="entryId", description="Unique identifier of the HTML page."
    )
    scope: Literal["artifact"] = Field(..., description="Scope of the HTML page entry.")
    type: Literal["html-page"] = Field(..., description="Type of the HTML page entry.")
    key: str | None = Field(default=None, description="Key of the HTML page entry.")
    workbook_id: str | None = Field(
        default=None,
        alias="workbookId",
        description="ID of the workbook containing the HTML page.",
    )
    collection_id: str | None = Field(
        default=None,
        alias="collectionId",
        description="ID of the collection containing the HTML page.",
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="ID of the current HTML page revision."
    )
    saved_id: str | None = Field(
        default=None, alias="savedId", description="ID of the saved HTML page revision."
    )
    published_id: str | None = Field(
        default=None,
        alias="publishedId",
        description="ID of the published HTML page revision.",
    )
    data: dict[str, Any] | None = Field(
        default=None, description="Versioned data of the HTML page entry."
    )
    meta: UpdateHtmlPageResultEntryMeta | None = None
    annotation: UpdateHtmlPageResultEntryAnnotation | None = None
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the HTML page.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the HTML page was created.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the HTML page.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the HTML page was last updated.",
    )
    rev_updated_by: str | None = Field(
        default=None,
        alias="revUpdatedBy",
        description="ID of the user who last updated the current revision.",
    )
    rev_updated_at: str | None = Field(
        default=None,
        alias="revUpdatedAt",
        description="Date and time when the current revision was last updated.",
    )
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the HTML page.",
    )
    hidden: bool | None = Field(default=None, description="Whether the HTML page is hidden.")
    version: Literal[1] = Field(..., description="Schema version of the HTML page.")
    public: bool | None = Field(default=None, description="Whether the HTML page is public.")
    links: dict[str, Any] | None = Field(
        default=None, description="Links associated with the HTML page."
    )
    is_favorite: bool | None = Field(
        default=None,
        alias="isFavorite",
        description="Whether the HTML page is a favorite.",
    )
    permissions: UpdateHtmlPageResultEntryPermissions | None = None


class UpdateHtmlPageArgsVariant1(APIModel):
    entry_id: str | None = Field(
        default=None, alias="entryId", description="ID of the HTML page to update."
    )
    content: str | None = Field(default=None, description="New HTML content of the page.")
    annotation: UpdateHtmlPageArgsVariant1Annotation | None = None
    mode: Literal["save", "publish"] | str | None = Field(
        default=None, description="HTML page update mode."
    )


class CreateHtmlPageResult(APIModel):
    entry: CreateHtmlPageResultEntry | None = None
    warnings: list[str] | None = Field(
        default=None,
        description="Warning codes generated while processing the HTML content.",
    )


class UpdateHtmlPageResult(APIModel):
    entry: UpdateHtmlPageResultEntry | None = None
    warnings: list[str] | None = Field(
        default=None,
        description="Warning codes generated while processing the HTML content.",
    )


class UpdateHtmlPageArgs(RootModel[UpdateHtmlPageArgsVariant1 | UpdateHtmlPageArgsVariant2]):
    root: UpdateHtmlPageArgsVariant1 | UpdateHtmlPageArgsVariant2
