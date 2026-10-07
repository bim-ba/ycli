"""A Wiki page as a file: ``wiki/<slug>.md``, its text under a header."""

from functools import partial

from pydantic import Field

from ycli.yandex.sync.document import Link
from ycli.yandex.sync.formats import MarkdownWithHeader
from ycli.yandex.sync.kind import CheckedVersion, Kind
from ycli.yandex.wiki.pages import endpoints
from ycli.yandex.wiki.pages.models import PageUpdate


class PageLink(Link):
    """What ties a page file to its page."""

    id: int | None = Field(default=None, description="Id of the page.")
    revision: int | None = Field(default=None, description="Revision the page was read at.")


#: The API takes no revision with an update, so the newest one is read and compared first.
PAGE = Kind(
    name="wiki/page",
    layout=MarkdownWithHeader(),
    link=PageLink,
    content=PageUpdate,
    find=partial(endpoints.descendants_list, include_self=True),
    read=partial(endpoints.get_by_id, fields="content"),
    create=endpoints.create,
    update=endpoints.update,
    delete=endpoints.delete,
    version=CheckedVersion(newest=endpoints.revisions_list),
)
