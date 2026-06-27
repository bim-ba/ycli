"""Tracker FastMCP subserver — mounts the per-resource tool servers (reads-only)."""
from fastmcp import FastMCP

from ycli.yandex.tracker.changelog.mcp import mcp as changelog_mcp
from ycli.yandex.tracker.comments.mcp import mcp as comments_mcp
from ycli.yandex.tracker.issues.mcp import mcp as issues_mcp
from ycli.yandex.tracker.issuetypes.mcp import mcp as issuetypes_mcp
from ycli.yandex.tracker.links.mcp import mcp as links_mcp
from ycli.yandex.tracker.linktypes.mcp import mcp as linktypes_mcp
from ycli.yandex.tracker.me.mcp import mcp as me_mcp
from ycli.yandex.tracker.priorities.mcp import mcp as priorities_mcp
from ycli.yandex.tracker.transitions.mcp import mcp as transitions_mcp
from ycli.yandex.tracker.worklog.mcp import mcp as worklog_mcp

mcp = FastMCP(
    "tracker",
    instructions=(
        "Read-only Yandex Tracker. Reference issues by key (e.g. QUEUE-123). "
        "issues_search / issues_count take a TQL query string; issues_list takes structured "
        "filters (queue/status/assignee/epic/type)."
    ),
)
mcp.mount(me_mcp)
mcp.mount(issues_mcp)
mcp.mount(comments_mcp)
mcp.mount(links_mcp)
mcp.mount(transitions_mcp)
mcp.mount(worklog_mcp)
mcp.mount(changelog_mcp)
mcp.mount(priorities_mcp)
mcp.mount(issuetypes_mcp)
mcp.mount(linktypes_mcp)
