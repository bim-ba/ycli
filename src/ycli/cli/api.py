"""``ycli api`` — call any endpoint ycli has not wrapped, with the same auth, retries and output.

Modelled on ``gh api``: the method defaults to GET (POST once fields or ``--input`` are given),
``-f``/``-F`` build the query string of a GET or the JSON body of a write, and the answer prints
through the normal output path, so ``-o``, ``--jq``, ``--yes`` and ``--dry-run`` work as they do
everywhere. The request is an :class:`~ycli.yandex.core.endpoint.Endpoint` sent through the
service's own client, so its effect follows the method: a ``DELETE`` asks for ``--yes``.
"""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, cast
from urllib.parse import parse_qs, urlsplit

import typer

from ycli.cli.api_response import ApiResponse
from ycli.cli.fields import parse_fields
from ycli.cli.output import BinaryResult
from ycli.cli.typedefs import AllOption, LimitOption
from ycli.settings import AppConfig
from ycli.yandex.core.endpoint import Endpoint, Paged, check_path
from ycli.yandex.errors import YandexClientError
from ycli.yandex.registry import SERVICES

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    import httpx2

    from ycli.yandex.core.endpoint import Method
    from ycli.yandex.service import Service

# Help text lives with the root sub-app list (ycli.cli.app).
app = typer.Typer(name="api", add_completion=False)

# These carry their fields in the query string; every other method sends them as a JSON body.
_QUERY_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "DELETE"})
_SERVICE_NAMES = ", ".join(service.name for service in SERVICES)
_PAGINATED_NAMES = ", ".join(service.name for service in SERVICES if service.pagination) or "none"


@app.command()
def api(
    path: Annotated[
        str,
        typer.Argument(
            metavar="PATH",
            help="Path under the service's base URL (issues/DE-1), or a full URL of a service.",
        ),
    ],
    service: Annotated[
        str | None,
        typer.Option(
            "--service",
            metavar="SERVICE",
            help=f"{_SERVICE_NAMES}; may be left out for a full URL.",
        ),
    ] = None,
    method: Annotated[
        str | None,
        typer.Option(
            "--method", "-X", help="HTTP method (default GET, or POST with fields or --input)."
        ),
    ] = None,
    field: Annotated[
        list[str] | None,
        typer.Option(
            "--field",
            "-F",
            metavar="KEY=VALUE",
            help="Typed field: true/false/null/numbers/JSON, @FILE (or @- for stdin) reads text; "
            "key\\[sub]=v nests and key\\[]=v makes an array.",
        ),
    ] = None,
    raw_field: Annotated[
        list[str] | None,
        typer.Option("--raw-field", "-f", metavar="KEY=VALUE", help="String field, never typed."),
    ] = None,
    header: Annotated[
        list[str] | None,
        typer.Option("--header", "-H", metavar="'NAME: VALUE'", help="Extra request header."),
    ] = None,
    input_file: Annotated[
        str | None,
        typer.Option(
            "--input",
            metavar="FILE",
            help="Send FILE (or - for stdin) as the raw body, JSON unless -H says otherwise; "
            "fields then go to the query string.",
        ),
    ] = None,
    paginate: Annotated[
        bool,
        typer.Option(
            "--paginate",
            help="Follow the pages of a GET listing and print every item as one JSON array "
            f"(works for {_PAGINATED_NAMES}: the other services page in more than one way).",
        ),
    ] = False,
    limit: LimitOption = None,
    all_: AllOption = False,
    *,
    context: typer.Context,
    config: AppConfig,
) -> ApiResponse | str | BinaryResult | None:
    """Call any endpoint of Tracker, Wiki or Forms, authenticated like every other command.

    ycli api issues/DE-1 --service tracker --jq .summary

    ycli api issues/DE-1/comments --service tracker -F text=@note.md   (POST)

    ycli api pages/descendants --service wiki -f slug=docs --paginate
    """
    fields = parse_fields(field, raw=raw_field, structured=True)
    content = _read_input(input_file)
    target, relative = _resolve_target(path, service)
    # Paging is a read, so ``--paginate -f k=v`` stays a GET with its fields in the query.
    verb = (
        ("POST" if (fields or content is not None) and not paginate else "GET")
        if method is None
        else method
    ).upper()
    pagination = target.listing_pagination()
    if paginate:
        _check_paginate(target, pagination, verb)
    elif limit is not None or all_:
        raise typer.BadParameter("--limit and --all need --paginate.", param_hint="--limit")
    in_query = verb in _QUERY_METHODS or content is not None
    # httpx replaces a path's own query with ``params``, so the two are merged here.
    path_only, _, own_query = relative.partition("?")
    params = parse_qs(own_query, keep_blank_values=True) | (_query(fields) if in_query else {})
    headers = _headers(header)
    if content is not None and not any(name.lower() == "content-type" for name in headers):
        headers["Content-Type"] = "application/json"
    try:
        endpoint = Endpoint(
            cast("Method", verb),
            path_only,
            params=params,
            json=None if in_query else fields or None,
            content=content,
            headers=headers,
            parser=_decode,
        )
    except ValueError as exc:  # an unknown method
        raise typer.BadParameter(str(exc), param_hint="--method") from exc
    client = context.find_root().obj.resolve(target.client_class())
    if paginate and pagination is not None:
        items = client.iterate(
            Paged(endpoint, pagination, _results), limit=config.http.cap(limit, all_=all_)
        )
        return ApiResponse(list(items))
    return client.send(endpoint)


