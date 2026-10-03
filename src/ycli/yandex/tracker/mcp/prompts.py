"""Tracker MCP prompts: ready requests over the Tracker tools, offered by the client's UI.

A prompt's text names the tools to call; ``NEEDS_TOOLS`` lists them, so a server that does not
serve one of them does not offer the prompt.
"""

from fastmcp import FastMCP

from ycli.yandex.mcp import NEEDS_TOOLS
from ycli.yandex.tracker.dependencies import TAGS

mcp = FastMCP("tracker-prompts")


@mcp.prompt(
    name="queue_digest",
    title="Digest of a queue's open issues",
    tags=TAGS,
    meta={NEEDS_TOOLS: ["tracker_issues_count", "tracker_issues_search"]},
)
def queue_digest(queue: str) -> str:
    """Summarise the open issues of a Tracker queue: how many, what is stuck, who holds what.

    Args:
        queue: Queue key, e.g. TEST.

    Returns:
        The request for the model.
    """
    return (
        f"Give me a digest of the open issues in the Yandex Tracker queue {queue}.\n\n"
        f"1. Call tracker_issues_count with query `Queue: {queue} Resolution: empty()` for the "
        "total.\n"
        "2. Call tracker_issues_search with the same query and "
        '`"Sort by": Updated ASC` appended, limit 50: the issues untouched the longest come '
        "first.\n"
        "3. Answer with: the total; a table of counts by status and by assignee; the five issues "
        "untouched the longest (key, summary, assignee, last update); and anything that looks "
        "blocked or has no assignee.\n\n"
        "Quote issue keys as they are. If the search returned fewer issues than the total, say "
        "that the breakdown covers only those."
    )


@mcp.prompt(
    name="issue_brief",
    title="Brief on one issue",
    tags=TAGS,
    meta={
        NEEDS_TOOLS: [
            "tracker_changelog_list",
            "tracker_comments_list",
            "tracker_issues_get",
            "tracker_links_list",
        ]
    },
)
def issue_brief(key: str) -> str:
    """Brief me on one Tracker issue: where it stands, what was decided, what blocks it.

    Args:
        key: Issue key, e.g. QUEUE-123.

    Returns:
        The request for the model.
    """
    return (
        f"Brief me on the Yandex Tracker issue {key}.\n\n"
        f"Call tracker_issues_get, tracker_comments_list, tracker_links_list and "
        f"tracker_changelog_list for {key}, then answer with:\n\n"
        "- what the issue asks for, in two sentences;\n"
        "- its status, assignee and deadline, and how long it has been in this status "
        "(from the changelog);\n"
        "- the decisions and open questions in the comments, each with its author;\n"
        "- linked issues that block it or depend on it;\n"
        "- the next step, and who it is waiting for.\n\n"
        "Keep to what the issue says: mark anything you infer as an inference."
    )


@mcp.prompt(
    name="sprint_review",
    title="Review of a sprint",
    tags=TAGS,
    meta={NEEDS_TOOLS: ["tracker_issues_search", "tracker_sprints_list"]},
)
def sprint_review(board_id: str, sprint: str = "") -> str:
    """Review a sprint of a Tracker board: what was done, what slipped, what to carry over.

    Args:
        board_id: Numeric id of the agile board.
        sprint: Sprint id or name; empty means the board's current sprint.

    Returns:
        The request for the model.
    """
    which = (
        f"the sprint whose id or name is {sprint!r}"
        if sprint
        else "the sprint in progress (status `in_progress`)"
    )
    return (
        f"Review a sprint of the Yandex Tracker board {board_id}.\n\n"
        f"1. Call tracker_sprints_list with board_id {board_id} and take {which}.\n"
        '2. Call tracker_issues_search with query `Sprint: "<the sprint\'s name>"`, limit 200.\n'
        "3. Answer with: the sprint's name and dates; counts of issues done, in progress and not "
        "started; the issues done (key, summary, assignee); the issues that will not make it and "
        "why it looks so; and what to carry over to the next sprint.\n\n"
        "Quote issue keys as they are and do not change any issue."
    )
