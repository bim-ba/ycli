"""Root Yandex 360 FastMCP server — mounts the per-domain subservers.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per domain: ``wiki_*``, ``tracker_*``, ``forms_*``. Reads-only.
"""

from fastmcp import FastMCP

from ycli.log import configure
from ycli.settings import AppConfig
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp

mcp = FastMCP(
    "yandex",
    instructions=(
        "Read-only access to Yandex 360: Tracker (issues, comments, worklog, …), "
        "Wiki (pages, attachments), and Forms. Tools are namespaced wiki_*, tracker_*, "
        "forms_*, and are all read-only — create/update happens via the ycli CLI/SDK, not "
        "here. Credentials come from the YANDEX_ID_OAUTH_TOKEN and "
        "YANDEX_ID_ORGANIZATION_ID environment variables."
    ),
)
mcp.mount(wiki_mcp, namespace="wiki")
mcp.mount(tracker_mcp, namespace="tracker")
mcp.mount(forms_mcp, namespace="forms")


def main() -> None:
    """Run the root server over stdio (the console-script entry point).

    Example:
        >>> main()  # doctest: +SKIP
    """
    configure(
        level=AppConfig().log_level
    )  # match the CLI: single stderr sink, stdout stays clean for the protocol
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
