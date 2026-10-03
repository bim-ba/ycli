"""Forms FastMCP subserver — mounts the per-resource tool servers (reads + writes)."""

from fastmcp import FastMCP

from ycli.yandex.forms.access.mcp import mcp as access_mcp
from ycli.yandex.forms.answers.mcp import mcp as answers_mcp
from ycli.yandex.forms.conditions.mcp import mcp as conditions_mcp
from ycli.yandex.forms.files.mcp import mcp as files_mcp
from ycli.yandex.forms.filling.mcp import mcp as filling_mcp
from ycli.yandex.forms.history.mcp import mcp as history_mcp
from ycli.yandex.forms.hooks.mcp import mcp as hooks_mcp
from ycli.yandex.forms.images.mcp import mcp as images_mcp
from ycli.yandex.forms.keysets.mcp import mcp as keysets_mcp
from ycli.yandex.forms.me.mcp import mcp as me_mcp
from ycli.yandex.forms.notifications.mcp import mcp as notifications_mcp
from ycli.yandex.forms.operations.mcp import mcp as operations_mcp
from ycli.yandex.forms.questions.mcp import mcp as questions_mcp
from ycli.yandex.forms.subscriptions.mcp import mcp as subscriptions_mcp
from ycli.yandex.forms.surveys.mcp import mcp as surveys_mcp
from ycli.yandex.forms.variables.mcp import mcp as variables_mcp

mcp = FastMCP(
    "forms",
    instructions=(
        "Yandex Forms — reads and writes. Reference a survey by id: surveys_list enumerates "
        "them, questions_list / answers_list drill into one. Write tools (create / update / "
        "delete / publish / submit / export / move) carry the 'write' tag and honest "
        "destructive/idempotent hints; binary endpoints (file & image upload, downloads) stay "
        "CLI/SDK-only."
    ),
)
mcp.mount(me_mcp)
mcp.mount(surveys_mcp)
mcp.mount(questions_mcp)
mcp.mount(conditions_mcp)
mcp.mount(access_mcp)
mcp.mount(history_mcp)
mcp.mount(answers_mcp)
mcp.mount(keysets_mcp)
mcp.mount(operations_mcp)
mcp.mount(notifications_mcp)
mcp.mount(files_mcp)
mcp.mount(images_mcp)
mcp.mount(filling_mcp)
mcp.mount(hooks_mcp)
mcp.mount(subscriptions_mcp)
mcp.mount(variables_mcp)
