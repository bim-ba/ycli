# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Any, Literal

from pydantic import ConfigDict, Field

from ycli.yandex.models import APIModel


class CurrentTenantDetailsSettings(APIModel):
    """Public tenant settings. Additional public settings may be returned."""

    model_config = ConfigDict(
        extra="allow",
    )
    __annotations__ = {
        "__pydantic_extra__": dict[str, Any],
    }
    data_export_prohibited: bool | None = Field(
        default=None,
        alias="dataExportProhibited",
        description="Whether exporting data is prohibited for the tenant.",
    )
    prohibition_publication: bool | None = Field(
        default=None,
        alias="prohibitionPublication",
        description="Whether entries publication is prohibited for the tenant.",
    )
    workbook_file_export_prohibited: bool | None = Field(
        default=None,
        alias="workbookFileExportProhibited",
        description="Whether workbooks export is prohibited for the tenant.",
    )
    default_color_palette_id: str | None = Field(
        default=None,
        alias="defaultColorPaletteId",
        description="ID of the default color palette.",
    )
    ai_assistant_prohibited: bool | None = Field(
        default=None,
        alias="aiAssistantProhibited",
        description="Whether the Neuroanalyst is prohibited for the tenant.",
    )
    ai_chat_history_prohibited: bool | None = Field(
        default=None,
        alias="aiChatHistoryProhibited",
        description="Whether storing Neuroanalyst chat history is prohibited for the tenant.",
    )
    sharing_prohibited: bool | None = Field(
        default=None,
        alias="sharingProhibited",
        description="Whether creating temporary public links is prohibited for the tenant.",
    )
    new_object_creator_role: Literal["admin", "editor", "none"] | str | None = Field(
        default=None,
        alias="newObjectCreatorRole",
        description="Default role assigned to the creator of a new object.",
    )
    default_sidebar_mode: Literal["simplified", "full"] | str | None = Field(
        default=None,
        alias="defaultSidebarMode",
        description="Default sidebar display mode.",
    )
    auto_assign_licenses: bool | None = Field(
        default=None,
        alias="autoAssignLicenses",
        description="Whether seats are assigned automatically.",
    )
    auto_buy_licenses: bool | None = Field(
        default=None,
        alias="autoBuyLicenses",
        description="Whether additional seats are purchased automatically.",
    )
    auto_buy_licenses_limit: int | float | None = Field(
        default=None,
        alias="autoBuyLicensesLimit",
        description="Maximum number of seats that can be purchased automatically.",
    )


class CurrentTenantDetails(APIModel):
    tenant_id: str | None = Field(
        default=None, alias="tenantId", description="ID of the current DataLens tenant."
    )
    org_id: str | None = Field(
        default=None,
        alias="orgId",
        description="ID of the organization. Null when the tenant has no organization.",
    )
    settings: CurrentTenantDetailsSettings | None = None
    dlp_enabled: bool | None = Field(
        default=None,
        alias="dlpEnabled",
        description="Whether DataLens Platform mode is enabled for the tenant.",
    )
    folders_enabled: bool | None = Field(
        default=None,
        alias="foldersEnabled",
        description="Whether legacy folder navigation is enabled for the tenant.",
    )
