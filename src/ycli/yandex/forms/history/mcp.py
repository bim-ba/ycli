"""Forms change-log FastMCP tool (a read)."""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, TAGS, app_config, forms_client
from ycli.yandex.forms.history.models import HistoryEvent
from ycli.yandex.models import ItemList

mcp = FastMCP("forms-history")


@mcp.tool(name="history_list", annotations={**RO, "title": "List Forms change log"}, tags=TAGS)
def list_(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    ordering: Annotated[
        Literal["asc", "desc"] | None,
        Field(description="desc (newest first, the API default) or asc."),
    ] = None,
    limit: Annotated[int, Field(description="Most events to return (0 = the configured cap).")] = 0,
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> ItemList[HistoryEvent]:
    """The changes made to a form — who changed which part, when — across pages.

    Capped at the configured item cap unless ``limit`` is given.
    """
    cap = config.http.cap(limit)
    return client.history.list(survey_id, ordering=ordering, limit=cap)
