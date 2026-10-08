"""Yandex Forms domain — per-resource clients (me/surveys/questions/answers), CLI, and MCP."""

from ycli.yandex.core.profile import ServiceProfile
from ycli.yandex.service import Service

SERVICE = Service(
    name="forms",
    help="Yandex Forms: surveys, questions, answers, publishing.",
    client="ycli.yandex.forms.client:FormsClient",
    cli="ycli.yandex.forms.cli:app",
    mcp="ycli.yandex.forms.mcp.server:mcp",
    start="forms_surveys_list",
    profile=ServiceProfile("https://api.forms.yandex.net/v1"),
)
