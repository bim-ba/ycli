"""Generate what the documentation site says about each service in the registry.

The home page shows one card per service and names the services in its slogan; a service's
overview page (``docs/<language>/services/<name>.md``) opens with the same facts, says what
signing in needs and links to the service's reference. All of it is written here, from
``ycli.yandex.registry.SERVICES`` and the counts the README's Coverage section uses, as the
fragments the pages include::

    --8 < --"docs/examples/services/cards.en.md"

A service added to the registry gets its card by itself. A service is *in progress* while
Yandex publishes operations ycli neither wraps nor leaves out on purpose
(``api_drift.NOT_WRAPPED``): its card then says how many of the published ones are wrapped.

Usage::

    uv run scripts/gen_services.py            # write the fragments
    uv run scripts/gen_services.py --check    # exit 1 if one is stale, missing or unused

``tests/docs/test_services.py`` runs the check.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:  # `scripts` and `tests` are importable from anywhere
    sys.path.insert(0, str(ROOT))

from scripts import gen_coverage  # noqa: E402

from ycli.settings import (  # noqa: E402
    CLOUD_ORGANIZATION_ID_ENV,
    IAM_TOKEN_ENV,
    OAUTH_TOKEN_ENV,
    ORGANIZATION_ID_ENV,
    SERVICE_ACCOUNT_KEY_FILE_ENV,
)
from ycli.yandex.registry import SERVICES  # noqa: E402

if TYPE_CHECKING:
    from scripts import api_drift

    from ycli.yandex.core.profile import ServiceProfile
    from ycli.yandex.service import Service

FRAGMENTS = ROOT / "docs" / "examples" / "services"
LANGUAGES = ("en", "ru")
# The Russian site links to the English reference, which is not translated.
SITE_URL = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))["project"][
    "site_url"
]
SURFACES = "CLI · MCP · Python"
SLOGAN = {
    "en": "**Yandex business services for people and for agents.** {services} from a command "
    "line, an MCP server and Python: one tool, and one name for each operation everywhere.",
    "ru": "**Бизнес-сервисы Яндекса для людей и для агентов.** {services} из командной строки, "
    "MCP-сервера и Python: один инструмент, и у каждой операции везде одно имя.",
}
AND = {"en": "and", "ru": "и"}
IN_PROGRESS = {"en": "in progress", "ru": "в работе"}
OPERATIONS = {
    "en": ("{count} operations", "{wrapped} of {published} operations"),
    "ru": ("операций: {count}", "операций: {wrapped} из {published}"),
}
PROGRESS_NOTE = {
    "en": "ycli wraps {title} section by section: {wrapped} of the {published} operations "
    "Yandex publishes so far.",
    "ru": "ycli оборачивает {title} раздел за разделом: пока {wrapped} из {published} операций, "
    "которые публикует Яндекс.",
}


@dataclass(frozen=True)
class Facts:
    """What the site says about one service, counted from the code and the API snapshot."""

    name: str
    titles: dict[str, str]
    summaries: dict[str, str]
    emoji: str
    operations: int
    wrapped: int
    published: int
    in_progress: bool


def summary(service: Service) -> str:
    """The one line of a card, from the service's CLI help.

    Examples:
        >>> from ycli.yandex.wiki import SERVICE
        >>> summary(SERVICE)
        'Pages, grids, comments, attachments.'
    """
    _, separator, rest = service.help.partition(": ")
    if not separator:
        raise SystemExit(f"gen_services: {service.name}'s help has no 'Yandex <Name>: ' prefix")
    return rest[0].upper() + rest[1:]


def in_progress(drift: api_drift.Drift) -> bool:
    """Whether Yandex publishes an operation ycli neither wraps nor leaves out on purpose."""
    return drift.wrapped < len(drift.published) - len(drift.excluded)


def facts() -> list[Facts]:
    """Every registry service, in the registry's order."""
    reports = {report.slug: report for report in gen_coverage._reports()}
    drifts = {drift.service: drift for drift in gen_coverage.api_drifts()}
    found = []
    for service in SERVICES:
        english, russian, _ = gen_coverage.TITLES[service.name]
        drift = drifts[service.name]
        found.append(
            Facts(
                name=service.name,
                titles={"en": english, "ru": russian},
                summaries={
                    "en": summary(service),
                    "ru": gen_coverage.SUMMARIES_RU[service.name],
                },
                emoji=gen_coverage.EMOJI[service.name],
                operations=reports[service.name].operation_count,
                wrapped=drift.wrapped,
                published=len(drift.published),
                in_progress=in_progress(drift),
            )
        )
    return found


