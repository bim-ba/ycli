"""The one list of Yandex services: the CLI root, the MCP server and ``auth status`` iterate it.

Adding a service is one :class:`~ycli.yandex.service.Service` in its package ``__init__`` plus
one entry in :data:`SERVICES`. A service names its CLI app, MCP server and client by import
path (``"module:attribute"``, resolved with :func:`pkgutil.resolve_name`), so reading the
registry imports none of them: a command loads only the service it runs.

Examples:
    >>> [service.name for service in SERVICES]
    ['tracker', 'wiki', 'forms', 'datalens']
"""

from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec
from pkgutil import iter_modules
from typing import TYPE_CHECKING, Any

from ycli.yandex import datalens, forms, tracker, wiki

if TYPE_CHECKING:
    from ycli.yandex.service import Service
    from ycli.yandex.sync.kind import Kind

SERVICES: tuple[Service, ...] = (
    tracker.SERVICE,
    wiki.SERVICE,
    forms.SERVICE,
    datalens.SERVICE,
)


def resources(service: Service) -> tuple[str, ...]:
    """The resources of ``service``, by name: its packages that declare operations.

    Nothing lists them: a resource is found by the ``endpoints`` module it has.

    Args:
        service: A registered service.

    Returns:
        The names of its resources, sorted.

    Examples:
        >>> "boards" in resources(SERVICES[0]) and "mcp" not in resources(SERVICES[0])
        True
    """
    package = import_module(f"{__package__}.{service.name}")
    return tuple(
        sorted(
            found.name
            for found in iter_modules(package.__path__)
            if found.ispkg and find_spec(f"{package.__name__}.{found.name}.endpoints") is not None
        )
    )


def about(service: Service) -> str:
    """What ``service`` is and how much it has: the words every surface says of it.

    The instructions of the MCP server and the header of ``ycli --help`` both read it.

    Args:
        service: A registered service.

    Returns:
        Its description and the number of its resources.

    Examples:
        >>> about(SERVICES[0]).startswith("Yandex Tracker: issues, queues")
        True
        >>> about(SERVICES[0]).endswith(" resources")
        True
    """
    return f"{service.help} {len(resources(service))} resources"


def start_command(service: Service) -> str:
    """The command an agent or a person begins with: the tool ``service.start``, as the CLI.

    A tool and its command are one name (ARCH-1): the service, the resource, the operation.

    Args:
        service: A registered service.

    Returns:
        The command line.

    Examples:
        >>> start_command(SERVICES[0])
        'ycli tracker me get'
    """
    rest = service.start.removeprefix(f"{service.name}_")
    resource = max((name for name in resources(service) if rest.startswith(f"{name}_")), key=len)
    operation = rest.removeprefix(f"{resource}_").replace("_", "-")
    return f"ycli {service.name} {resource} {operation}"


def kinds() -> tuple[Kind[Any, Any], ...]:
    """Every kind of file a resource of a registered service declares, by name.

    A resource declares a kind in its ``sync`` module; nothing lists them. The modules are
    found by walking the packages of the services, so a new resource is picked up by the file
    it adds.

    Returns:
        The declared kinds, by name.

    Examples:
        >>> [kind.name for kind in kinds()] == sorted(kind.name for kind in kinds())
        True
    """
    # Imported here: reading the list of services must not load the file engine.
    from ycli.yandex.sync.kind import Kind

    found: list[Kind[Any, Any]] = []
    for service in SERVICES:
        package = import_module(f"{__package__}.{service.name}")
        for resource in iter_modules(package.__path__):
            name = f"{package.__name__}.{resource.name}.sync"
            if resource.ispkg and find_spec(name) is not None:
                declared = vars(import_module(name)).values()
                found += [value for value in declared if isinstance(value, Kind)]
    return tuple(sorted(found, key=lambda kind: kind.name))
