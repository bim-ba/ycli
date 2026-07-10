"""Forms FastMCP subserver — mounts the per-resource tool servers (reads-only)."""

from fastmcp import FastMCP

from ycli.yandex.forms.answers.mcp import mcp as answers_mcp
from ycli.yandex.forms.files.mcp import mcp as files_mcp
from ycli.yandex.forms.filling.mcp import mcp as filling_mcp
from ycli.yandex.forms.images.mcp import mcp as images_mcp
from ycli.yandex.forms.keysets.mcp import mcp as keysets_mcp
from ycli.yandex.forms.me.mcp import mcp as me_mcp
from ycli.yandex.forms.operations.mcp import mcp as operations_mcp
from ycli.yandex.forms.questions.mcp import mcp as questions_mcp
from ycli.yandex.forms.surveys.mcp import mcp as surveys_mcp

mcp = FastMCP(
    "forms",
    instructions=(
        "Read-only Yandex Forms. Reference a survey by id: surveys_list enumerates them, "
        "questions_list / answers_list drill into one."
    ),
)
mcp.mount(me_mcp)
mcp.mount(surveys_mcp)
mcp.mount(questions_mcp)
mcp.mount(answers_mcp)
mcp.mount(keysets_mcp)
mcp.mount(operations_mcp)
mcp.mount(files_mcp)
mcp.mount(images_mcp)
mcp.mount(filling_mcp)
