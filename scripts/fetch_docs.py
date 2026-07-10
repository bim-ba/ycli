"""Reproducibly mirror Yandex service documentation to Markdown.

Two documentation sources, one output tree:

* **diplodoc** (default) — the Yandex 360 / dev-hub product docs published as Diplodoc/YFM
  sites at ``yandex.ru``. Each rendered page has a stable ``.md`` sibling URL that serves the
  self-contained YFM source over plain HTTP, no browser and no auth; each service publishes a
  flat ``sitemap.xml``. Pipeline: ``read sitemap -> for each <loc>: GET <loc>.md -> write``.
* **cloud** — the open-source Yandex Cloud documentation at ``github.com/yandex-cloud/docs``.
  Enumerated via the GitHub trees API and fetched verbatim from ``raw.githubusercontent.com``,
  pinned to the default-branch HEAD commit for reproducibility.

Examples::

    python scripts/fetch_docs.py tracker --limit 5 --out /tmp/sample      # validate diplodoc
    python scripts/fetch_docs.py tracker                                  # one diplodoc service
    python scripts/fetch_docs.py --all                                    # every diplodoc service
    python scripts/fetch_docs.py wiki --dry-run                           # list, no writes
    python scripts/fetch_docs.py datalens --source cloud --limit 5        # validate cloud
    python scripts/fetch_docs.py --all --source cloud                     # clone all cloud docs

Diplodoc output mirrors the URL path 1:1 under ``<out>/<service>/<url-path>.md``; cloud output
mirrors the repo path under ``<out>/cloud/<lang>/<service>/<repo-path>``. Each service dir gets a
``.fetch-manifest.json`` (revision/generator/pages for diplodoc; licence/commit/pages for cloud)
so re-runs are diffable.

Licensing — read before redistributing what this fetches:

* **diplodoc** pages come from ``yandex.ru`` and are covered by the Yandex User Agreement, NOT an
  open licence. Fetch them for local/offline reference; do **not** commit or redistribute the
  corpus without permission.
* **cloud** pages are (C) YANDEX LLC, licensed under Creative Commons Attribution 4.0
  International (CC BY 4.0). They may be redistributed **with** attribution; ``--source cloud``
  writes an ``ATTRIBUTION.md`` and records the licence + pinned commit in the manifest.

A ``GITHUB_TOKEN`` / ``GH_TOKEN`` env var, if present, authenticates the GitHub API calls used by
cloud mode (raising the rate limit from 60 to 5000 req/h — matters for ``--all --source cloud``).
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import time
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import requests

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "references" / "yandex-360"
USER_AGENT = "ycli-docs-fetcher/1.0 (+https://github.com/bim-ba/ycli)"
REQUEST_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3

# --- cloud source: github.com/yandex-cloud/docs (CC BY 4.0) ---------------------------
GITHUB_API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
CLOUD_OWNER = "yandex-cloud"
CLOUD_REPO = "docs"
CLOUD_REPO_URL = "https://github.com/yandex-cloud/docs"
CLOUD_LICENSE = "CC-BY-4.0"
CLOUD_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
CLOUD_COPYRIGHT = "(C) YANDEX LLC, 2018"


@dataclass(frozen=True)
class ServiceConfig:
    """One documentation site: where to enumerate it and where it lands locally."""

    subdir: str
    sitemaps: tuple[str, ...]
    url_prefix: str  # path prefix (after host) stripped from each loc, e.g. "/support/tracker/"

    @property
    def source_base(self) -> str:
        """Human-facing base URL of the doc site (host + stripped prefix)."""
        host = urlparse(self.sitemaps[0]).netloc
        return f"https://{host}{self.url_prefix}"


# Two URL families: the 360-suite product docs live under yandex.ru/support/<svc>/…,
# while the api360 / Disk developer portals live under yandex.ru/dev/<svc>/doc/….
# Telemost has no standalone portal — its sitemap is the 301 target of
# support/telemost/sitemap.xml, nested inside the Yandex 360 support tree.
SERVICES: dict[str, ServiceConfig] = {
    "tracker": ServiceConfig(
        subdir="tracker",
        sitemaps=("https://yandex.ru/support/tracker/sitemap.xml",),
        url_prefix="/support/tracker/",
    ),
    "wiki": ServiceConfig(
        subdir="wiki",
        sitemaps=("https://yandex.ru/support/wiki/sitemap.xml",),
        url_prefix="/support/wiki/",
    ),
    "forms": ServiceConfig(
        subdir="forms",
        sitemaps=("https://yandex.ru/support/forms/sitemap.xml",),
        url_prefix="/support/forms/",
    ),
    "api360": ServiceConfig(
        subdir="api360",
        sitemaps=("https://yandex.ru/dev/api360/doc/sitemap.xml",),
        url_prefix="/dev/api360/doc/",
    ),
    "disk": ServiceConfig(
        subdir="disk",
        sitemaps=("https://yandex.ru/dev/disk-api/doc/sitemap.xml",),
        url_prefix="/dev/disk-api/doc/",
    ),
    "telemost": ServiceConfig(
        subdir="telemost",
        sitemaps=("https://yandex.ru/support/yandex-360/customers/telemost/web/sitemap.xml",),
        url_prefix="/support/yandex-360/customers/telemost/web/",
    ),
    # --- wider dev hub — REST-API & developer portals (Diplodoc .md, verified live) ---
    "id": ServiceConfig(
        subdir="id",
        sitemaps=("https://yandex.ru/dev/id/doc/sitemap.xml",),
        url_prefix="/dev/id/doc/",
    ),
    "telemost-api": ServiceConfig(
        subdir="telemost-api",
        sitemaps=("https://yandex.ru/dev/telemost/doc/sitemap.xml",),
        url_prefix="/dev/telemost/doc/",
    ),
    "metrika": ServiceConfig(
        subdir="metrika",
        sitemaps=("https://yandex.ru/dev/metrika/sitemap.xml",),
        url_prefix="/dev/metrika/",
    ),
    "direct": ServiceConfig(
        subdir="direct",
        sitemaps=("https://yandex.ru/dev/direct/doc/sitemap.xml",),
        url_prefix="/dev/direct/doc/",
    ),
    "audience": ServiceConfig(
        subdir="audience",
        sitemaps=("https://yandex.ru/dev/audience/sitemap.xml",),
        url_prefix="/dev/audience/",
    ),
    "webmaster": ServiceConfig(
        subdir="webmaster",
        sitemaps=("https://yandex.ru/dev/webmaster/doc/sitemap.xml",),
        url_prefix="/dev/webmaster/doc/",
    ),
    "weather": ServiceConfig(
        subdir="weather",
        sitemaps=("https://yandex.ru/dev/weather/doc/sitemap.xml",),
        url_prefix="/dev/weather/doc/",
    ),
    "market": ServiceConfig(
        subdir="market",
        sitemaps=("https://yandex.ru/dev/market/partner-api/doc/sitemap.xml",),
        url_prefix="/dev/market/partner-api/doc/",
    ),
    "admetrica": ServiceConfig(
        subdir="admetrica",
        sitemaps=("https://yandex.ru/dev/admetrica/doc/sitemap.xml",),
        url_prefix="/dev/admetrica/doc/",
    ),
    "rtb": ServiceConfig(
        subdir="rtb",
        sitemaps=("https://yandex.ru/dev/rtb/doc/sitemap.xml",),
        url_prefix="/dev/rtb/doc/",
    ),
    "rasp": ServiceConfig(
        subdir="rasp",
        sitemaps=("https://yandex.ru/dev/rasp/doc/sitemap.xml",),
        url_prefix="/dev/rasp/doc/",
    ),
    "travel-partners": ServiceConfig(
        subdir="travel-partners",
        sitemaps=("https://yandex.ru/dev/travel-partners-api/doc/sitemap.xml",),
        url_prefix="/dev/travel-partners-api/doc/",
    ),
    "games": ServiceConfig(
        subdir="games",
        sitemaps=("https://yandex.ru/dev/games/doc/sitemap.xml",),
        url_prefix="/dev/games/doc/",
    ),
    "speller": ServiceConfig(
        subdir="speller",
        sitemaps=("https://yandex.ru/dev/speller/doc/sitemap.xml",),
        url_prefix="/dev/speller/doc/",
    ),
    "safebrowsing": ServiceConfig(
        subdir="safebrowsing",
        sitemaps=("https://yandex.ru/dev/safebrowsing/doc/sitemap.xml",),
        url_prefix="/dev/safebrowsing/doc/",
    ),
    "video-sdk": ServiceConfig(
        subdir="video-sdk",
        sitemaps=("https://yandex.ru/dev/video-sdk/doc/sitemap.xml",),
        url_prefix="/dev/video-sdk/doc/",
    ),
    "tanker": ServiceConfig(
        subdir="tanker",
        sitemaps=("https://yandex.ru/dev/tanker/doc/sitemap.xml",),
        url_prefix="/dev/tanker/doc/",
    ),
    "alice": ServiceConfig(
        subdir="dialogs/alice",
        sitemaps=("https://yandex.ru/dev/dialogs/alice/doc/sitemap.xml",),
        url_prefix="/dev/dialogs/alice/doc/",
    ),
    "smart-home": ServiceConfig(
        subdir="dialogs/smart-home",
        sitemaps=("https://yandex.ru/dev/dialogs/smart-home/doc/sitemap.xml",),
        url_prefix="/dev/dialogs/smart-home/doc/",
    ),
}

# --- Conservative source tidy-up ------------------------------------------------------
# The served .md passes through decorative raw-HTML that the hand-made corpus omits:
# a `request_example` box wrapping the method + endpoint URL, plus `yfm-clipboard`
# copy buttons with an inline SVG. We drop only the clearly-decorative wrappers and
# reformat the method/URL as plain Markdown — content is never discarded.
_CLIPBOARD_BUTTON = re.compile(r'<button class="yfm-clipboard-button">.*?</button>', re.DOTALL)
_REQUEST_EXAMPLE = re.compile(r'<div class="request_example[^"]*">(?P<body>.*?)</div>', re.DOTALL)
_METHOD = re.compile(r"<p>\s*(?P<method>[A-Z]+)\s*</p>")
_CODE = re.compile(r"<pre><code>(?P<url>.*?)</code></pre>", re.DOTALL)
_GENERATOR = re.compile(r"content:\s*(Diplodoc Platform v[\d.]+)")
_REVISION = re.compile(r'"revision":"(r\d+)"')
_REVISION_ASSET = re.compile(r"rev/(r\d+)")
_SITEMAP_LOC = ".//{*}loc"


def _unwrap_request_example(match: re.Match[str]) -> str:
    body = match.group("body")
    method = _METHOD.search(body)
    code = _CODE.search(body)
    if not (method and code):
        return match.group(0)  # unfamiliar shape -> leave content untouched
    url = html.unescape(code.group("url").strip())
    return f"{method.group('method')}\n\n```\n{url}\n```"


def _tidy(text: str) -> str:
    """Strip decorative clipboard buttons and unwrap request_example boxes."""
    text = _CLIPBOARD_BUTTON.sub("", text)
    return _REQUEST_EXAMPLE.sub(_unwrap_request_example, text)


class _NoSource:
    """Sentinel: a page URL has no YFM `.md` sibling (a section root / non-page) — an expected
    absence, kept distinct from a fetch failure so it is skipped without counting as one."""


_NO_SOURCE = _NoSource()


@dataclass
class _HttpClient:
    """Polite retry/backoff HTTP shared by both fetch strategies, over one Session."""

    out_dir: Path
    delay_seconds: float = 0.2
    dry_run: bool = False
    lang: str = "ru"
    session: requests.Session = field(default_factory=requests.Session)

    def __post_init__(self) -> None:
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.encountered_failure = False

    def _get(self, url: str) -> requests.Response | None:
        """GET with retry/backoff. Returns the response for any completed HTTP status (callers
        inspect ``status_code``); returns None only when the request never completed — a network
        error, or a 5xx / 429 / 403 that persisted across every retry."""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            except requests.RequestException as error:
                if attempt == MAX_ATTEMPTS:
                    print(f"  ! {url} — {error}")
                    return None
                time.sleep(self.delay_seconds * attempt)
                continue
            rate_limited = response.status_code in (429, 403)
            if attempt < MAX_ATTEMPTS and (response.status_code >= 500 or rate_limited):
                time.sleep(self.delay_seconds * attempt * (2 if rate_limited else 1))
                continue
            return response
        return None

    def _get_json(self, url: str) -> dict | list | None:
        response = self._get(url)
        if response is None or response.status_code != 200:
            if response is not None:
                print(f"  ! {url} — HTTP {response.status_code}")
            return None
        try:
            return response.json()
        except ValueError:
            print(f"  ! {url} — non-JSON response")
            return None

    def _safe_target(self, rel_path: Path) -> Path | None:
        """Resolve rel_path under out_dir, refusing any path that escapes it (``..``/absolute).

        Write paths derive from remote data (sitemap locs, redirect URLs, git-tree entries);
        this keeps a hostile or malformed source from writing outside the chosen output root.
        """
        root = self.out_dir.resolve()
        target = (self.out_dir / rel_path).resolve()
        if target != root and root not in target.parents:
            print(f"  ! refusing to write outside {root}: {rel_path}")
            return None
        return target

    def _write(self, rel_path: Path, text: str) -> None:
        target = self._safe_target(rel_path)
        if target is None:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def _write_bytes(self, rel_path: Path, data: bytes) -> None:
        """Write raw response bytes unchanged — keeps a redistributed corpus byte-verbatim."""
        target = self._safe_target(rel_path)
        if target is None:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


@dataclass
class DocsFetcher(_HttpClient):
    """Mirror one or more Diplodoc-published Yandex doc sites, politely and idempotently."""

    def _matches_lang(self, loc: str) -> bool:
        """Keep pages of the chosen language, plus language-agnostic pages (no ru/en segment)."""
        if self.lang == "all":
            return True
        has_ru = "/ru/" in loc or loc.endswith("/ru")
        has_en = "/en/" in loc or loc.endswith("/en")
        if not has_ru and not has_en:
            return True
        return f"/{self.lang}/" in loc or loc.endswith(f"/{self.lang}")

    # -- enumeration -------------------------------------------------------------------
    def _enumerate(self, sitemaps: tuple[str, ...]) -> list[str] | None:
        """Fetchable page URLs from the sitemap(s). Returns None when a sitemap can't be fetched
        or parsed — kept distinct from an empty list (a valid, genuinely empty map) so the caller
        never mistakes a network / anti-bot failure for "this service has no pages"."""
        locs: list[str] = []
        seen: set[str] = set()
        for sitemap_url in sitemaps:
            response = self._get(sitemap_url)
            if response is None or response.status_code != 200:
                print(f"  ! {sitemap_url} — could not fetch sitemap")
                return None
            try:
                root = ElementTree.fromstring(response.content)
            except ElementTree.ParseError as error:
                print(f"  ! {sitemap_url} — invalid sitemap XML ({error})")
                return None
            for element in root.findall(_SITEMAP_LOC):
                loc = (element.text or "").strip()
                # Skip trailing-slash locs (they 404 as `.md`) and malformed locs that embed a
                # second URL after the origin — some Yandex sitemaps list external links / PDFs
                # (t.me, /legal/…, *.pdf) as <loc>, which 401/404 when `.md` is appended.
                if not loc or loc.endswith("/") or loc.count("://") > 1 or loc in seen:
                    continue
                seen.add(loc)
                locs.append(loc)
        return locs

    # -- path mapping ------------------------------------------------------------------
    def _relative_path(self, md_url: str, config: ServiceConfig) -> Path:
        path = urlparse(md_url).path
        remainder = (
            path[len(config.url_prefix) :]
            if path.startswith(config.url_prefix)
            else path.lstrip("/")
        )
        if not remainder.endswith(".md"):
            remainder = f"{remainder.rstrip('/')}.md"
        return Path(config.subdir) / remainder

    # -- single page -------------------------------------------------------------------
    def _fetch_page(self, loc: str, config: ServiceConfig) -> tuple[Path, str] | _NoSource | None:
        """Fetch one page's YFM source. Returns (path, text) on success, ``_NO_SOURCE`` when the
        URL has no `.md` sibling (404 or non-markdown — expected for section roots), or None on a
        genuine fetch failure (network / 5xx / rate-limit)."""
        response = self._get(f"{loc}.md")
        if response is None:
            return None
        if response.status_code == 404:
            return _NO_SOURCE
        if response.status_code != 200:
            print(f"  ! {loc}.md — HTTP {response.status_code}")
            return None
        if "markdown" not in response.headers.get("Content-Type", ""):
            return _NO_SOURCE  # a section index / HTML page — no YFM source here
        # Derive the path from the *final* URL so redirects land at their real name.
        rel_path = self._relative_path(response.url, config)
        return rel_path, _tidy(response.text)

    def _probe_revision(self, page_url: str) -> str | None:
        """Best-effort Diplodoc build revision (rNNNN) from a page's HTML __DATA__."""
        response = self._get(page_url)
        if response is None:
            return None
        match = _REVISION.search(response.text) or _REVISION_ASSET.search(response.text)
        return match.group(1) if match else None

    # -- orchestration -----------------------------------------------------------------
    def fetch_service(self, name: str, config: ServiceConfig, limit: int | None) -> None:
        print(f"[{name}] enumerating {', '.join(config.sitemaps)}")
        locs = self._enumerate(config.sitemaps)
        if locs is None:
            print(f"[{name}] ⚠ enumeration failed — skipping (existing files/manifest left intact)")
            self.encountered_failure = True
            return
        if self.lang != "all":
            locs = [loc for loc in locs if self._matches_lang(loc)]
        print(f"[{name}] {len(locs)} fetchable pages ({self.lang})")

        if self.dry_run:
            for loc in locs[: limit if limit is not None else len(locs)]:
                print(f"  would fetch {loc}.md -> {self._relative_path(loc + '.md', config)}")
            return

        written: list[str] = []
        failed = 0
        first_page_url: str | None = None
        generator: str | None = None
        for loc in locs:
            if limit is not None and len(written) >= limit:
                break
            result = self._fetch_page(loc, config)
            if isinstance(result, _NoSource):
                continue  # no YFM sibling here (section root) — expected, not a failure
            if result is None:
                failed += 1
                continue
            rel_path, text = result
            if generator is None:
                match = _GENERATOR.search(text)
                generator = match.group(1) if match else None
            if first_page_url is None:
                first_page_url = loc
            self._write(rel_path, text)
            written.append(rel_path.relative_to(config.subdir).as_posix())
            print(f"  + {rel_path.as_posix()}")
            time.sleep(self.delay_seconds)

        revision = self._probe_revision(first_page_url) if first_page_url else None
        self._write_manifest(name, config, written, revision, generator)
        summary = (
            f"[{name}] wrote {len(written)} pages · revision={revision} · generator={generator}"
        )
        if failed:
            self.encountered_failure = True
            summary += f" · ⚠ {failed} skipped (fetch failed) — mirror is incomplete"
        print(summary)

    def _write_manifest(
        self,
        name: str,
        config: ServiceConfig,
        pages: list[str],
        revision: str | None,
        generator: str | None,
    ) -> None:
        manifest = {
            "service": name,
            "source_base": config.source_base,
            "sitemaps": list(config.sitemaps),
            "revision": revision,
            "generator": generator,
            "page_count": len(pages),
            "pages": sorted(pages),
        }
        target = self.out_dir / config.subdir / ".fetch-manifest.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(manifest, ensure_ascii=False, indent=2)
        target.write_text(payload + "\n", encoding="utf-8")