def _resolve_target(path: str, service_name: str | None) -> tuple[Service, str]:
    """The service a call goes to and its path under that service's base URL.

    A full URL must be a registered service's own origin and live under its base URL, so the
    token never goes to another host; ``service_name`` is needed only for a relative path.

    Args:
        path: A relative path, or a full URL of a registered service.
        service_name: The service a relative path belongs to; optional for a full URL, where it
            must name the URL's own service.

    Returns:
        The service and the path under its base URL.

    Raises:
        typer.BadParameter: ``service_name`` is unknown, missing for a relative path or names
            another service than the URL's, or the URL is not under a registered service.

    Examples:
        >>> wiki = next(s for s in SERVICES if s.name == "wiki")
        >>> service, relative = _resolve_target(f"{wiki.profile.base_url}/pages?slug=a", None)
        >>> service.name, relative
        ('wiki', 'pages?slug=a')
    """
    if service_name is not None and service_name not in {s.name for s in SERVICES}:
        raise typer.BadParameter(
            f"unknown service {service_name!r}; expected one of {_SERVICE_NAMES}",
            param_hint="--service",
        )
    parts = urlsplit(path)
    if not (parts.netloc or parts.scheme in {"http", "https"}):
        if service_name is None:
            raise typer.BadParameter(
                f"a relative PATH needs --service ({_SERVICE_NAMES}).", param_hint="--service"
            )
        return next(s for s in SERVICES if s.name == service_name), _inside(path.lstrip("/"))
    owner = next((s for s in SERVICES if _origin(s.profile.base_url) == _origin(path)), None)
    if owner is None:
        raise typer.BadParameter(
            f"refusing to send credentials to {parts.netloc or path!r}: "
            f"ycli api reaches only {', '.join(_origin(s.profile.base_url)[1] for s in SERVICES)}."
        )
    if service_name not in {None, owner.name}:
        raise typer.BadParameter(
            f"--service {service_name} contradicts the URL, which is a {owner.name} URL."
        )
    prefix = urlsplit(owner.profile.base_url).path.rstrip("/") + "/"
    if not parts.path.startswith(prefix):
        raise typer.BadParameter(f"{path!r} is not under {owner.profile.base_url}.")
    query = f"?{parts.query}" if parts.query else ""
    return owner, _inside(parts.path.removeprefix(prefix)) + query


def _inside(relative: str) -> str:
    """``relative`` if it stays under the base URL; httpx would resolve ``..`` out of it."""
    try:
        check_path(relative.partition("?")[0])
    except YandexClientError as exc:
        raise typer.BadParameter(str(exc)) from exc
    return relative


def _origin(url: str) -> tuple[str, str]:
    parts = urlsplit(url)
    return parts.scheme, parts.netloc.lower()


def _check_paginate(service: Service, pagination: object, verb: str) -> None:
    if verb != "GET":
        raise typer.BadParameter("--paginate works with GET only.", param_hint="--paginate")
    if pagination is None:
        raise typer.BadParameter(
            f"{service.name} listings do not share one pagination scheme (--paginate works for "
            f"{_PAGINATED_NAMES}); pass the paging parameters with -f, e.g. -f page=2.",
            param_hint="--paginate",
        )


def _read_input(source: str | None) -> bytes | None:
    if source is None:
        return None
    if source == "-":
        return sys.stdin.buffer.read()
    try:
        return Path(source).read_bytes()
    except OSError as exc:
        raise typer.BadParameter(
            f"cannot read {source!r}: {exc.strerror}", param_hint="--input"
        ) from exc


def _headers(items: Sequence[str] | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in items or []:
        name, sep, value = item.partition(":")
        if not sep or not name.strip():
            raise typer.BadParameter(
                f"a header must be 'Name: value', got {item!r}", param_hint="--header"
            )
        headers[name.strip()] = value.strip()
    return headers


def _query(fields: Mapping[str, Any]) -> dict[str, Any]:
    """Fields as query parameters; a nested object becomes bracketed keys.

    Args:
        fields: The request fields; a nested object is allowed.

    Returns:
        The query parameters, with a nested object as bracketed keys.

    Examples:
        >>> _query({"a": {"b": 1}, "t": [1, 2], "q": "x"})
        {'a[b]': 1, 't': [1, 2], 'q': 'x'}
    """
    flat: dict[str, Any] = {}
    for key, value in fields.items():
        if isinstance(value, dict):
            flat |= _query({f"{key}[{inner}]": nested for inner, nested in value.items()})
        else:
            flat[key] = value
    return flat


def _decode(response: httpx2.Response) -> ApiResponse | str | BinaryResult | None:
    """What a response prints as: JSON through the output path, text as text, the rest as bytes."""
    if not response.content:
        return None
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        with contextlib.suppress(ValueError):  # declared JSON that is not: print it as text
            return ApiResponse(response.json())
    if "json" in content_type or content_type.startswith("text/"):
        return response.text
    return BinaryResult(response.content)


def _results(page: object) -> Sequence[object]:
    """The items of one page: a Tracker listing's array, or a Wiki listing's ``results``."""
    root = page.root if isinstance(page, ApiResponse) else None
    if isinstance(root, list):
        return root
    if isinstance(root, dict) and isinstance(root.get("results"), list):
        return root["results"]
    raise typer.BadParameter(
        'this endpoint did not answer with a listing ([...] or {"results": [...]}).',
        param_hint="--paginate",
    )