def operations(fact: Facts, language: str) -> str:
    """The count a card shows: ``190 operations``, or ``1 of 141 operations`` in progress."""
    whole, part = OPERATIONS[language]
    if fact.in_progress:
        return part.format(wrapped=fact.wrapped, published=fact.published)
    return whole.format(count=fact.operations)


def mark(fact: Facts, language: str) -> str:
    """The yellow mark of a service in progress: the theme's own ``<mark>``, no CSS of ours."""
    return f" <mark>{IN_PROGRESS[language]}</mark>" if fact.in_progress else ""


def cards(found: list[Facts], language: str) -> str:
    """The row of cards on the home page; a card links to the service's overview page."""
    lines = ['<div class="grid cards" markdown>', ""]
    for fact in found:
        title = fact.titles[language]
        lines += [
            f"-   {fact.emoji} **[{title}](services/{fact.name}.md)**{mark(fact, language)}",
            "",
            f"    {fact.summaries[language]}",
            "",
            f"    `{operations(fact, language)}`",
            "",
            f"    {SURFACES}",
            "",
        ]
    return "\n".join([*lines, "</div>", ""])


def slogan(found: list[Facts], language: str) -> str:
    """The home page's first paragraph, naming every service."""
    titles = [fact.titles[language] for fact in found]
    services = f"{', '.join(titles[:-1])} {AND[language]} {titles[-1]}"
    return SLOGAN[language].format(services=services) + "\n"


def header(fact: Facts, language: str) -> str:
    """The top of an overview page: the card's facts under the page's heading.

    The mark stands in the facts line: in the heading it would enter the page's title.
    """
    lines = [
        f"# {fact.emoji} {fact.titles[language]}",
        "",
        fact.summaries[language],
        "",
        f"`{operations(fact, language)}` · {SURFACES}{mark(fact, language)}",
    ]
    if fact.in_progress:
        note = PROGRESS_NOTE[language].format(
            title=fact.titles[language], wrapped=fact.wrapped, published=fact.published
        )
        lines += ["", note]
    return "\n".join([*lines, ""])


def sign_in(profile: ServiceProfile, language: str) -> str:
    """What signing in to a service needs: which token, and which organization id."""
    if profile.oauth_token:
        token = {
            "en": f"`{OAUTH_TOKEN_ENV}`: a Yandex ID OAuth token; `ycli auth login` gets one. "
            f"A ready IAM token in `{IAM_TOKEN_ENV}` works in its place",
            "ru": f"`{OAUTH_TOKEN_ENV}`: OAuth-токен Яндекс ID, его получает `ycli auth login`. "
            f"Вместо него подойдёт готовый IAM-токен в `{IAM_TOKEN_ENV}`",
        }
    else:
        token = {
            "en": f"`{IAM_TOKEN_ENV}`: an IAM token, or a service account's key in "
            f"`{SERVICE_ACCOUNT_KEY_FILE_ENV}`. A Yandex ID OAuth token is not taken",
            "ru": f"`{IAM_TOKEN_ENV}`: IAM-токен, либо ключ сервисного аккаунта в "
            f"`{SERVICE_ACCOUNT_KEY_FILE_ENV}`. OAuth-токен Яндекс ID не подходит",
        }
    kinds = (
        (profile.org_header, ORGANIZATION_ID_ENV, {"en": "Yandex 360", "ru": "Яндекс 360"}),
        (
            profile.cloud_org_header,
            CLOUD_ORGANIZATION_ID_ENV,
            {"en": "Yandex Cloud", "ru": "Yandex Cloud"},
        ),
    )
    sent = {"en": "sent as", "ru": "уходит в заголовке"}
    organization = {"en": " or ", "ru": " или "}[language].join(
        f"`{variable}` ({kind[language]}, {sent[language]} `{header_name}`)"
        for header_name, variable, kind in kinds
        if header_name
    ) or {"en": "none", "ru": "не нужна"}[language]
    columns = {
        "en": ("You need", "Set", "a token", "an organization"),
        "ru": ("Нужно", "Задайте", "токен", "организация"),
    }[language]
    more = {
        "en": "How to get each of them: [Authenticate](../how-to/authenticate.md).",
        "ru": "Как получить каждое значение: [Аутентификация](../how-to/authenticate.md).",
    }[language]
    return "\n".join(
        [
            f"| {columns[0]} | {columns[1]} |",
            "|---|---|",
            f"| {columns[2]} | {token[language]} |",
            f"| {columns[3]} | {organization} |",
            "",
            more,
            "",
        ]
    )


