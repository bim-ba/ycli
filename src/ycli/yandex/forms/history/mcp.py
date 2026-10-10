"""Forms change-log FastMCP tool (a read)."""

from typing import Annotated

from fastmcp.dependencies import Depends
from pydantic import Field

from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.dependencies import RO, All, Next, app_config, forms_client, new_server
from ycli.yandex.forms.history.models import HistoryEvent
from ycli.yandex.models import Listed, SortDirection

mcp = new_server("forms-history")


@mcp.tool(name="history_list", annotations={**RO, "title": "List Forms change log"})
def list_(
    survey_id: Annotated[str, Field(description="Form id (24-char hex).")],
    ordering: Annotated[
        SortDirection | None,
        Field(description="desc (newest first, the API default) or asc."),
    ] = None,
    limit: Annotated[
        int | None, Field(ge=1, description="Most events to return (omitted: the configured cap).")
    ] = None,
    all: All = False,
    next: Next = None,
    client: FormsClient = Depends(forms_client),
    config: AppConfig = Depends(app_config),
) -> Listed[HistoryEvent]:
    """The changes made to a form — who changed which part, when — across pages.

    Capped at the configured item cap unless ``limit`` is given.
    """
    cap = config.http.cap(limit, all_=all)
    return client.history.list(survey_id, ordering=ordering, limit=cap, next=next).collect()
