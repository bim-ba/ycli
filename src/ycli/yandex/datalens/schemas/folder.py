# Generated from the DataLens specification by scripts/gen_datalens_models.py; do not edit by hand.

from __future__ import annotations

from typing import Literal

from pydantic import Field, RootModel

from ycli.yandex.models import APIModel, RequestBody

from . import shared


class DlsInitialPermissionItem(APIModel):
    comment: str = Field(
        ..., description="Comment describing the reason for this initial permission."
    )
    subject: str = Field(..., description="Subject identifier.")


class GetPermissionsArgs(RequestBody):
    entry_id: str = Field(
        ..., alias="entryId", description="ID of the entry to get permissions for."
    )


class ModifyPermissionsResult(APIModel):
    result: Literal["ok"]
    next_page_token: str | None = Field(
        default=None,
        alias="nextPageToken",
        description="Token for fetching the next page of results.",
    )


class DlsSuggestArgs(RequestBody):
    search_text: str = Field(
        ..., alias="searchText", description="Text to search for permission subjects."
    )


class DeleteFolderArgs(RequestBody):
    folder_id: str = Field(..., alias="folderId", description="ID of the folder to delete.")


class MoveEntryResultEntry(APIModel):
    entry_id: str | None = Field(default=None, alias="entryId", description="ID of the entry.")
    key: str | None = Field(default=None, description="Key identifier of the entry.")
    scope: shared.EntryScope | None = None
    type: str | None = Field(default=None, description="Type of the entry.")


class MoveEntryResult(RootModel[list[MoveEntryResultEntry]]):
    """Entries affected by the move operation."""

    root: list[MoveEntryResultEntry] = Field(
        ..., description="Entries affected by the move operation."
    )


class MoveEntryArgs(RequestBody):
    entry_id: str = Field(..., alias="entryId", description="ID of the entry to move.")
    destination: str = Field(..., description="Destination path for the entry.")
    name: str | None = Field(default=None, description="New name for the entry at destination.")


class DeleteFolderResponse(APIModel):
    pass


class CreateFolderResultUnversionedData(APIModel):
    """Unversioned data of the folder."""


class CreateFolderResultData(APIModel):
    """Versioned data of the folder."""


class CreateFolderResultMeta(APIModel):
    """Metadata of the folder."""


class CreateFolderArgsInitialPermissions(APIModel):
    """Initial permissions for the folder."""

    acl_adm: list[DlsInitialPermissionItem] | None = Field(
        default=None, description="Initial admin permissions."
    )
    acl_edit: list[DlsInitialPermissionItem] | None = Field(
        default=None, description="Initial edit permissions."
    )
    acl_view: list[DlsInitialPermissionItem] | None = Field(
        default=None, description="Initial view permissions."
    )
    acl_execute: list[DlsInitialPermissionItem] | None = Field(
        default=None, description="Initial execute permissions."
    )


class DlsPermissionPendingParticipantExtrasVariant2(APIModel):
    initial_on_create: bool | None = Field(
        default=None, description="Whether to set this permission on entry creation."
    )


class DlsPermissionPendingParticipantRequesterParent(APIModel):
    """Parent group information."""

    link: str | None = Field(default=None, description="Link to the parent group.")
    title: str | None = Field(default=None, description="Display title of the parent group.")


class DlsPermissionPendingParticipantSubjectParent(APIModel):
    """Parent group information."""

    link: str | None = Field(default=None, description="Link to the parent group.")
    title: str | None = Field(default=None, description="Display title of the parent group.")


class DlsPermissionParticipantApproverParent(APIModel):
    """Parent group information."""

    link: str | None = Field(default=None, description="Link to the parent group.")
    title: str | None = Field(default=None, description="Display title of the parent group.")


class DlsPermissionParticipantExtrasVariant2(APIModel):
    initial_on_create: bool | None = Field(
        default=None, description="Whether to set this permission on entry creation."
    )


