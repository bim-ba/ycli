"""Wiki MCP prompts: ready requests over the Wiki tools, offered by the client's UI.

A prompt's text names the tools to call; ``NEEDS_TOOLS`` lists them, so a server that does not
serve one of them does not offer the prompt.
"""

from fastmcp import FastMCP

from ycli.yandex.mcp import NEEDS_TOOLS
from ycli.yandex.wiki.dependencies import WRITE_TAGS

mcp = FastMCP("wiki-prompts")


@mcp.prompt(
    name="page_from_issue",
    title="Draft a Wiki page from a Tracker issue",
    tags=WRITE_TAGS,
    meta={NEEDS_TOOLS: ["tracker_comments_list", "tracker_issues_get", "wiki_pages_create"]},
)
def page_from_issue(key: str, parent_slug: str) -> str:
    """Draft a Wiki page from a Tracker issue and its discussion, then create it once approved.

    Args:
        key: Issue key, e.g. QUEUE-123.
        parent_slug: Slug of the page the new one goes under, e.g. team/decisions.

    Returns:
        The request for the model.
    """
    return (
        f"Write a Yandex Wiki page from the Yandex Tracker issue {key}.\n\n"
        f"1. Call tracker_issues_get and tracker_comments_list for {key}.\n"
        "2. Draft the page in Markdown: the context, what was decided and why, the alternatives "
        f"that were rejected, the open questions, and a link back to {key}. Leave out the "
        "back-and-forth; keep the names of who decided what.\n"
        f"3. Show me the draft, the title and the slug you propose under {parent_slug}/, and "
        "wait for my answer.\n"
        "4. Only after I approve, call wiki_pages_create with that slug, title and content, and "
        "give me the new page's slug.\n\n"
        "Do not create or change anything before step 4."
    )
