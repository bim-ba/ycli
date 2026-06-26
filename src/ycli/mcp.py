"""Root Yandex 360 FastMCP server — mounts the per-domain subservers.

Run over stdio for LLM-agent clients: ``uv run ycli-mcp`` (or ``python -m ycli.mcp``).
Tools are namespaced per domain: ``wiki_*``, ``tracker_*``, ``forms_*``. Reads-only.
"""

from fastmcp import FastMCP

from ycli.log import configure
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp

mcp = FastMCP("yandex")
mcp.mount(wiki_mcp, namespace="wiki")
mcp.mount(tracker_mcp, namespace="tracker")
mcp.mount(forms_mcp, namespace="forms")


def main() -> None:  # pragma: no cover
    """Run the root server over stdio (the console-script entry point).

    Example:
        >>> main()  # doctest: +SKIP
    """
    configure()  # match the CLI: single stderr sink, stdout stays clean for the protocol
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
