"""Wiki FastMCP subserver — mounts the per-resource tool servers."""

from fastmcp import FastMCP

from ycli.yandex.wiki.access.mcp import mcp as access_mcp
from ycli.yandex.wiki.attachments.mcp import mcp as attachments_mcp
from ycli.yandex.wiki.comments.mcp import mcp as comments_mcp
from ycli.yandex.wiki.grids.mcp import mcp as grids_mcp
from ycli.yandex.wiki.mcp.prompts import mcp as prompts_mcp
from ycli.yandex.wiki.mcp.resources import mcp as mcp_resources_mcp
from ycli.yandex.wiki.me.mcp import mcp as me_mcp
from ycli.yandex.wiki.operations.mcp import mcp as operations_mcp
from ycli.yandex.wiki.pages.mcp import mcp as pages_mcp
from ycli.yandex.wiki.recovery.mcp import mcp as recovery_mcp
from ycli.yandex.wiki.resources.mcp import mcp as resources_mcp
from ycli.yandex.wiki.uploadsessions.mcp import mcp as uploadsessions_mcp

mcp = FastMCP(
    "wiki",
    instructions=(
        "Yandex Wiki, reads and writes. Pages are addressed by their permanent slug: "
        "pages_get fetches content, pages_get_meta the metadata, pages_descendants_list the child "
        "tree, pages_search finds pages by text; writes (pages_create/pages_update/…, grids_*, "
        "comments_*, access_*, attachments_*) "
        "carry honest readOnly/destructive/idempotent hints and the 'write' tag. Treat slugs as "
        "permanent: pages_move can rename a page but the old address then answers 404, and "
        "pages_clone copies content to a new one; pages_delete returns the "
        "recovery_token that recovery_recover redeems."
    ),
)
mcp.mount(me_mcp)
mcp.mount(pages_mcp)
mcp.mount(access_mcp)
mcp.mount(comments_mcp)
mcp.mount(attachments_mcp)
mcp.mount(resources_mcp)
mcp.mount(recovery_mcp)
mcp.mount(grids_mcp)
mcp.mount(operations_mcp)
mcp.mount(uploadsessions_mcp)
mcp.mount(prompts_mcp)
mcp.mount(mcp_resources_mcp)
