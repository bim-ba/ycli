# Yandex developer-service landscape

A point-in-time survey of which Yandex developer services expose **public REST API
documentation** — the map of what `ycli` could wrap next, and what is deliberately out of
scope. It complements [`api-coverage.md`](api-coverage.md) (which tracks coverage of the
services already wrapped: Tracker, Wiki, Forms).

> **Provenance.** Verified **2026-07-10**. The service list was extracted from the live dev hub
> `https://yandex.ru/dev/` and cross-probed against the Yandex 360 family. Each candidate was
> first `curl`-checked (HTTP status + final URL after redirects); every **360-relevant** entry
> was then **Playwright-verified** — navigated in a real browser and confirmed by the rendered
> page title / nav tree to be a genuine API-reference page rather than a 404, a marketing page,
> or a Passport-SSO block (Yandex dev pages carry anti-headless protection, so a bare `curl` 200
> is not sufficient evidence). This is a discovery snapshot, not a generated artifact — re-run
> the method above to refresh it.

`ycli` today wraps **Tracker, Wiki, Forms** across SDK + CLI + read-only MCP. DataLens is
**vendored** under `docs/references/yandex/datalens/` but not wrapped.

## Uncovered, Yandex-360-relevant (candidates)

| Service | Docs | Real REST API? | Covered? | What it is |
|---------|------|:--------------:|:--------:|------------|
| **Yandex 360 API (api360)** | `yandex.ru/dev/api360/doc/ru/` | ✅ Playwright | — | Org-admin / directory REST: Organizations, Users, Groups, Departments, ExternalContacts, mail user-settings, antispam allowlist, routing rules, domain sender policies, shared/delegated mailboxes, Domains, DomainDNS, 2FA, Sessions, Passwords, AuditLog, ServiceApplications |
| **Telemost API** | `yandex.ru/dev/telemost/doc/ru/` | ✅ Playwright | — | Video-meeting REST: conference CRUD, cohosts, settings. Public OpenAPI spec at `doc-static.yandex.net/dev/telemost/api-specification.yaml` |
| **Disk REST API** | `yandex.ru/dev/disk-api/doc/ru/` | ✅ Playwright | — | File-storage REST (part of 360): files/folders, upload/download, publish, trash, async ops (plus a legacy WebDAV surface) |
| **Yandex ID** | `yandex.ru/dev/id/doc/ru/` | ✅ Playwright | partial | OAuth token flows + user-info endpoint. `ycli` already consumes it for auth; only a `whoami`/userinfo read would be new surface |
| DataLens | `datalens.ru/opensource/docs/` | ⚠️ partial | vendored | BI UI tool; opensource docs expose no REST reference, Cloud API is Passport-SSO-gated. Low API ROI — defer |

### Merged / superseded (do **not** cover separately)

| Service | Docs | Why skip |
|---------|------|----------|
| Connect / Directory | redirects → api360 | Legacy org-directory API, **merged into api360** |
| Mail for Domain (pdd) | `yandex.ru/dev/pdd/` | Legacy mail-for-domain admin, largely **superseded by api360** mail services |

### Protocol-only (no REST surface to wrap)

| Service | Protocol | Note |
|---------|----------|------|
| Calendar | CalDAV (`caldav.yandex.ru`) | 360 service, but no REST API |
| Contacts | CardDAV (`carddav.yandex.ru`) | 360 service, but no REST API |
| Mail (messages) | IMAP / SMTP | Only mail *admin* settings are REST — via api360 |

## Out of scope (real dev services, but not the 360 workspace theme)

Consumer / ads / cloud-infra APIs, confirmed live but outside `ycli`'s remit:
Metrica, Direct, Audience, Webmaster, Market Partner, Weather, Translate / AI Studio,
Dictionary, SpeechKit, SmartCaptcha, Maps / Geocoder / Suggest, Yandex Cloud, Dialogs (Alice).

## Recommended next to cover — ranked

1. **api360** — the flagship next step: the **org-management layer** that complements
   Tracker/Wiki/Forms (users, groups, departments, domains, mail, mailboxes, 2FA, audit logs,
   service apps). Large but well-structured (17 named services under one host); highest
   strategic value for a "360 workspace" toolkit.
2. **Telemost** — small, clean, fully-REST (conference CRUD + cohosts + settings) with a
   **published OpenAPI spec**. Fastest high-quality win.
3. **Disk** — real, well-documented file API in 360; enables file/attachment workflows.
   Larger surface (upload/download/publish/async ops) — medium effort.
4. **Yandex ID user-info** — tiny add: the OAuth token is already held, so a `whoami`/userinfo
   read is nearly free and useful for auth diagnostics. Low priority, low effort.
5. **DataLens** — already vendored, but public REST is thin and Cloud/SSO-gated; defer until a
   concrete BI use-case appears.

*Skip Connect and pdd (superseded by api360); skip Calendar/Contacts/Mail (CalDAV/CardDAV/IMAP,
no REST).*