def links(name: str, language: str) -> str:
    """Where a service's reference is: its CLI, MCP and SDK pages, and the guide for an agent."""
    if language == "en":
        targets = [f"../reference/{surface}/{name}.md" for surface in ("cli", "mcp", "sdk")]
        guides = "../reference/mcp/prompts-and-resources.md#guides"
        labels = ("CLI commands", "MCP tools", "Python SDK", "Guide for an agent")
        guide = f"the MCP resource `ycli://{name}/guide`"
    else:
        targets = [f"{SITE_URL}reference/{surface}/{name}/" for surface in ("cli", "mcp", "sdk")]
        guides = f"{SITE_URL}reference/mcp/prompts-and-resources/#guides"
        labels = (
            "Команды CLI (англ.)",
            "MCP-инструменты (англ.)",
            "Python SDK (англ.)",
            "Гид для агента (англ.)",
        )
        guide = f"MCP-ресурс `ycli://{name}/guide`"
    lines = [f"- [{label}]({target})" for label, target in zip(labels, targets, strict=False)]
    return "\n".join([*lines, f"- [{labels[3]}]({guides}): {guide}", ""])


def build() -> dict[Path, str]:
    """Every fragment to write, keyed by its path."""
    found = facts()
    profiles = {service.name: service.profile for service in SERVICES}
    fragments: dict[Path, str] = {}
    for language in LANGUAGES:
        fragments[FRAGMENTS / f"cards.{language}.md"] = cards(found, language)
        fragments[FRAGMENTS / f"slogan.{language}.md"] = slogan(found, language)
        for fact in found:
            stem = f"{fact.name}.{{}}.{language}.md"
            fragments[FRAGMENTS / stem.format("header")] = header(fact, language)
            fragments[FRAGMENTS / stem.format("sign-in")] = sign_in(profiles[fact.name], language)
            fragments[FRAGMENTS / stem.format("links")] = links(fact.name, language)
    return fragments


def main(argv: list[str] | None = None) -> int:
    """Write the fragments, or with ``--check`` report the stale and unused ones and exit 1."""
    parser = argparse.ArgumentParser(description="Generate the site's per-service fragments.")
    parser.add_argument("--check", action="store_true", help="exit 1 if a fragment is stale")
    args = parser.parse_args(argv)
    fragments = build()
    orphans = [path for path in FRAGMENTS.glob("*.md") if path not in fragments]
    if args.check:
        stale = [
            path
            for path, text in fragments.items()
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        for path in [*stale, *orphans]:
            print(f"stale: {path.relative_to(ROOT)}", file=sys.stderr)
        if stale or orphans:
            print("run: uv run scripts/gen_services.py", file=sys.stderr)
            return 1
        return 0
    for path in orphans:
        path.unlink()
    for path, text in fragments.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