class DlsPermissionParticipantRequesterParent(APIModel):
    """Parent group information."""

    link: str | None = Field(default=None, description="Link to the parent group.")
    title: str | None = Field(default=None, description="Display title of the parent group.")


class DlsPermissionParticipantSubjectParent(APIModel):
    """Parent group information."""

    link: str | None = Field(default=None, description="Link to the parent group.")
    title: str | None = Field(default=None, description="Display title of the parent group.")


class ModifyPermissionsArgsBodyDiffAddedAclAdmItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffAddedAclEditItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffAddedAclViewItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffAddedAclExecuteItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffRemovedAclAdmItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffRemovedAclEditItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffRemovedAclViewItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffRemovedAclExecuteItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")


class ModifyPermissionsArgsBodyDiffModifiedAclAdmItemNew(APIModel):
    grant_type: Literal["acl_view", "acl_edit", "acl_adm", "acl_execute"] | str = Field(
        ..., alias="grantType", description="New ACL level to assign to the subject."
    )
    subject: str = Field(..., description="New subject identifier after modification.")


class ModifyPermissionsArgsBodyDiffModifiedAclEditItemNew(APIModel):
    grant_type: Literal["acl_view", "acl_edit", "acl_adm", "acl_execute"] | str = Field(
        ..., alias="grantType", description="New ACL level to assign to the subject."
    )
    subject: str = Field(..., description="New subject identifier after modification.")


class ModifyPermissionsArgsBodyDiffModifiedAclViewItemNew(APIModel):
    grant_type: Literal["acl_view", "acl_edit", "acl_adm", "acl_execute"] | str = Field(
        ..., alias="grantType", description="New ACL level to assign to the subject."
    )
    subject: str = Field(..., description="New subject identifier after modification.")


class ModifyPermissionsArgsBodyDiffModifiedAclExecuteItemNew(APIModel):
    grant_type: Literal["acl_view", "acl_edit", "acl_adm", "acl_execute"] | str = Field(
        ..., alias="grantType", description="New ACL level to assign to the subject."
    )
    subject: str = Field(..., description="New subject identifier after modification.")


class DlsPermissionUnitParent(APIModel):
    """Parent group information."""

    link: str | None = Field(default=None, description="Link to the parent group.")
    title: str | None = Field(default=None, description="Display title of the parent group.")


class CreateFolderResult(APIModel):
    entry_id: str | None = Field(
        default=None,
        alias="entryId",
        description="Unique identifier of the created folder.",
    )
    scope: Literal["folder"] = Field(..., description="Scope of the created entry.")
    type: Literal[""] = Field(..., description="Type of the created folder entry.")
    key: str | None = Field(default=None, description="Key of the created folder.")
    unversioned_data: CreateFolderResultUnversionedData | None = Field(
        default=None, alias="unversionedData"
    )
    created_by: str | None = Field(
        default=None,
        alias="createdBy",
        description="ID of the user who created the folder.",
    )
    created_at: str | None = Field(
        default=None,
        alias="createdAt",
        description="Date and time when the folder was created.",
    )
    updated_by: str | None = Field(
        default=None,
        alias="updatedBy",
        description="ID of the user who last updated the folder.",
    )
    updated_at: str | None = Field(
        default=None,
        alias="updatedAt",
        description="Date and time when the folder was last updated.",
    )
    saved_id: str | None = Field(
        default=None, alias="savedId", description="ID of the saved folder revision."
    )
    rev_id: str | None = Field(
        default=None, alias="revId", description="ID of the current folder revision."
    )
    published_id: str | None = Field(
        default=None,
        alias="publishedId",
        description="ID of the published folder revision.",
    )
    tenant_id: str | None = Field(
        default=None,
        alias="tenantId",
        description="ID of the tenant that owns the folder.",
    )
    data: CreateFolderResultData | None = None
    meta: CreateFolderResultMeta | None = None
    annotation: None = Field(default=None, description="Annotation of the folder.")
    hidden: bool | None = Field(default=None, description="Whether the folder is hidden.")
    mirrored: bool | None = Field(default=None, description="Whether the folder is mirrored.")
    public: bool | None = Field(default=None, description="Whether the folder is public.")
    workbook_id: None = Field(
        default=None,
        alias="workbookId",
        description="Workbook ID associated with the folder.",
    )
    collection_id: None = Field(
        default=None,
        alias="collectionId",
        description="Collection ID associated with the folder.",
    )
    version: None = Field(default=None, description="Folder schema version.")
    source_version: None = Field(
        default=None, alias="sourceVersion", description="Source folder schema version."
    )
    links: None = Field(default=None, description="Links associated with the folder.")


