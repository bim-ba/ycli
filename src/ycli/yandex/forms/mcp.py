"""Forms FastMCP subserver — mounts the per-resource tool servers (reads-only)."""
from fastmcp import FastMCP

from ycli.yandex.forms.answers.mcp import mcp as answers_mcp
from ycli.yandex.forms.me.mcp import mcp as me_mcp
from ycli.yandex.forms.questions.mcp import mcp as questions_mcp
from ycli.yandex.forms.surveys.mcp import mcp as surveys_mcp

mcp = FastMCP("forms")
mcp.mount(me_mcp)
mcp.mount(surveys_mcp)
mcp.mount(questions_mcp)
mcp.mount(answers_mcp)
