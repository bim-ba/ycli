#!/usr/bin/env python
"""What each published operation does: its kind of action, and the word the API uses for it.

Step 2 of the naming inventory (issue #268). ``scripts/api_snapshot/<service>.json`` lists the
operations; this script writes ``<service>.kinds.json`` beside each, one row per operation:

* ``verb``: the API's own word for the action, read from the operation's own name
  (``getDashboard`` -> ``get``, ``PublishResource`` -> ``publish``); empty when the name has none.
* ``kind``: WHAT the operation does to its object, one of :data:`KINDS`.
* ``aspect``: WHAT IS SPECIAL about the object or the manner, one of :data:`ASPECTS` or empty.
* ``by``: how the kind was decided: ``name`` (the verb), ``shape`` (the method and the path),
  ``name+shape``, a named rule, or ``hand``.

The boundary between the two columns, stated once. ``kind`` answers "which verb would a person
use": read one, read many, search, count, create, change some fields, replace a whole value,
delete, add to a set, remove from a set, change a state, send, or none of these. ``aspect``
never changes that answer; it marks the operations a naming system must name alike across
services: permissions (``access``), members of a set (``membership``), bytes going in or out
(``file``), many objects in one call (``bulk``), an asynchronous operation started or polled
(``long-running``), an analytics query (``report``). Uploading a file is ``create`` with
``file``; reading who may see a page is ``list`` with ``access``; polling an export is ``get``
with ``long-running``.

The script proposes; a person decides what it cannot. The name comes first (it is the API's
own word), the shape of the request refines a read and answers where there is no name, and a
class of disagreements is closed by a named rule. What is left is decided by hand in
``<service>.decisions.json``, each row with its reason.

Usage::

    uv run scripts/api_kinds.py            # rewrite every <service>.kinds.json
    uv run scripts/api_kinds.py --check    # exit 1 if one is stale
    uv run scripts/api_kinds.py --summary  # the tables for issue #268, as Markdown
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import api_surface  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scripts.api_surface import Operation

KINDS = (
    "get",
    "list",
    "search",
    "count",
    "create",
    "update",
    "replace",
    "delete",
    "add",
    "remove",
    "state",
    "send",
    "other",
)
ASPECTS = ("access", "membership", "file", "bulk", "long-running", "report")

_STATE_VERBS = (
    "publish",
    "unpublish",
    "archive",
    "unarchive",
    "suspend",
    "resume",
    "start",
    "stop",
    "cancel",
    "move",
    "copy",
    "clone",
    "restore",
    "confirm",
    "moderate",
    "accept",
    "reject",
    "approve",
    "enable",
    "disable",
    "activate",
    "deactivate",
    "pin",
    "unpin",
    "recrawl",
    "verify",
    "restart",
    "close",
    "revoke",
    "transition",
    "execute",
    "abort",
    "finish",
    "skip",
    "hide",
    "merge",
    "block",
    "unblock",
    "recover",
    "undelete",
    "recheck",
    "transfer",
    "logout",
    "reprocess",
)
# The API's own verb -> the kind it usually means. A verb that is absent here is still
# recorded as the operation's verb; it just does not decide the kind.
VERB_KIND = {
    # `find` is a read like `get`: the path says whether of one or of many.
    **dict.fromkeys(("get", "read", "fetch", "show", "info", "find", "download"), "get"),
    "list": "list",
    **dict.fromkeys(("search", "query", "suggest"), "search"),
    "count": "count",
    **dict.fromkeys(
        (
            "create",
            "add",
            "new",
            "register",
            "generate",
            "upload",
            "import",
            "export",
            "attach",
            "submit",
        ),
        "create",
    ),
    **dict.fromkeys(
        ("update", "edit", "modify", "change", "patch", "rename", "append", "extend"), "update"
    ),
    **dict.fromkeys(("put", "set", "replace", "save"), "replace"),
    **dict.fromkeys(("delete", "del", "remove", "clear", "drop", "clean"), "delete"),
    **dict.fromkeys(("grant", "assign"), "add"),
    # A computation that stores nothing: it reads no object and changes none.
    **dict.fromkeys(("check", "validate", "calculate", "estimate", "deduplicate"), "other"),
    **dict.fromkeys(_STATE_VERBS, "state"),
    **dict.fromkeys(("send", "notify", "share"), "send"),
}
# The kinds that only read: what a `GET` can be.
READS = ("get", "list", "search", "count")
# The last segment of a path that names one thing, not a collection.
SINGLETONS = (
    "info",
    "myself",
    "me",
    "settings",
    "status",
    "quota",
    "summary",
    "limits",
    "capacity",
)
# A last word that names many things without a plural `s`.
COLLECTIONS = ("list", "all", "history", "changelog", "worklog", "queue", "relative", "suggest")
# Words of a generated name that say nothing about its object.
_NAME_NOISE = ("view", "public", "paginate", "get")
# Words of a name or a path that mark an aspect, in the order they are tried.
ASPECT_WORDS = {
    "bulk": ("bulk", "batch", "bulkchange", "mass"),
    "access": ("access", "accesses", "grant", "grants", "permission", "permissions", "acl"),
    "membership": ("member", "members", "cohosts", "delegate", "delegates", "followers"),
    "long-running": ("operation", "operations", "task", "tasks", "async"),
    "file": (
        "upload",
        "download",
        "export",
        "import",
        "attachment",
        "attachments",
        "file",
        "files",
        "image",
        "images",
        "avatar",
    ),
    "report": ("stat", "stats", "statistics", "report", "reports", "analytics"),
}
_WORD = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+")
_PLACEHOLDER = re.compile(r"\{[^}]*\}|<[^>]*>")
_SHAPE = {"PATCH": "update", "PUT": "replace", "DELETE": "delete", "POST": "create"}
# Fewer operations than this say nothing about whether a service uses one method for all.
_RPC_MINIMUM = 4


@dataclass(frozen=True)
class Kind:
    """One operation's row of ``<service>.kinds.json``; the first four fields identify it."""

    method: str
    base: str
    path: str
    name: str
    verb: str
    kind: str
    aspect: str
    by: str
    why: str = ""