class CreateFolderArgs(RequestBody):
    key: str = Field(..., description="Key of the folder to create.")
    initial_permissions: CreateFolderArgsInitialPermissions | None = Field(
        default=None, alias="initialPermissions"
    )


class DlsPermissionUnit(APIModel):
    cloud_icon: str | None = Field(default=None, description="Cloud icon URL for the subject.")
    cloud_icon_data: str | None = Field(
        default=None, description="Cloud icon raw data for the subject."
    )
    cloud_user_id: str | None = Field(default=None, description="Cloud platform user ID.")
    icon: str | None = Field(default=None, description="Icon URL for the subject.")
    link: str | None = Field(default=None, description="Profile link for the subject.")
    name: str | None = Field(default=None, description="Subject id.")
    title: str | None = Field(default=None, description="Display title for the subject.")
    type: (
        Literal[
            "user",
            "user-staff",
            "user-system",
            "group-system",
            "group-staff-servicerole",
            "group-staff-service",
            "group-staff-wiki",
            "group-staff-department",
        ]
        | str
        | None
    ) = Field(default=None, description="Subject type.")
    parent: DlsPermissionUnitParent | None = None
    field__rlsid: str | None = Field(
        default=None, alias="__rlsid", description="Row-level security identifier."
    )
    field__source: str | None = Field(
        default=None, alias="__source", description="Source system identifier."
    )


class DlsSuggestResult(RootModel[list[DlsPermissionUnit]]):
    """List of matching DLS subjects."""

    root: list[DlsPermissionUnit] = Field(..., description="List of matching DLS subjects.")


class DlsPermissionPendingParticipantRequester(APIModel):
    """User who submitted the permission request."""

    cloud_icon: str | None = Field(default=None, description="Cloud icon URL for the subject.")
    cloud_icon_data: str | None = Field(
        default=None, description="Cloud icon raw data for the subject."
    )
    cloud_user_id: str | None = Field(default=None, description="Cloud platform user ID.")
    icon: str | None = Field(default=None, description="Icon URL for the subject.")
    link: str | None = Field(default=None, description="Profile link for the subject.")
    name: str | None = Field(default=None, description="Subject id.")
    title: str | None = Field(default=None, description="Display title for the subject.")
    type: (
        Literal[
            "user",
            "user-staff",
            "user-system",
            "group-system",
            "group-staff-servicerole",
            "group-staff-service",
            "group-staff-wiki",
            "group-staff-department",
        ]
        | str
        | None
    ) = Field(default=None, description="Subject type.")
    parent: DlsPermissionPendingParticipantRequesterParent | None = None
    field__rlsid: str | None = Field(
        default=None, alias="__rlsid", description="Row-level security identifier."
    )
    field__source: str | None = Field(
        default=None, alias="__source", description="Source system identifier."
    )


