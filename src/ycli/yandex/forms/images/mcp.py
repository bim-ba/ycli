"""Forms images FastMCP subserver — intentionally tool-less.

ARCH-1 gives every resource package the four surface files, but the only endpoint here is a
multipart image **upload** (a write), so this subserver registers no tools. It is created for
symmetry and mounts cleanly; upload the image via the CLI or SDK.
"""

from fastmcp import FastMCP

mcp = FastMCP("forms-images")