def words(text: str) -> list[str]:
    """The lowercase words of a name or a path, whatever its case style.

    Examples:
        >>> words("UserService_GetDomain2fa")
        ['user', 'service', 'get', 'domain', '2', 'fa']
        >>> words("/pages/{idx}/access-requests")
        ['pages', 'access', 'requests']
    """
    return [word.lower() for word in _WORD.findall(_PLACEHOLDER.sub(" ", text))]


def _own_name(operation: Operation) -> str:
    """The operation's name without the module path a framework puts before it.

    Wiki and Forms publish the name of the view: ``wiki_api_v2_public_upload_sessions_views_
    abort_all_view``. What follows ``_views_`` names the operation; before it ``upload`` is
    the module, not the verb.
    """
    return operation.name.rpartition("_views_")[2]


def _many(word: str) -> bool:
    """Whether ``word`` names many things: a collection word or a plural, not a singleton."""
    plural = word.endswith("s") and not word.endswith(("ss", "us")) and len(word) > 2
    return word in COLLECTIONS or (plural and word not in SINGLETONS)


def own_verb(operation: Operation) -> str:
    """The API's own verb: the first known verb of the operation's name, else of its address.

    A name without a verb leaves the last segment of the path to say it (``POST …/recrawl``,
    ``POST /revoke_token``).

    Examples:
        >>> from scripts.api_surface import Operation
        >>> own_verb(Operation("POST", "/x", name="events_b2b_v1_views_publish_survey_view"))
        'publish'
        >>> own_verb(Operation("POST", "/sitemaps/{id}/recrawl", name="re-crawl-initiation"))
        'recrawl'
        >>> own_verb(Operation("GET", "/counters", name="counters"))
        ''
    """
    last = operation.path.rstrip("/").rsplit("/", 1)[-1]
    found = [word for word in (*words(_own_name(operation)), *words(last)) if word in VERB_KIND]
    if operation.method == "GET":
        # A `GET` reads: another verb in its name is part of the object (`host-recrawl-get`).
        found = [word for word in found if VERB_KIND[word] in READS]
    return next(iter(found), "")