class DlsPermissionPendingParticipantSubject(APIModel):
    """Subject details."""

    cloud_icon: str | None = Field(default=None, description="Cloud icon URL for the subject.")
    cloud_icon_data: str | None = Field(
        default=None, description="Cloud icon raw data for the subject."
    )
    cloud_user_id: str | None = Field(default=None, description="Cloud platform user ID.")
    icon: str | None = Field(default=None, description="Icon URL for the subject.")
    link: str | None = Field(default=None, description="Profile link for the subject.")
    name: str | None = Field(default=None, description="Subject id.")
    title: str | None = Field(default=None, description="Display title for the subject.")
    type: (
        Literal[
            "user",
            "user-staff",
            "user-system",
            "group-system",
            "group-staff-servicerole",
            "group-staff-service",
            "group-staff-wiki",
            "group-staff-department",
        ]
        | str
        | None
    ) = Field(default=None, description="Subject type.")
    parent: DlsPermissionPendingParticipantSubjectParent | None = None
    field__rlsid: str | None = Field(
        default=None, alias="__rlsid", description="Row-level security identifier."
    )
    field__source: str | None = Field(
        default=None, alias="__source", description="Source system identifier."
    )


class DlsPermissionParticipantApprover(APIModel):
    """User who approved this permission."""

    cloud_icon: str | None = Field(default=None, description="Cloud icon URL for the subject.")
    cloud_icon_data: str | None = Field(
        default=None, description="Cloud icon raw data for the subject."
    )
    cloud_user_id: str | None = Field(default=None, description="Cloud platform user ID.")
    icon: str | None = Field(default=None, description="Icon URL for the subject.")
    link: str | None = Field(default=None, description="Profile link for the subject.")
    name: str | None = Field(default=None, description="Subject id.")
    title: str | None = Field(default=None, description="Display title for the subject.")
    type: (
        Literal[
            "user",
            "user-staff",
            "user-system",
            "group-system",
            "group-staff-servicerole",
            "group-staff-service",
            "group-staff-wiki",
            "group-staff-department",
        ]
        | str
        | None
    ) = Field(default=None, description="Subject type.")
    parent: DlsPermissionParticipantApproverParent | None = None
    field__rlsid: str | None = Field(
        default=None, alias="__rlsid", description="Row-level security identifier."
    )
    field__source: str | None = Field(
        default=None, alias="__source", description="Source system identifier."
    )


class DlsPermissionParticipantRequester(APIModel):
    """User who requested this permission."""

    cloud_icon: str | None = Field(default=None, description="Cloud icon URL for the subject.")
    cloud_icon_data: str | None = Field(
        default=None, description="Cloud icon raw data for the subject."
    )
    cloud_user_id: str | None = Field(default=None, description="Cloud platform user ID.")
    icon: str | None = Field(default=None, description="Icon URL for the subject.")
    link: str | None = Field(default=None, description="Profile link for the subject.")
    name: str | None = Field(default=None, description="Subject id.")
    title: str | None = Field(default=None, description="Display title for the subject.")
    type: (
        Literal[
            "user",
            "user-staff",
            "user-system",
            "group-system",
            "group-staff-servicerole",
            "group-staff-service",
            "group-staff-wiki",
            "group-staff-department",
        ]
        | str
        | None
    ) = Field(default=None, description="Subject type.")
    parent: DlsPermissionParticipantRequesterParent | None = None
    field__rlsid: str | None = Field(
        default=None, alias="__rlsid", description="Row-level security identifier."
    )
    field__source: str | None = Field(
        default=None, alias="__source", description="Source system identifier."
    )


