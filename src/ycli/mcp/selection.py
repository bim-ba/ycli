"""Which tools one MCP server serves: the typed selection behind ``ycli mcp start`` flags.

Importable without the ``mcp`` extra (no fastmcp here), so the CLI can parse and validate
flags before importing the server. Precedence, strongest first (github-mcp-server's rule):
``read_only`` over ``exclude_tools`` over ``tools`` over ``toolsets``.

Examples:
    >>> Selection(toolsets=("wiki",), tools=("tracker_issues_get",)).services()
    ('tracker', 'wiki')
"""

from dataclasses import dataclass

from ycli.mcp.profiles import CORE_TOOLS, STATUS_TOOL
from ycli.yandex.registry import SERVICES

ALL = "all"
CORE = "core"
TOOLSET_NAMES: tuple[str, ...] = (*(service.name for service in SERVICES), CORE, ALL)


def split_names(value: str | None) -> tuple[str, ...]:
    """A comma-separated flag value as names, blanks dropped.

    Args:
        value: A comma-separated flag value; ``None`` when the flag is not given.

    Returns:
        The names, in order.

    Examples:
        >>> split_names("tracker, wiki,,")
        ('tracker', 'wiki')
    """
    return tuple(name for part in (value or "").split(",") if (name := part.strip()))


def _service_of(tool_name: str) -> str | None:
    """The registry service a tool name belongs to (``tracker_issues_get`` -> ``tracker``)."""
    prefix = tool_name.split("_", 1)[0]
    return prefix if any(service.name == prefix for service in SERVICES) else None


@dataclass(frozen=True, slots=True)
class Selection:
    """The tools to serve: toolsets, extra tools, exclusions and the read-only / search modes.

    ``toolsets`` names registry services plus ``core`` (a curated profile) and ``all`` (the
    default). ``tools`` adds names beyond the toolsets, ``exclude_tools`` removes names, and
    ``read_only`` hides every write tool last. ``tool_search`` replaces the listing with a
    search interface that keeps ``status_get`` visible.
    """

    toolsets: tuple[str, ...] = (ALL,)
    tools: tuple[str, ...] = ()
    exclude_tools: tuple[str, ...] = ()
    read_only: bool = False
    tool_search: bool = False

    def __post_init__(self) -> None:
        unknown = [name for name in self.toolsets if name not in TOOLSET_NAMES]
        if unknown or not self.toolsets:
            raise ValueError(
                f"unknown toolset(s) {', '.join(unknown) or '(none given)'}; "
                f"valid: {', '.join(TOOLSET_NAMES)}"
            )
        if STATUS_TOOL in self.exclude_tools:
            raise ValueError(f"{STATUS_TOOL} is always served and cannot be excluded")
        for name in (*self.tools, *self.exclude_tools):
            if name != STATUS_TOOL and _service_of(name) is None:
                raise ValueError(f"unknown tool {name!r}: tool names start with a service name")

    @property
    def serves_everything(self) -> bool:
        """Whether every tool of every service is a candidate (no allowlist is applied)."""
        return ALL in self.toolsets

    def services(self) -> tuple[str, ...]:
        """Names of the services to mount, in registry order.

        A service is mounted when a toolset names it, ``core`` draws from it, or a tool named
        in ``tools`` / ``exclude_tools`` belongs to it (so the name can be checked).
        """
        named = {name for name in self.toolsets if name != CORE}
        if self.serves_everything:
            named |= {service.name for service in SERVICES}
        if CORE in self.toolsets:
            named |= {service for name in CORE_TOOLS if (service := _service_of(name))}
        named |= {
            service for name in (*self.tools, *self.exclude_tools) if (service := _service_of(name))
        }
        return tuple(service.name for service in SERVICES if service.name in named)

    def listed_services(self) -> tuple[str, ...]:
        """Services served whole: named directly (or all), not merely drawn on by ``core``."""
        if self.serves_everything:
            return tuple(service.name for service in SERVICES)
        return tuple(service.name for service in SERVICES if service.name in self.toolsets)

    def listed_names(self) -> frozenset[str]:
        """Tool names served by name: ``status_get``, the ``core`` profile and ``tools``."""
        core = CORE_TOOLS if CORE in self.toolsets else frozenset()
        return frozenset({STATUS_TOOL, *self.tools}) | core
