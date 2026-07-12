"""Tracker FastMCP subserver — mounts the per-resource tool servers (reads + writes)."""

from fastmcp import FastMCP

from ycli.yandex.tracker.applications.mcp import mcp as applications_mcp
from ycli.yandex.tracker.attachments.mcp import mcp as attachments_mcp
from ycli.yandex.tracker.autoactions.mcp import mcp as autoactions_mcp
from ycli.yandex.tracker.boards.mcp import mcp as boards_mcp
from ycli.yandex.tracker.bulk.mcp import mcp as bulk_mcp
from ycli.yandex.tracker.changelog.mcp import mcp as changelog_mcp
from ycli.yandex.tracker.checklists.mcp import mcp as checklists_mcp
from ycli.yandex.tracker.columns.mcp import mcp as columns_mcp
from ycli.yandex.tracker.comments.mcp import mcp as comments_mcp
from ycli.yandex.tracker.components.mcp import mcp as components_mcp
from ycli.yandex.tracker.dashboards.mcp import mcp as dashboards_mcp
from ycli.yandex.tracker.entities.mcp import mcp as entities_mcp
from ycli.yandex.tracker.fields.mcp import mcp as fields_mcp
from ycli.yandex.tracker.filters.mcp import mcp as filters_mcp
from ycli.yandex.tracker.import_.mcp import mcp as import_mcp
from ycli.yandex.tracker.issues.mcp import mcp as issues_mcp
from ycli.yandex.tracker.issuetypes.mcp import mcp as issuetypes_mcp
from ycli.yandex.tracker.links.mcp import mcp as links_mcp
from ycli.yandex.tracker.linktypes.mcp import mcp as linktypes_mcp
from ycli.yandex.tracker.localfields.mcp import mcp as localfields_mcp
from ycli.yandex.tracker.macros.mcp import mcp as macros_mcp
from ycli.yandex.tracker.me.mcp import mcp as me_mcp
from ycli.yandex.tracker.priorities.mcp import mcp as priorities_mcp
from ycli.yandex.tracker.queues.mcp import mcp as queues_mcp
from ycli.yandex.tracker.remotelinks.mcp import mcp as remotelinks_mcp
from ycli.yandex.tracker.resolutions.mcp import mcp as resolutions_mcp
from ycli.yandex.tracker.sprints.mcp import mcp as sprints_mcp
from ycli.yandex.tracker.statuses.mcp import mcp as statuses_mcp
from ycli.yandex.tracker.transitions.mcp import mcp as transitions_mcp
from ycli.yandex.tracker.triggers.mcp import mcp as triggers_mcp
from ycli.yandex.tracker.users.mcp import mcp as users_mcp
from ycli.yandex.tracker.worklog.mcp import mcp as worklog_mcp

mcp = FastMCP(
    "tracker",
    instructions=(
        "Yandex Tracker (reads and writes). Reference issues by key (e.g. QUEUE-123). "
        "issues_search / issues_count take a TQL query string; issues_list takes structured "
        "filters (queue/status/assignee/epic/type). Write tools carry honest annotations: "
        "readOnlyHint=false plus destructiveHint/idempotentHint per operation — check them "
        "before mutating; destructive tools delete data irreversibly."
    ),
)
mcp.mount(me_mcp)
mcp.mount(issues_mcp)
mcp.mount(comments_mcp)
mcp.mount(links_mcp)
mcp.mount(transitions_mcp)
mcp.mount(worklog_mcp)
mcp.mount(changelog_mcp)
mcp.mount(checklists_mcp)
mcp.mount(columns_mcp)
mcp.mount(priorities_mcp)
mcp.mount(issuetypes_mcp)
mcp.mount(linktypes_mcp)
mcp.mount(users_mcp)
mcp.mount(statuses_mcp)
mcp.mount(resolutions_mcp)
mcp.mount(queues_mcp)
mcp.mount(localfields_mcp)
mcp.mount(fields_mcp)
mcp.mount(components_mcp)
mcp.mount(filters_mcp)
mcp.mount(applications_mcp)
mcp.mount(boards_mcp)
mcp.mount(sprints_mcp)
mcp.mount(attachments_mcp)
mcp.mount(macros_mcp)
mcp.mount(triggers_mcp)
mcp.mount(autoactions_mcp)
mcp.mount(bulk_mcp)
mcp.mount(remotelinks_mcp)
mcp.mount(import_mcp)
mcp.mount(dashboards_mcp)
mcp.mount(entities_mcp)