class DlsPermissionParticipantSubject(APIModel):
    """Subject details."""

    cloud_icon: str | None = Field(default=None, description="Cloud icon URL for the subject.")
    cloud_icon_data: str | None = Field(
        default=None, description="Cloud icon raw data for the subject."
    )
    cloud_user_id: str | None = Field(default=None, description="Cloud platform user ID.")
    icon: str | None = Field(default=None, description="Icon URL for the subject.")
    link: str | None = Field(default=None, description="Profile link for the subject.")
    name: str | None = Field(default=None, description="Subject id.")
    title: str | None = Field(default=None, description="Display title for the subject.")
    type: (
        Literal[
            "user",
            "user-staff",
            "user-system",
            "group-system",
            "group-staff-servicerole",
            "group-staff-service",
            "group-staff-wiki",
            "group-staff-department",
        ]
        | str
        | None
    ) = Field(default=None, description="Subject type.")
    parent: DlsPermissionParticipantSubjectParent | None = None
    field__rlsid: str | None = Field(
        default=None, alias="__rlsid", description="Row-level security identifier."
    )
    field__source: str | None = Field(
        default=None, alias="__source", description="Source system identifier."
    )


class ModifyPermissionsArgsBodyDiffAdded(APIModel):
    """Permissions to add."""

    acl_adm: list[ModifyPermissionsArgsBodyDiffAddedAclAdmItem] | None = Field(
        default=None, description="Subjects to grant admin access."
    )
    acl_edit: list[ModifyPermissionsArgsBodyDiffAddedAclEditItem] | None = Field(
        default=None, description="Subjects to grant edit access."
    )
    acl_view: list[ModifyPermissionsArgsBodyDiffAddedAclViewItem] | None = Field(
        default=None, description="Subjects to grant view access."
    )
    acl_execute: list[ModifyPermissionsArgsBodyDiffAddedAclExecuteItem] | None = Field(
        default=None, description="Subjects to grant execute access."
    )


class ModifyPermissionsArgsBodyDiffRemoved(APIModel):
    """Permissions to remove."""

    acl_adm: list[ModifyPermissionsArgsBodyDiffRemovedAclAdmItem] | None = Field(
        default=None, description="Subjects to revoke admin access from."
    )
    acl_edit: list[ModifyPermissionsArgsBodyDiffRemovedAclEditItem] | None = Field(
        default=None, description="Subjects to revoke edit access from."
    )
    acl_view: list[ModifyPermissionsArgsBodyDiffRemovedAclViewItem] | None = Field(
        default=None, description="Subjects to revoke view access from."
    )
    acl_execute: list[ModifyPermissionsArgsBodyDiffRemovedAclExecuteItem] | None = Field(
        default=None, description="Subjects to revoke execute access from."
    )


class ModifyPermissionsArgsBodyDiffModifiedAclAdmItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")
    new: ModifyPermissionsArgsBodyDiffModifiedAclAdmItemNew


class ModifyPermissionsArgsBodyDiffModifiedAclEditItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")
    new: ModifyPermissionsArgsBodyDiffModifiedAclEditItemNew


class ModifyPermissionsArgsBodyDiffModifiedAclViewItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")
    new: ModifyPermissionsArgsBodyDiffModifiedAclViewItemNew


class ModifyPermissionsArgsBodyDiffModifiedAclExecuteItem(APIModel):
    comment: str | None = Field(
        default=None,
        description="Comment describing the reason for this permission change.",
    )
    subject: str = Field(..., description="Subject identifier.")
    new: ModifyPermissionsArgsBodyDiffModifiedAclExecuteItemNew


class DlsPermissionPendingParticipant(APIModel):
    approver: None = Field(default=None, description="Always null for pending permissions.")
    description: str | None = Field(
        default=None,
        description="Human-readable description of the pending permission request.",
    )
    extras: DlsPermissionPendingParticipantExtrasVariant2 | None = Field(
        default=None, description="Additional configuration for the permission request."
    )
    kind: Literal["user", "group"] | str | None = Field(
        default=None, description="Participant kind."
    )
    name: str | None = Field(default=None, description="Subject id.")
    requester: DlsPermissionPendingParticipantRequester | None = None
    subject: DlsPermissionPendingParticipantSubject | None = None