def shape_kind(operation: Operation) -> str:
    """The kind the method and the path alone suggest; ``""`` where they say nothing.

    A ``GET`` reads many when the path ends with a plural or a collection word, or the name
    does (``/queues``, ``getCampaigns``, ``…/history``), and one object otherwise: a path that
    ends with a placeholder, with a singleton (``/settings``) or with a singular noun
    (``/resources/download``). A ``POST`` creates only when the path ends with a plain noun:
    ``POST …/publish`` or an RPC address says nothing by its shape.

    Examples:
        >>> from scripts.api_surface import Operation
        >>> shape_kind(Operation("GET", "/queues/{id}")), shape_kind(Operation("GET", "/queues"))
        ('get', 'list')
        >>> shape_kind(Operation("POST", "/rpc/getDashboard"))
        ''
    """
    last = operation.path.rstrip("/").rsplit("/", 1)[-1]
    if operation.method == "GET":
        if last == "count":
            return "count"
        if _PLACEHOLDER.fullmatch(last) or last in SINGLETONS or not last:
            return "get"
        named = [word for word in words(_own_name(operation)) if word not in _NAME_NOISE]
        return "list" if any(map(_many, [*words(last)[-1:], *named[-1:]])) else "get"
    if operation.method not in _SHAPE:
        return ""
    if operation.method == "POST" and (
        _PLACEHOLDER.fullmatch(last) or any(word in VERB_KIND for word in words(last))
    ):
        return ""
    return _SHAPE[operation.method]


def aspect_of(operation: Operation) -> str:
    """The aspect the words of the name and the path mark, else ``""``.

    Examples:
        >>> from scripts.api_surface import Operation
        >>> aspect_of(Operation("POST", "/bulkchange/_update", name="bulk-update-issues"))
        'bulk'
    """
    found = {*words(operation.name), *words(operation.base), *words(operation.path)}
    return next((aspect for aspect, marks in ASPECT_WORDS.items() if found & set(marks)), "")


def proposed(operation: Operation, *, rpc: bool) -> tuple[str, str]:
    """The kind the script proposes for ``operation`` and how it got there; ``("", "")`` if none.

    Args:
        operation: The published operation.
        rpc: Whether every operation of the service is sent with one method (RPC, a WSDL),
            so that the shape of a request says nothing.

    Returns:
        The kind and the way it was decided.
    """
    verb = own_verb(operation)
    shape = "" if rpc else shape_kind(operation)
    kind = VERB_KIND.get(verb, "")
    if not kind:
        return (shape, "shape") if shape else ("", "")
    if kind == "get" and shape == "list":
        return "list", "name+shape"  # APIs say "get" for a collection too
    if kind in {"get", "list"} and operation.method == "POST" and not rpc:
        return "search", "rule:read-by-post"  # a read with its filter in the body
    if kind == "get" and rpc and _many((words(_own_name(operation)) or [""])[-1]):
        return "list", "rule:plural"  # with one method for all, only the name tells one from many
    if kind == "get" and "SelectionCriteria" in operation.request:
        return "search", "rule:selection"  # Direct's `get` takes a filter and returns many
    if aspect_of(operation) == "membership" and kind in {"create", "delete"}:
        # Adding to a set and removing from it are not creating and deleting the member.
        return {"create": "add", "delete": "remove"}[kind], "rule:membership"
    return kind, "name"


def _key(row: Operation | Kind) -> tuple[str, str, str, str]:
    return row.method, row.base, row.path, row.name


def decisions(service: str) -> dict[tuple[str, str, str, str], dict[str, str]]:
    """The hand decisions of ``service``, by operation; empty when it has none."""
    path = api_surface.SNAPSHOTS / f"{service}.decisions.json"
    if not path.exists():
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {
        (row["method"], row.get("base", ""), row["path"], row.get("name", "")): row for row in rows
    }


