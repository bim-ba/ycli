"""Per-domain base — carries the Wiki API base_url; resource clients inherit it."""

from typing import ClassVar

from ycli.yandex.base import BaseYandex
from ycli.yandex.wiki import SERVICE


class WikiResource(BaseYandex):
    base_url: ClassVar[str] = SERVICE.profile.base_url
