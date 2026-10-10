"""ARCH-5 — Single sources of truth (see ARCHITECTURE.md)."""

import re
from pathlib import Path

import pytest

from tests.architecture.scanners import SRC

# `timeout=30` as a keyword argument, or `timeout: float = 30.0` as an annotated default.
_LITERAL_DEFAULT_RE = re.compile(
    r"\b(timeout|timeout_seconds|retries|max_items|max_tool_items|max_pages|max_retry_after_seconds|"
    r"max_wait_seconds)"
    r"\s*(:[^=\n]+)?=\s*\d"
)
# `MAX_RETRY_AFTER_SECONDS = 60.0` at module level: a limit a user can run into, kept out of
# the settings. A page size is a fact of the API and stays where it is used.
_LIMIT_CONSTANT_RE = re.compile(
    r"^_?(DEFAULT|MAX)_(?!\w*PAGE_SIZE\b)\w+\s*(:[^=\n]+)?=\s*\d", re.MULTILINE
)
_CREDENTIAL_ENV_RE = re.compile(r"YANDEX_(ID_OAUTH_TOKEN|ID_ORGANIZATION_ID|CLOUD_IAM_TOKEN)\b")
_TOKEN_RE = re.compile(r"YANDEX_ID_\w+\s*=\s*['\"]")
_VERSION_RE = re.compile(r"__version__\s*=\s*['\"]\d")
_ORG_HEADER_RE = re.compile(r"X-Org-I[dD]")
_YANDEX_HOST_RE = re.compile(
    r"https://(?:[\w.-]*api[\w.-]*\.yandex\.(?:net|ru)|pypi\.org)"
)  # API hosts, not web pages; and PyPI, the one host ycli asks that is not Yandex's
# Where a Yandex host may be spelled, and why: each service's profile, the IAM token endpoint,
# and the Yandex ID and API 360 hosts `auth status` reads.
ARCH5_HOST_HOMES = {
    Path("yandex/tracker/__init__.py"): "Tracker service profile",
    Path("yandex/wiki/__init__.py"): "Wiki service profile",
    Path("yandex/forms/__init__.py"): "Forms service profile",
    Path("yandex/core/auth.py"): "IAM token endpoint for service accounts",
    Path("yandex/status/token_client.py"): "Yandex ID and API 360 profiles of `auth status`",
    Path("yandex/status/release_client.py"): "PyPI, asked without credentials by `ycli doctor`",
}


def _single_source_offenders(rel: Path, text: str) -> list[str]:
    offenders = []
    if _TOKEN_RE.search(text):
        offenders.append(f"{rel}: hardcoded YANDEX_ID token literal")
    if rel != Path("__init__.py") and _VERSION_RE.search(text):
        offenders.append(f"{rel}: hardcoded __version__ literal")
    if rel != Path("yandex/core/profile.py") and _ORG_HEADER_RE.search(text):
        offenders.append(f"{rel}: org header string outside yandex/core/profile.py")
    if rel not in ARCH5_HOST_HOMES and _YANDEX_HOST_RE.search(text):
        offenders.append(f"{rel}: Yandex host outside a service profile")
    if rel != Path("settings.py"):
        if _CREDENTIAL_ENV_RE.search(text):
            offenders.append(f"{rel}: credential variable name spelled outside settings.py")
        code = "\n".join(line for line in text.splitlines() if ">>>" not in line)  # not doctests
        if _LITERAL_DEFAULT_RE.search(code):
            offenders.append(f"{rel}: a literal default shadows the HTTP settings")
        if _LIMIT_CONSTANT_RE.search(code):
            offenders.append(f"{rel}: a limit is a module constant instead of a setting")
        if re.search(r"class \w+\(BaseSettings\)", text):
            offenders.append(f"{rel}: BaseSettings subclass outside settings.py")
    return offenders


def test_arch5_single_sources_of_truth():
    """Version, credentials, org header, hosts and timeouts each have one home."""
    offenders = [
        finding
        for p in SRC.rglob("*.py")
        for finding in _single_source_offenders(p.relative_to(SRC), p.read_text(encoding="utf-8"))
    ]
    assert not offenders, offenders


_LOGGER_NAME_RE = re.compile(r"""getLogger\(\s*["']([\w.]+)["']""")


def _repeated_logger_names(sources: dict[str, str]) -> dict[str, list[str]]:
    """A logger name spelled as a literal in more than one module, with those modules."""
    homes: dict[str, list[str]] = {}
    for rel, text in sources.items():
        for name in set(_LOGGER_NAME_RE.findall(text)):
            homes.setdefault(name, []).append(rel)
    return {name: sorted(rels) for name, rels in homes.items() if len(rels) > 1}


def test_arch5_a_logger_name_is_spelled_in_one_module():
    """Two modules that log to one channel share its constant (``ycli.log``)."""
    sources = {str(p.relative_to(SRC)): p.read_text(encoding="utf-8") for p in SRC.rglob("*.py")}
    assert _repeated_logger_names(sources) == {}


def test_arch5_logger_name_check_bites():
    sources = {
        "a.py": 'logger = logging.getLogger("ycli.http")',
        "b.py": "logger = logging.getLogger('ycli.http')",
        "c.py": 'logger = logging.getLogger("ycli.status")',
        "d.py": "logger = logging.getLogger(HTTP_LOGGER_NAME)",
    }
    assert _repeated_logger_names(sources) == {"ycli.http": ["a.py", "b.py"]}


def test_arch5_every_host_home_still_spells_a_host():
    """An allowlist entry whose file no longer names a host is removed, not kept."""
    stale = [
        str(rel)
        for rel in ARCH5_HOST_HOMES
        if not (SRC / rel).is_file()
        or not _YANDEX_HOST_RE.search((SRC / rel).read_text(encoding="utf-8"))
    ]
    assert stale == []


def test_arch5_stale_host_home_check_bites(monkeypatch):
    monkeypatch.setitem(ARCH5_HOST_HOMES, Path("yandex/models.py"), "names no host")
    with pytest.raises(AssertionError):
        test_arch5_every_host_home_still_spells_a_host()


def test_arch5_guard_bites():
    rel = Path("yandex/wiki/pages/client.py")
    for source in (
        'YANDEX_ID_OAUTH_TOKEN = "x"',
        '__version__ = "1.0"',
        'headers = {"X-Org-Id": org}',
        'URL = "https://api.wiki.yandex.net/v1"',
        'URL = "https://pypi.org/pypi/other/json"',
        "session.send(request, timeout=30)",
        "def session(*, timeout_seconds: float = 30.0) -> None: ...",
        "def __init__(self, retries: int = 3) -> None: ...",
        "def items(max_items: int | None = 500) -> None: ...",
        "def iterate(paged, *, max_pages: int = 1000) -> None: ...",
        "def poll(fetch, *, max_wait_seconds: float = 1380.0) -> None: ...",
        "DEFAULT_MAX_PAGES = 1000",
        "MAX_RETRY_AFTER_SECONDS = 60.0",
        "class Local(BaseSettings): ...",
        'hint = "check YANDEX_ID_OAUTH_TOKEN"',
        'missing = {"YANDEX_ID_ORGANIZATION_ID"}',
        'hint = "or set YANDEX_CLOUD_IAM_TOKEN"',
    ):
        assert _single_source_offenders(rel, source), source
    # A comparison or a value read from the settings is not a literal default.
    for source in ("if retries == 0: ...", "timeout_seconds: float = config.timeout_seconds"):
        assert not _single_source_offenders(rel, source), source
