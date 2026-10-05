"""Wiki ``/pages/{id}/resources``, declared once (sans-IO).

Examples:
    >>> paged = list_(7, q=None, types="grid", order_by=None, order_direction=None)
    >>> paged.endpoint.params["page_size"]
    100
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.cursor import WIKI_CURSOR
from ycli.yandex.wiki.models import CursorPage
from ycli.yandex.wiki.resources.models import ResourceItem


def list_(
    page_id: int,
    *,
    q: str | None,
    types: str | None,
    order_by: str | None,
    order_direction: str | None,
) -> Paged[CursorPage[ResourceItem], ResourceItem]:
    params = {
        "page_size": 100,
        "q": q,
        "types": types,
        "order_by": order_by,
        "order_direction": order_direction,
    }
    return Paged(
        Endpoint(
            HTTPMethod.GET,
            f"pages/{segment(page_id)}/resources",
            CursorPage[ResourceItem],
            params=params,
        ),
        WIKI_CURSOR,
        lambda page: page.results,
    )
