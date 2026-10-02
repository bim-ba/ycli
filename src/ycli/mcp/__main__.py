"""``python -m ycli.mcp`` — run the MCP server (reads and writes) over stdio."""

from ycli.log import configure
from ycli.mcp.selection import Selection
from ycli.mcp.server import main
from ycli.settings import AppConfig

if __name__ == "__main__":  # pragma: no cover
    # `ycli mcp start` is configured by the CLI root; this direct entry configures itself.
    logging_config = AppConfig().logging
    configure(level=logging_config.level, log_format=logging_config.format)
    main(Selection())
