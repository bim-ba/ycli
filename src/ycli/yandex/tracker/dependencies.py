"""Per-request tracker MCP client provider (see ycli.yandex.mcp.client_provider)."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.mcp import (
    DESTRUCTIVE,
    GRANTS_ACCESS,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    All,
    Next,
    app_config,
    client_provider,
    new_server,
)
from ycli.yandex.tracker.client import TrackerClient

TAGS: set[str] = {"tracker"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
tracker_client = client_provider(TrackerClient)

# Parameter types shared by many tools: one description, reused, so no tool lists a bare id.
IssueKey = Annotated[str, Field(description="Issue key, e.g. QUEUE-123.")]
QueueID = Annotated[
    str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
]
BoardID = Annotated[int, Field(description="Numeric identifier of the agile board.")]
ColumnID = Annotated[int, Field(description="Numeric identifier of the board column.")]
SprintID = Annotated[int, Field(description="Numeric identifier of the sprint.")]
MacroID = Annotated[
    int, Field(description="Numeric identifier of the macro, from ``macros_list``.")
]
CommentID = Annotated[
    int | str,
    Field(description="Comment id (numeric ``id`` or ``longId``), from ``comments_list``."),
]
ChecklistItemID = Annotated[str, Field(description="Checklist item id, from ``checklists_list``.")]
WorklogRecordID = Annotated[str, Field(description="Worklog record id, from ``worklog_list``.")]
# The parameters most write operations share: what the reply carries and who is notified.
Expand = Annotated[str | None, Field(description="Extra blocks to include in the reply.")]
ReplyFields = Annotated[
    str | None, Field(description="Comma-separated fields to include in the reply.")
]
Notify = Annotated[
    bool | None,
    Field(description="Notify the users in the fields of the object; omitted, the API notifies."),
]
NotifyAuthor = Annotated[
    bool | None,
    Field(description="Notify the author of the change; omitted, the API does not."),
]
AddToFollowers = Annotated[
    bool | None,
    Field(description="Add the comment's author to the followers; omitted, the API adds."),
]
Version = Annotated[
    int | None,
    Field(description="Current version of the object (optimistic lock), from its get/list tool."),
]

__all__ = [
    "DESTRUCTIVE",
    "GRANTS_ACCESS",
    "LIMIT_CAP",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "All",
    "BoardID",
    "ChecklistItemID",
    "ColumnID",
    "CommentID",
    "IssueKey",
    "MacroID",
    "Next",
    "QueueID",
    "SprintID",
    "Version",
    "WorklogRecordID",
    "app_config",
    "new_server",
    "tracker_client",
]
