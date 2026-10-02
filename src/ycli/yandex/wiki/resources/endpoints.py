"""Wiki ``/pages/{id}/resources``, declared once (sans-IO).

Example:
    >>> list_resources(7, q=None, types="grid", order_by=None).endpoint.params["page_size"]
    100
"""

from __future__ import annotations

from ycli.yandex.core.endpoint import Endpoint, Paged, segment
from ycli.yandex.wiki.cursor import WIKI_CURSOR
from ycli.yandex.wiki.resources.models import ResourceItem, ResourcesResponse


def list_resources(
    page_id: int, *, q: str | None, types: str | None, order_by: str | None
) -> Paged[ResourcesResponse, ResourceItem]:
    params = {"page_size": 100, "q": q, "types": types, "order_by": order_by}
    return Paged(
        Endpoint("GET", f"pages/{segment(page_id)}/resources", ResourcesResponse, params=params),
        WIKI_CURSOR,
        lambda page: page.results,
    )
