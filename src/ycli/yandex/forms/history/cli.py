"""`forms history` command: a form's change log."""

from __future__ import annotations

from typing import Annotated

import typer

from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.forms.client import FormsClient
from ycli.yandex.forms.history.models import HistoryEvent
from ycli.yandex.forms.typedefs import SurveyIdArg
from ycli.yandex.models import ItemList

app = typer.Typer(name="history", help="Forms change log.", no_args_is_help=True)


@app.command("list")
def list_(
    survey_id: SurveyIdArg,
    ordering: Annotated[
        str | None, typer.Option(help="desc (newest first, the API default) or asc.")
    ] = None,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    config: AppConfig,
    forms: FormsClient,
) -> ItemList[HistoryEvent]:
    """List the changes made to form SURVEY_ID (auto-paginated; --all for everything)."""
    cap = config.http.cap(limit, all_=all_)
    return forms.history.list(survey_id, ordering=ordering, limit=cap)
