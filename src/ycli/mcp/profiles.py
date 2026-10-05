"""The curated ``core`` toolset: the tools an everyday Tracker / Wiki / Forms session uses.

``--toolsets core`` serves these (with ``status_get`` and ``schema_get``) instead of a whole
service, so a host
that caps a request at 128 tools (VS Code does) or charges tokens per listed tool stays small.
Selection rule: read and edit the work items people touch daily and nothing that administers
the workspace.

| Service | Kept | Left out |
|---|---|---|
| Tracker | issues, comments, transitions, worklog, links, changelog | admin objects, deletes |
| Tracker | attachment, queue and user reads, `me` | boards, sprints, workflows |
| Wiki | page get / create / update / append, subtree, search, comments | grids, access, deletes |
| Forms | survey, question and answer reads | editing, publishing, deletes |

A name here must exist in the full server; ``tests/unit/mcp/test_mcp_selection.py`` keeps that
true and keeps the count between 30 and 50.

Examples:
    >>> "tracker_issues_get" in CORE_TOOLS and "tracker_queues_delete" not in CORE_TOOLS
    True
"""

# The always-served tools: the auth probe an agent needs to explain a failing call, and the
# reader of the schemas a tool does not list (a body over the schema budget).
STATUS_TOOL = "status_get"
SCHEMA_TOOL = "schema_get"
ALWAYS_SERVED = (STATUS_TOOL, SCHEMA_TOOL)

CORE_TOOLS: frozenset[str] = frozenset(
    {
        *ALWAYS_SERVED,
        # Tracker
        "tracker_me_get",
        "tracker_issues_get",
        "tracker_issues_list",
        "tracker_issues_search",
        "tracker_issues_count",
        "tracker_issues_create",
        "tracker_issues_update",
        "tracker_issues_move",
        "tracker_comments_list",
        "tracker_comments_get",
        "tracker_comments_create",
        "tracker_comments_update",
        "tracker_transitions_list",
        "tracker_transitions_execute",
        "tracker_worklog_list",
        "tracker_worklog_create",
        "tracker_worklog_update",
        "tracker_links_list",
        "tracker_links_create",
        "tracker_changelog_list",
        "tracker_attachments_list",
        "tracker_attachments_get",
        "tracker_queues_list",
        "tracker_queues_get",
        "tracker_users_get",
        "tracker_users_list",
        # Wiki
        "wiki_pages_get",
        "wiki_pages_get_by_id",
        "wiki_pages_create",
        "wiki_pages_update",
        "wiki_pages_append",
        "wiki_pages_descendants_list",
        "wiki_pages_search",
        "wiki_comments_list",
        "wiki_comments_create",
        # Forms
        "forms_surveys_list",
        "forms_surveys_get",
        "forms_questions_list",
        "forms_questions_get",
        "forms_answers_list",
        "forms_answers_get",
    }
)