def classify(service: str) -> list[Kind]:
    """Every operation of ``service`` with its verb, kind and aspect.

    Args:
        service: A listed service.

    Returns:
        One row per operation of the service's snapshot, in its order.

    Raises:
        ValueError: An operation has no kind, or a hand decision matches no operation.
    """
    operations = api_surface.load(service)
    methods = {operation.method for operation in operations}
    # One method for every operation, and not `GET`: the method then says nothing.
    rpc = len(methods) == 1 and "GET" not in methods and len(operations) >= _RPC_MINIMUM
    by_hand = decisions(service)
    rows, undecided = [], []
    for operation in operations:
        kind, by = proposed(operation, rpc=rpc)
        aspect, why = aspect_of(operation), ""
        if (decision := by_hand.pop(_key(operation), None)) is not None:
            kind, by, why = decision.get("kind", ""), "hand", decision.get("why", "")
            aspect = decision.get("aspect", aspect)
            if kind not in KINDS or aspect not in ("", *ASPECTS) or not why:
                raise ValueError(
                    f"{service}: the hand decision for {operation.method} {operation.path} needs "
                    f"a kind of {KINDS}, an aspect of {ASPECTS} or none, and a reason"
                )
        if not kind:
            undecided.append(operation)
        rows.append(
            Kind(
                *_key(operation),
                verb=own_verb(operation),
                kind=kind,
                aspect=aspect,
                by=by,
                why=why,
            )
        )
    if by_hand:
        raise ValueError(f"{service}: hand decisions for no operation: {sorted(by_hand)}")
    if undecided:
        names = ", ".join(f"{o.method} {o.base}{o.path} {o.name}".strip() for o in undecided)
        raise ValueError(f"{service}: {len(undecided)} operations have no kind: {names}")
    return rows


def dump(rows: Iterable[Kind]) -> str:
    """The text of a kinds file: one JSON object per line, empty fields left out."""
    lines = [
        json.dumps(
            {name: value for name, value in asdict(row).items() if value}, ensure_ascii=False
        )
        for row in rows
    ]
    return "[\n" + ",\n".join(lines) + "\n]\n"


def summary() -> str:
    """The tables for issue #268: kinds by service, and the verbs each kind goes by.

    Returns:
        Markdown: a table of operations per kind and service, a table of the APIs' own verbs
        per kind (with the services that use each), and the count per aspect.
    """
    rows = {service: classify(service) for service in api_surface.LISTED}
    total = sum(len(found) for found in rows.values())
    lines = [f"{total} operations of {len(rows)} services.", ""]
    lines += ["| Service | " + " | ".join(KINDS) + " | all |", "|---|" + "---:|" * (len(KINDS) + 1)]
    for service, found in rows.items():
        counts = [sum(row.kind == kind for row in found) for kind in KINDS]
        cells = " | ".join(str(count or "") for count in counts)
        lines.append(f"| {service} | {cells} | {len(found)} |")
    every = [row for found in rows.values() for row in found]
    totals = " | ".join(str(sum(row.kind == kind for row in every)) for kind in KINDS)
    lines += [f"| **all** | {totals} | {total} |", ""]
    lines += ["| Kind | The APIs' own verbs (operations; services) |", "|---|---|"]
    for kind in KINDS:
        verbs: dict[str, list[str]] = {}
        for service, found in rows.items():
            for row in found:
                if row.kind == kind:
                    verbs.setdefault(row.verb or "(none)", []).append(service)
        cells = "; ".join(
            f"`{verb}` {len(services)} ({', '.join(sorted(set(services)))})"
            for verb, services in sorted(verbs.items(), key=lambda item: -len(item[1]))
        )
        lines.append(f"| {kind} | {cells} |")
    lines += ["", "| Aspect | Operations | Kinds |", "|---|---:|---|"]
    for aspect in ASPECTS:
        found = [row for row in every if row.aspect == aspect]
        kinds = ", ".join(
            f"{kind} {count}" for kind in KINDS if (count := sum(row.kind == kind for row in found))
        )
        lines.append(f"| {aspect} | {len(found)} | {kinds} |")
    by_hand = sum(row.by == "hand" for row in every)
    lines += ["", f"Decided by hand: {by_hand} of {total}."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Write the kinds files, or with ``--check`` report the stale ones and exit 1."""
    parser = argparse.ArgumentParser(description="Write the kind of action of every operation.")
    parser.add_argument("--check", action="store_true", help="exit 1 if a kinds file is stale")
    parser.add_argument("--summary", action="store_true", help="print the tables for #268")
    args = parser.parse_args(argv)
    if args.summary:
        sys.stdout.write(summary())
        return 0
    stale = []
    for service in api_surface.LISTED:
        path = api_surface.SNAPSHOTS / f"{service}.kinds.json"
        text = dump(classify(service))
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(path.name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print(f"api_kinds: stale: {', '.join(stale)}; run scripts/api_kinds.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
