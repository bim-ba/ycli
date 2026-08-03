"""Root Yandex 360 FastMCP server — mounts the per-domain subservers.

Run over stdio for LLM-agent clients: ``ycli mcp start`` (or ``python -m ycli.mcp``).
Tools are namespaced per domain: ``wiki_*``, ``tracker_*``, ``forms_*``. Reads and
writes; ``--read-only`` serves the reads-only view.
"""

from fastmcp import FastMCP

from ycli.log import configure
from ycli.settings import AppConfig
from ycli.yandex.forms.mcp import mcp as forms_mcp
from ycli.yandex.mcp import WRITE_TAG
from ycli.yandex.status.mcp import mcp as status_mcp
from ycli.yandex.tracker.mcp import mcp as tracker_mcp
from ycli.yandex.wiki.mcp import mcp as wiki_mcp

mcp = FastMCP(
    "yandex",
    instructions=(
        "Read/write access to Yandex 360: Tracker (issues, comments, worklog, …), "
        "Wiki (pages, grids, attachments), and Forms (surveys, questions, answers). "
        "Tools are namespaced wiki_*, tracker_*, forms_*. Every tool carries honest "
        "annotations: reads have readOnlyHint=true; writes have readOnlyHint=false and "
        "an explicit destructiveHint — treat destructiveHint=true tools (delete/clear/"
        "abort) with care. Credentials come from YANDEX_ID_* OAuth variables or "
        "YANDEX_CLOUD_* IAM variables."
    ),
)
mcp.mount(wiki_mcp, namespace="wiki")
mcp.mount(tracker_mcp, namespace="tracker")
mcp.mount(forms_mcp, namespace="forms")
mcp.mount(status_mcp, namespace="status")


def main(read_only: bool = False) -> None:
    """Run the root server over stdio (the console-script entry point).

    ``read_only=True`` hides every write-tagged tool, restoring the pre-write surface.

    Example:
        >>> main()  # doctest: +SKIP
    """
    configure(
        level=AppConfig().log_level
    )  # match the CLI: single stderr sink, stdout stays clean for the protocol
    if read_only:
        mcp.disable(tags={WRITE_TAG})
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
