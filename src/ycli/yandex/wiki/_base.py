"""Per-domain base — carries the Wiki API base_url; resource clients inherit it."""
from typing import ClassVar

from ycli.yandex.base import BaseYandex


class WikiResource(BaseYandex):
    base_url: ClassVar[str] = "https://api.wiki.yandex.net/v1"
