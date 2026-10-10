"""Wiki ``/pages/{id}/access``, declared once (sans-IO).

``prevent_selflock`` asks the API to refuse a change that would lock the caller out of the page;
it is sent only when set, because ``false`` is the API's default.

Examples:
    >>> delete(7, "9", prevent_selflock=True).params
    {'prevent_selflock': True}
    >>> update(7, "9", {"role": "reader"}, prevent_selflock=False).effect
    <Effect.IDEMPOTENT_WRITE: 'idempotent_write'>
"""

from http import HTTPMethod

from ycli.yandex.core.endpoint import Effect, Endpoint, segment
from ycli.yandex.wiki.access.models import PageAccess, PageAccessCreate, PageAccessUpdate


def _selflock(prevent_selflock: bool | None) -> dict[str, bool | None]:
    return {"prevent_selflock": prevent_selflock}


def create(page_id: int, body: PageAccessCreate) -> Endpoint[PageAccess]:
    return Endpoint(
        HTTPMethod.POST,
        f"pages/{segment(page_id)}/access",
        PageAccess,
        json=body,
        grants_access=True,
    )


def update(
    page_id: int, access_id: str, body: PageAccessUpdate, *, prevent_selflock: bool | None
) -> Endpoint[PageAccess]:
    path = f"pages/{segment(page_id)}/access/{segment(access_id)}"
    # violation(arch-3): POST access sets role; a resend is a no-op
    return Endpoint(
        HTTPMethod.POST,
        path,
        PageAccess,
        params=_selflock(prevent_selflock),
        json=body,
        effect=Effect.IDEMPOTENT_WRITE,
        grants_access=True,
    )


def delete(page_id: int, access_id: str, *, prevent_selflock: bool | None) -> Endpoint[None]:
    path = f"pages/{segment(page_id)}/access/{segment(access_id)}"
    return Endpoint(HTTPMethod.DELETE, path, params=_selflock(prevent_selflock))


def clear(page_id: int, *, prevent_selflock: bool | None) -> Endpoint[None]:
    return Endpoint(
        HTTPMethod.DELETE, f"pages/{segment(page_id)}/access", params=_selflock(prevent_selflock)
    )