class DlsPermissionParticipant(APIModel):
    approver: DlsPermissionParticipantApprover | None = None
    description: str | None = Field(
        default=None, description="Human-readable description of the permission."
    )
    extras: DlsPermissionParticipantExtrasVariant2 | None = Field(
        default=None, description="Additional configuration for the permission."
    )
    kind: Literal["user", "group"] | str | None = Field(
        default=None, description="Participant kind."
    )
    name: str | None = Field(default=None, description="Subject id.")
    requester: DlsPermissionParticipantRequester | None = None
    subject: DlsPermissionParticipantSubject | None = None


class GetPermissionsResultPendingPermissions(APIModel):
    """Pending permission requests grouped by ACL level."""

    acl_adm: list[DlsPermissionPendingParticipant] | None = Field(
        default=None, description="Pending admin access requests."
    )
    acl_edit: list[DlsPermissionPendingParticipant] | None = Field(
        default=None, description="Pending edit access requests."
    )
    acl_view: list[DlsPermissionPendingParticipant] | None = Field(
        default=None, description="Pending view access requests."
    )
    acl_execute: list[DlsPermissionPendingParticipant] | None = Field(
        default=None, description="Pending execute access requests."
    )


class GetPermissionsResultPermissions(APIModel):
    """Granted permissions grouped by ACL level."""

    acl_adm: list[DlsPermissionParticipant] | None = Field(
        default=None, description="Participants with admin access."
    )
    acl_edit: list[DlsPermissionParticipant] | None = Field(
        default=None, description="Participants with edit access."
    )
    acl_view: list[DlsPermissionParticipant] | None = Field(
        default=None, description="Participants with view access."
    )
    acl_execute: list[DlsPermissionParticipant] | None = Field(
        default=None, description="Participants with execute access."
    )


class ModifyPermissionsArgsBodyDiffModified(APIModel):
    """Permissions to modify."""

    acl_adm: list[ModifyPermissionsArgsBodyDiffModifiedAclAdmItem] | None = Field(
        default=None, description="Admin permission modifications."
    )
    acl_edit: list[ModifyPermissionsArgsBodyDiffModifiedAclEditItem] | None = Field(
        default=None, description="Edit permission modifications."
    )
    acl_view: list[ModifyPermissionsArgsBodyDiffModifiedAclViewItem] | None = Field(
        default=None, description="View permission modifications."
    )
    acl_execute: list[ModifyPermissionsArgsBodyDiffModifiedAclExecuteItem] | None = Field(
        default=None, description="Execute permission modifications."
    )


class GetPermissionsResult(APIModel):
    editable: bool | None = Field(
        default=None,
        description="Whether the current user can edit permissions for this entry.",
    )
    pending_permissions: GetPermissionsResultPendingPermissions | None = Field(
        default=None, alias="pendingPermissions"
    )
    permissions: GetPermissionsResultPermissions | None = None


class ModifyPermissionsArgsBodyDiff(APIModel):
    """Set of permission changes to apply."""

    added: ModifyPermissionsArgsBodyDiffAdded | None = None
    removed: ModifyPermissionsArgsBodyDiffRemoved | None = None
    modified: ModifyPermissionsArgsBodyDiffModified | None = None


class ModifyPermissionsArgsBody(APIModel):
    """Permission changes to apply."""

    diff: ModifyPermissionsArgsBodyDiff


class ModifyPermissionsArgs(RequestBody):
    entry_id: str = Field(
        ..., alias="entryId", description="ID of the entry to modify permissions for."
    )
    body: ModifyPermissionsArgsBody
    check_type: Literal["straight", "hierarchical", "root"] | str | None = Field(
        default=None,
        alias="checkType",
        description="Scope of permission check: straight (direct), hierarchical, or root.",
    )
    nested: bool | None = Field(
        default=None, description="Apply changes recursively to all nested entries."
    )
    page: float | None = Field(default=None, description="Page number for paginated results.")
    page_size: float | None = Field(
        default=None, alias="pageSize", description="Number of results per page."
    )
