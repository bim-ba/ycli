"""ARCH-9 — The API answers for its own rules (see ARCHITECTURE.md)."""

from __future__ import annotations

import ast

from tests.architecture.scanners import DOMAINS, SRC, YANDEX

# ARCH-9: every place where a service's code refuses a request before it is sent, with the
# reason the request cannot be built without the check, or the limit of ycli's own it guards.
ARCH9_REFUSALS: dict[str, str] = {
    "yandex/forms/files/cli.py:verify: raises typer.BadParameter": (
        "--url values pair with --path values by position; unequal counts give no pairs"
    ),
    "yandex/tracker/entities/cli.py:checklists_update: raises typer.BadParameter": (
        "--item is ycli's own id=text syntax; without the = there is no id to send"
    ),
    "yandex/tracker/filters/cli.py:_parse_filter: raises typer.BadParameter": (
        "--filter is JSON; text that does not parse gives no value for the body"
    ),
    "yandex/tracker/gaps/cli.py:create: raises typer.BadParameter": (
        "--gap is JSON; text that does not parse gives no absence to send"
    ),
    "yandex/tracker/workflows/cli.py:_json: raises typer.BadParameter": (
        "an option that takes JSON; text that does not parse gives no value for the body"
    ),
    "yandex/tracker/issues/client.py:search: raises YandexInvalidRequestError": (
        "limit is ycli's own cap on the issues it fetches, not a field of the API"
    ),
}
_ARCH9_RAISES = {"typer.BadParameter", "YandexInvalidRequestError", "ValueError", "TypeError"}
_ARCH9_VALIDATORS = {"model_validator", "field_validator"}
_ARCH9_WRAPPERS = {"AfterValidator", "BeforeValidator", "PlainValidator", "WrapValidator"}
_ARCH9_CONSTRAINTS = {
    "min_length",
    "max_length",
    "ge",
    "le",
    "gt",
    "lt",
    "pattern",
    "multiple_of",
    "min",
    "max",
}


def _refusals(path: str, source: str) -> list[str]:
    """Where ``source`` refuses or constrains a request: raises, validators, field limits.

    A ``ge`` on a ``limit`` that goes into ``HTTPConfig.cap`` is ycli's own item cap and is
    not reported; a ``limit`` sent to the API is.
    """
    found: set[str] = set()
    own_cap: set[int] = set()

    def visit(node: ast.AST, owner: str) -> None:
        if isinstance(node, ast.FunctionDef):
            decorators = {ast.unparse(item).split("(")[0] for item in node.decorator_list}
            if decorators & _ARCH9_VALIDATORS:
                found.add(f"{path}:{owner}.{node.name}: validator")
            if "cap(limit" in ast.unparse(node):
                for argument in [*node.args.args, *node.args.kwonlyargs]:
                    if argument.arg == "limit" and argument.annotation is not None:
                        own_cap.update(id(item) for item in ast.walk(argument.annotation))
        if isinstance(node, ast.FunctionDef | ast.ClassDef):
            owner = node.name
        if isinstance(node, ast.Raise) and node.exc is not None:
            raised = ast.unparse(node.exc).split("(")[0]
            if raised in _ARCH9_RAISES:
                found.add(f"{path}:{owner}: raises {raised}")
        if isinstance(node, ast.Call):
            called = ast.unparse(node.func)
            if called in _ARCH9_WRAPPERS:
                found.add(f"{path}:{owner}: {called}")
            if called in {"Field", "typer.Option", "typer.Argument"} and id(node) not in own_cap:
                found.update(
                    f"{path}:{owner}: {keyword.arg}"
                    for keyword in node.keywords
                    if keyword.arg in _ARCH9_CONSTRAINTS
                )
        for child in ast.iter_child_nodes(node):
            visit(child, owner)

    visit(ast.parse(source), "<module>")
    return sorted(found)


def test_arch9_a_request_is_refused_only_where_it_cannot_be_built():
    """ARCH-9: a service's code refuses before sending only what is listed with its reason.

    Everything the API can check itself (a value's length or range, which arguments go
    together, a rule of the service) is sent as given, and the API's answer is shown.
    """
    found = [
        finding
        for domain in DOMAINS
        for path in sorted((YANDEX / domain).rglob("*.py"))
        for finding in _refusals(str(path.relative_to(SRC)), path.read_text(encoding="utf-8"))
    ]
    assert sorted(found) == sorted(ARCH9_REFUSALS)


def test_arch9_refusal_check_bites():
    """Prove-it: a raise, a validator, a field limit and an option limit are each reported."""
    source = (
        "class Body(RequestBody):\n"
        "    title: str = Field(max_length=255)\n"
        "    name: Annotated[str, AfterValidator(_checked)]\n"
        "    @model_validator(mode='after')\n"
        "    def _both(self): ...\n"
        "def create(\n"
        "    page: Annotated[int, typer.Option(min=1, max=500)] = 1,\n"
        "    limit: Annotated[int | None, Field(ge=1)] = None,\n"
        "):\n"
        "    if page > 3:\n"
        "        raise typer.BadParameter('too far')\n"
        "    cap = config.http.cap(limit)\n"
        "def log(limit: Annotated[int | None, Field(ge=1)] = None):\n"
        "    return client.log(limit=limit)\n"
    )
    assert _refusals("a/cli.py", source) == [
        "a/cli.py:Body._both: validator",
        "a/cli.py:Body: AfterValidator",
        "a/cli.py:Body: max_length",
        "a/cli.py:create: max",
        "a/cli.py:create: min",
        "a/cli.py:create: raises typer.BadParameter",
        "a/cli.py:log: ge",
    ]
