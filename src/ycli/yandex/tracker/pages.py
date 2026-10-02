"""How a raw Tracker listing pages (``ycli api --paginate``): follow ``Link: rel="next"``.

Tracker sends that link on page-number and relative listings alike, and only while another page
exists, so following it never asks for a page the listing does not have.
"""

from ycli.yandex.core.pagination import LinkHeaderPagination

LINK_NEXT = LinkHeaderPagination()
