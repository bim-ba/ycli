"""The one list of Yandex services: the CLI root, the MCP server and ``auth status`` iterate it.

Adding a service is one :class:`~ycli.yandex.service.Service` in its package ``__init__`` plus
one entry in :data:`SERVICES`. A service names its CLI app, MCP server and client by import
path (``"module:attribute"``, resolved with :func:`pkgutil.resolve_name`), so reading the
registry imports none of them: a command loads only the service it runs.

Examples:
    >>> [service.name for service in SERVICES]
    ['tracker', 'wiki', 'forms']
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ycli.yandex import forms, tracker, wiki

if TYPE_CHECKING:
    from ycli.yandex.service import Service

SERVICES: tuple[Service, ...] = (tracker.SERVICE, wiki.SERVICE, forms.SERVICE)
