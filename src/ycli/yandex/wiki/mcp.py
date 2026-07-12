"""Wiki FastMCP subserver — mounts the per-resource tool servers."""

from fastmcp import FastMCP

from ycli.yandex.wiki.attachments.mcp import mcp as attachments_mcp
from ycli.yandex.wiki.comments.mcp import mcp as comments_mcp
from ycli.yandex.wiki.grids.mcp import mcp as grids_mcp
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
        "pages_get fetches content, pages_meta the metadata, pages_descendants the child "
        "tree; writes (pages_create/pages_update/…, grids_*, comments_*, attachments_*) "
        "carry honest readOnly/destructive/idempotent hints and the 'write' tag. Slugs are "
        "permanent — only pages_clone gives content a new address; pages_delete returns the "
        "recovery_token that recovery_restore redeems."
    ),
)
mcp.mount(me_mcp)
mcp.mount(pages_mcp)
mcp.mount(comments_mcp)
mcp.mount(attachments_mcp)
mcp.mount(resources_mcp)
mcp.mount(recovery_mcp)
mcp.mount(grids_mcp)
mcp.mount(operations_mcp)
mcp.mount(uploadsessions_mcp)
