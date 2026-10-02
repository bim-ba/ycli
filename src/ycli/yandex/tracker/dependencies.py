"""Per-request tracker MCP client provider (see ycli.yandex.mcp.client_provider)."""

from typing import Annotated

from pydantic import Field

from ycli.yandex.mcp import (
    DESTRUCTIVE,
    LIMIT_CAP,
    RO,
    WRITE,
    WRITE_IDEMPOTENT,
    WRITE_TAG,
    app_config,
    client_provider,
)
from ycli.yandex.tracker.client import TrackerClient

TAGS: set[str] = {"tracker"}
WRITE_TAGS: set[str] = TAGS | {WRITE_TAG}
tracker_client = client_provider(TrackerClient)

# Parameter types shared by many tools: one description, reused, so no tool lists a bare id.
IssueKey = Annotated[str, Field(description="Issue key, e.g. QUEUE-123.")]
QueueId = Annotated[
    str, Field(description="Queue key (case-sensitive, e.g. TEST) or numeric queue id.")
]
BoardId = Annotated[int, Field(description="Numeric identifier of the agile board.")]
ColumnId = Annotated[int, Field(description="Numeric identifier of the board column.")]
SprintId = Annotated[int, Field(description="Numeric identifier of the sprint.")]
MacroId = Annotated[
    int, Field(description="Numeric identifier of the macro, from ``macros_list``.")
]
CommentId = Annotated[
    str, Field(description="Comment id (numeric ``id`` or ``longId``), from ``comments_list``.")
]
ChecklistItemId = Annotated[str, Field(description="Checklist item id, from ``checklists_get``.")]
WorklogRecordId = Annotated[str, Field(description="Worklog record id, from ``worklog_list``.")]
Version = Annotated[
    int | None,
    Field(description="Current version of the object (optimistic lock), from its get/list tool."),
]

__all__ = [
    "DESTRUCTIVE",
    "LIMIT_CAP",
    "RO",
    "TAGS",
    "WRITE",
    "WRITE_IDEMPOTENT",
    "WRITE_TAGS",
    "BoardId",
    "ChecklistItemId",
    "ColumnId",
    "CommentId",
    "IssueKey",
    "MacroId",
    "QueueId",
    "SprintId",
    "Version",
    "WorklogRecordId",
    "app_config",
    "tracker_client",
]