@dataclass
class CloudFetcher(_HttpClient):
    """Mirror CC-BY-4.0 Yandex Cloud docs from github.com/yandex-cloud/docs, verbatim.

    Enumeration uses the GitHub trees API on a single service subtree (bounded, so the 7 MB /
    100k-entry truncation limit is never hit); files are fetched from raw.githubusercontent.com
    pinned to the default-branch HEAD commit. Output is byte-for-byte the source — the only
    additions are an ``ATTRIBUTION.md`` and a manifest, per the CC BY 4.0 attribution clause.
    """

    def __post_init__(self) -> None:
        super().__post_init__()
        self.session.headers["Accept"] = "application/vnd.github+json"
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    # -- pin + enumerate ---------------------------------------------------------------
    def _resolve_commit(self) -> str | None:
        """HEAD commit of the repo's default branch — pins the whole corpus for reproducibility."""
        repo = self._get_json(f"{GITHUB_API_BASE}/repos/{CLOUD_OWNER}/{CLOUD_REPO}")
        if not isinstance(repo, dict):
            return None
        branch = repo.get("default_branch", "master")
        head = self._get_json(
            f"{GITHUB_API_BASE}/repos/{CLOUD_OWNER}/{CLOUD_REPO}/commits/{branch}"
        )
        return head.get("sha") if isinstance(head, dict) else None

    def _lang_services(self, lang: str, commit: str) -> dict[str, str]:
        """Map service dir name -> its git-tree SHA for one language root (``ru`` / ``en``)."""
        url = f"{GITHUB_API_BASE}/repos/{CLOUD_OWNER}/{CLOUD_REPO}/contents/{lang}?ref={commit}"
        entries = self._get_json(url)
        if not isinstance(entries, list):
            return {}
        return {e["name"]: e["sha"] for e in entries if e.get("type") == "dir"}

    def _service_files(self, tree_sha: str) -> list[str] | None:
        """Markdown paths (relative to the service dir) via one recursive subtree call. Returns
        None when the API call fails (rate-limit / error) — distinct from a service with 0 files."""
        url = f"{GITHUB_API_BASE}/repos/{CLOUD_OWNER}/{CLOUD_REPO}/git/trees/{tree_sha}?recursive=1"
        data = self._get_json(url)
        if not isinstance(data, dict):
            return None
        if data.get("truncated"):
            print("  ! subtree truncated by GitHub — file list is partial")
        return sorted(
            node["path"]
            for node in data.get("tree", [])
            if node.get("type") == "blob" and node["path"].endswith(".md")
        )

    # -- orchestration -----------------------------------------------------------------
    def run(self, service: str | None, all_services: bool, limit: int | None) -> None:
        commit = self._resolve_commit()
        if commit is None:
            print(
                "! could not resolve yandex-cloud/docs HEAD commit (rate-limited? set GITHUB_TOKEN)"
            )
            self.encountered_failure = True
            return
        langs = ["ru", "en"] if self.lang == "all" else [self.lang]
        for lang in langs:
            available = self._lang_services(lang, commit)
            if not available:
                print(f"[cloud/{lang}] ⚠ no services listed (rate-limited? set GITHUB_TOKEN)")
                self.encountered_failure = True
                continue
            names = sorted(available) if all_services else [service]
            for name in names:
                if name not in available:
                    print(f"[cloud/{lang}] unknown service {name!r} — not in repo")
                    self.encountered_failure = True
                    continue
                self._fetch_service(lang, name, available[name], commit, limit)

    def _fetch_service(
        self, lang: str, service: str, tree_sha: str, commit: str, limit: int | None
    ) -> None:
        files = self._service_files(tree_sha)
        if files is None:
            print(f"[cloud/{lang}/{service}] ⚠ could not list files — skipping (nothing written)")
            self.encountered_failure = True
            return
        print(f"[cloud/{lang}/{service}] {len(files)} markdown files @ {commit[:8]}")

        if self.dry_run:
            for path in files[: limit if limit is not None else len(files)]:
                print(f"  would fetch {lang}/{service}/{path}")
            return

        written: list[str] = []
        failed = 0
        for path in files:
            if limit is not None and len(written) >= limit:
                break
            raw_url = f"{RAW_BASE}/{CLOUD_OWNER}/{CLOUD_REPO}/{commit}/{lang}/{service}/{path}"
            response = self._get(raw_url)
            if response is None or response.status_code != 200:
                if response is not None:
                    print(f"  ! {raw_url} — HTTP {response.status_code}")
                failed += 1
                continue
            self._write_bytes(Path("cloud") / lang / service / path, response.content)
            written.append(path)
            print(f"  + cloud/{lang}/{service}/{path}")
            time.sleep(self.delay_seconds)

        self._write_attribution(lang, service, commit, written)
        summary = f"[cloud/{lang}/{service}] wrote {len(written)} files · {CLOUD_LICENSE}"
        if failed:
            self.encountered_failure = True
            summary += f" · ⚠ {failed} skipped (fetch failed) — set GITHUB_TOKEN if rate-limited"
        print(summary)

    def _write_attribution(self, lang: str, service: str, commit: str, pages: list[str]) -> None:
        base = self.out_dir / "cloud" / lang / service
        source_tree = f"{CLOUD_REPO_URL}/tree/{commit}/{lang}/{service}"
        notice = (
            "# Attribution\n\n"
            f"Source: {source_tree}\n\n"
            f"{CLOUD_COPYRIGHT}. Licensed under the Creative Commons Attribution 4.0 "
            f"International Public License (CC BY 4.0), {CLOUD_LICENSE_URL}.\n\n"
            "Files in this directory are reproduced verbatim from the source repository at the "
            "pinned commit above; only this notice and the manifest have been added.\n"
        )
        (base / "ATTRIBUTION.md").parent.mkdir(parents=True, exist_ok=True)
        (base / "ATTRIBUTION.md").write_text(notice, encoding="utf-8")
        manifest = {
            "service": service,
            "language": lang,
            "source": f"{CLOUD_OWNER}/{CLOUD_REPO}",
            "source_repo": CLOUD_REPO_URL,
            "ref": commit,
            "license": CLOUD_LICENSE,
            "license_url": CLOUD_LICENSE_URL,
            "copyright": CLOUD_COPYRIGHT,
            "page_count": len(pages),
            "pages": sorted(pages),
        }
        payload = json.dumps(manifest, ensure_ascii=False, indent=2)
        (base / ".fetch-manifest.json").write_text(payload + "\n", encoding="utf-8")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mirror Yandex service docs to self-contained YFM Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "service",
        nargs="?",
        help="service to fetch (a diplodoc service name, or any cloud service dir); "
        "omit and pass --all for every service",
    )
    parser.add_argument("--all", action="store_true", help="fetch every service in the source")
    parser.add_argument(
        "--source",
        choices=("diplodoc", "cloud"),
        default="diplodoc",
        help="doc source: 'diplodoc' (yandex.ru rendered .md, default) or "
        "'cloud' (github.com/yandex-cloud/docs, CC BY 4.0)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="stop after writing the first N pages (for validation)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        metavar="DIR",
        help=f"output root (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        metavar="SECONDS",
        help="polite delay between requests (default: 0.2)",
    )
    parser.add_argument(
        "--lang",
        choices=("ru", "en", "all"),
        default="ru",
        help="language(s) to fetch (default: ru; language-agnostic pages are always kept)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="list what would be fetched, no writes"
    )
    args = parser.parse_args(argv)
    if bool(args.service) == bool(args.all):
        parser.error("pass exactly one of a service name or --all")
    if args.source == "diplodoc" and args.service and args.service not in SERVICES:
        valid = ", ".join(sorted(SERVICES))
        parser.error(f"unknown diplodoc service {args.service!r}; choose from: {valid}")
    return args


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    if args.source == "cloud":
        cloud = CloudFetcher(
            out_dir=args.out, delay_seconds=args.delay, dry_run=args.dry_run, lang=args.lang
        )
        cloud.run(service=args.service, all_services=args.all, limit=args.limit)
        if cloud.encountered_failure:
            raise SystemExit(1)
        return
    fetcher = DocsFetcher(
        out_dir=args.out, delay_seconds=args.delay, dry_run=args.dry_run, lang=args.lang
    )
    names = sorted(SERVICES) if args.all else [args.service]
    for name in names:
        fetcher.fetch_service(name, SERVICES[name], args.limit)
    if fetcher.encountered_failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
