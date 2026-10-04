# Resource conventions

These rules fill the gap between the structural invariants in
[`ARCHITECTURE.md`](../../ARCHITECTURE.md) (ARCH-1..9) and the per-file conventions
documented in [`skills-and-commands.md`](skills-and-commands.md).  They apply to every
`yandex/<domain>/<resource>/` package, including the singleton `me` resources.

---

## 1. Every model inherits `APIModel`

All pydantic models — including sub-models and singleton `me` models — inherit from
`ycli.yandex.models.APIModel`:

```python
from ycli.yandex.models import APIModel


class MyModel(APIModel): ...
```

`APIModel` sets `extra="allow"` (a reply keeps a field the model does not declare, so what
Yandex adds shows up in the output at once, untyped), `validate_by_name=True` (a field may be
set by its Python name *or* its alias) and `serialize_by_alias=True` (every dump, CLI and MCP
alike, keeps the API's field names). A model that only request bodies are built from inherits
`RequestBody` (`extra="forbid"`): a key it does not declare is an error where the body is
built, not something sent to the API. Never use bare `pydantic.BaseModel` inside
`ycli.yandex`; a bare mapping with no fields of its own is a `RootModel[dict[...]]`.

Two lists hold what is open on purpose, each entry with its reason: `OPEN_BODIES` in
`scripts/api_drift.py` (an issue takes custom fields; the drift comparison skips only these
bodies) and `BODY_AND_REPLY` in `tests/test_conventions.py` (a model that both builds a body
and reads a reply stays open, so a key it does not declare, nested in a body, reaches the API;
its declared fields are still compared with the published ones).

### One class per shape

A shape that two or more resources of a service read (a reference with `self`, `id` and
`display`; a localized name) is one class in the service's `models.py`
(`ycli.yandex.tracker.models.Reference`), not a class per resource. Models of one kind that
differ by a few fields share a base class and add their own (`KeyedReference(Reference)`
adds `key`); models of different kinds that only happen to match stay separate. A model
used by one resource stays in that resource. `tests/test_model_shapes.py` fails when two models of a
service have the same schema, unless the group is listed in `SAME_SHAPE` with its reason.

A public model that is renamed or merged stops importing under its old name in the same
release: no alias is kept. The commit that does it carries a `BREAKING CHANGE` footer listing
"was → is", which becomes the changelog entry.

### A field with a set of values

A set of values is the known values plus any string, and the definition itself says so:

```python
SortDirection = Literal["asc", "desc"] | str
```

It is the same on the way in and on the way out, in every service: a CLI option, an MCP tool
parameter, a request-body field, a reply field. ycli does not refuse a value outside the set:
it goes to the API, which answers for it, and in a reply it does not fail the parse. An IDE
suggests the known values, and a tool's schema shows them (`anyOf` of the `enum` and a string).

- **CLI.** Typer has no "one of these or any string" type, so the option is a string built by
  `ycli.cli.typedefs.values_option(SortDirection, "--order", help="Sort direction.")`, which
  takes the values for the help text and the completion from the definition. Do not list the
  values by hand: `test_an_option_takes_the_values_it_names_from_the_definition_of_the_set`.
- **One definition per set**, used by name: a set of one resource in its `models.py`, of
  several in the service's `models.py`, of several services in `ycli.yandex.models`
  (`SortDirection`, `GroupSource`). `test_a_closed_value_set_is_defined_once` fails on a second
  `Literal` or `StrEnum` with the same values.
- **Strict on purpose** (not sets of Yandex values): a discriminator field, by which pydantic
  picks the class (`type` of a question or a subscription); `forms questions --type`, the five
  types the flags can build; the sets ycli's own code branches on (`Method`, `Effect`, the log
  level and format, `CredentialKind`); a `StrEnum` option that names a part of the address.

### A field the API ignores

A request field or parameter that the API accepts and does nothing with stays in ycli. Its
description begins with `IGNORED_BY_API` (`ycli.yandex.models`), so the CLI help, the MCP
input schema and the reference say so; its body model inherits `WarnsOnIgnored`, so setting
it logs a warning (a reply carrying the same name is read silently); `scripts/api_drift.py`
lists it in `EXPLAINED` with the `IGNORED` reason, and `tests/test_api_drift.py` fails when
one of the two is missing.

---

## 2. Lists: `ItemList[X]` is flat, `XResponse` is the envelope

| What | Type | Used as |
|---|---|---|
| Flat list | `ItemList[X]` from `ycli.yandex.models` | Public return type of `client.list()` and of the MCP `list` tool |
| Envelope | `class XResponse(APIModel): links: ...; result: list[X]` | The page the endpoint parses, read by the pager |

```python
# client.py
def list(self, *, limit: int | None = None) -> ItemList[Survey]: ...


# models.py
class SurveysResponse(APIModel):  # envelope — internal
    links: dict[str, Any] = Field(default_factory=dict)
    result: list[Survey] = Field(default_factory=list)
```

A resource does not define a list class of its own. An envelope that holds only the items and
their paging (`XResponse`, or `CursorPage[X]` for a Wiki cursor listing) is read by the pager and
flattened. An envelope that carries data of its own is the public type: Forms conditions return
`ConditionsResponse` because its `operator` joins the groups.

---

## 3. MCP annotation sets / `<domain>_client` come from the domain `dependencies`

Every `mcp.py` imports the annotation sets (`RO`, `WRITE`, `WRITE_IDEMPOTENT`,
`DESTRUCTIVE`) and the domain client provider from the domain's `dependencies` module — not
from the shared `ycli.yandex.mcp`:

```python
# src/ycli/yandex/tracker/issues/mcp.py
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    WRITE,
    tracker_client,
)
```

The `dependencies` module re-exports the annotation sets (from `ycli.yandex.mcp`) in its
`__all__`, so import-linter and IDEs resolve the canonical source correctly. It also defines
the domain tags (`TAGS`, `WRITE_TAGS`) for the prompts and resources of the service, which
have no annotations to derive them from.  The scaffold (`scripts/new_endpoint.py`) generates this single-line import, and
an import-linter contract forbids a resource `mcp.py` from importing `ycli.yandex.mcp`.

### Why `<domain>_client` is a per-request provider

fastmcp's `mount()` does not propagate lifespan context across server boundaries, so a
mounted domain server cannot receive a shared client through startup state.  Each `dependencies`
module therefore builds its provider with `client_provider` (in `ycli.yandex.mcp`):

```python
# src/ycli/yandex/tracker/dependencies.py
tracker_client = client_provider(TrackerClient)
```

The provider resolves credentials (`caller_credentials`: the environment over stdio, the signed-in
caller's Yandex token over HTTP) and builds the client
on every tool call, so a rotated token applies without a restart and nothing is cached per
process; `app_config()` is the matching per-call config provider.  MCP tools consume them via
`Depends(tracker_client)`.

---

## 4. MCP tool-metadata standard

Every MCP tool MUST satisfy the following metadata contract.  fastmcp auto-derives
`description` from the docstring and `outputSchema` from the return type annotation —
**never set either by hand**.

### Required fields

| Field | Where it lives | Requirement |
|---|---|---|
| `name` | `@mcp.tool(name=…)` | `snake_case`, `<resource>[_<subresource>]_<verb>`, usually verb last (a few keep the API's own phrase, e.g. `tracker_queues_set_permissions`); `edit`/`modify` are `update`. Prefixed with the service it is the CLI path of the same operation (`tracker_boards_update` = `ycli tracker boards update`, ARCH-1 `test_arch1_cli_path_equals_mcp_name`) |
| description | function docstring (first line) | One sentence; the LLM's primary selector — **required** |
| output schema | return type annotation | A concrete type (`ModelClass`, `list[X]`, `dict[str, Any]`) — **required**; bodyless writes return `Ack` (see below) |
| parameters | `Annotated[T, Field(description=…)]` | **Every** input property carries a non-empty description (`tests/test_mcp_metadata.py`). Reuse the shared aliases in `<domain>/dependencies.py` (`IssueKey`, `QueueID`, `Version`, `SurveyID`, `Slug`, …) instead of repeating a description per tool; a request `body` model describes itself through its fields |
| `annotations` | `@mcp.tool(annotations={**<SET>, "title": "…"})` | `<SET>` matches the verb class exactly: `RO` for reads, `WRITE` for additive creates, `WRITE_IDEMPOTENT` for PATCH-style edits, `DESTRUCTIVE` for delete/clear/abort — plus an imperative title. Explicit because the MCP-spec default for an unannotated tool is `destructiveHint=true` |
| `tags` | never passed | The root server derives them (`ycli.mcp.listing.DerivedTags`): the service from the tool's name, `write` when `readOnlyHint` is not true — the tag `ycli mcp start --read-only` disables wholesale. A tool that passes `tags=` fails `test_arch3_no_tool_states_its_tags_itself` |

### Prohibited

- `description=` kwarg in `@mcp.tool(…)` — set the docstring instead
- `output_schema=` kwarg in `@mcp.tool(…)` — set the return annotation instead
- `meta`, `icons`, `version`, top-level `title=` — omit by default
- examples in a tool docstring: it is the tool's description, so it carries none
  (`test_no_tool_docstring_carries_an_example`); the SDK method it calls has the example. A request
  model's examples reach the input schema, and the listing strips them (`ycli.mcp.listing`)

### Read example

```python
@mcp.tool(
    name="issues_get",
    annotations={**RO, "title": "Get Tracker issue"},
)
def get(key: IssueKey, client: TrackerClient = Depends(tracker_client)) -> Issue:
    """A single Tracker issue by key."""  # ← this IS the description
    return client.issues.get(key)  # return type IS the outputSchema
```

### Write example

```python
@mcp.tool(
    name="comments_delete",
    annotations={**DESTRUCTIVE, "title": "Delete Tracker issue comment"},
)
def delete(key: str, comment_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete one comment from a Tracker issue (irreversible)."""
    client.comments.delete(key, comment_id)
    return Ack(detail=f"deleted comment {comment_id} on {key}")
```

### Typed request body — never `dict`

A request body is the resource's pydantic request model in every layer: the MCP tool takes
it as its `body` parameter, the CLI command builds it from its options, the client method and
the endpoint builder take it as it is, and `Endpoint` dumps it once (`Endpoint.body`: API field
names, unset fields left out). The dump is pydantic's own: `APIModel` carries one wrap
serializer that, for a request body (`model_dump(context=WIRE)`), leaves out an optional field
that is `None`, keeps a required field that is `None`, and keeps a key the model does not
declare as it was given. The serializer has no return annotation on purpose: with one, pydantic
replaces the model's schema with that type and every MCP output schema loses its fields
(`tests/snapshots/mcp_output_schemas.txt` would change). A model may carry pydantic
serializers of its own. Nothing in between dumps it, so the three surfaces
send the same JSON. In an MCP tool the model is the input schema: an agent sees the field
names, types and aliases instead of an opaque `object`, and a malformed payload fails before
the HTTP call:

```python
@mcp.tool(
    name="bulk_update",
    annotations={**WRITE, "title": "Bulk-update issues"},
)
def update(body: BulkUpdate, client: TrackerClient = Depends(tracker_client)) -> BulkChange:
    """Start an async bulk field update over many Tracker issues; returns the operation."""
    return client.bulk.update(body)
```

A `None` is an absence and is not sent, except where the caller could only have meant it: in a
field with no default, and in a field the model does not declare (an open body: Tracker clears
a field given as `null`). A command that merges `--field` values into its body dumps the named
options, merges, and validates the result into the model.

The only exception is a binary upload, which takes `Base64Bytes` (see below);
`ARCH8_BODY_DICT_ALLOWLIST` in `tests/test_architecture.py` is where another would be listed,
and it is empty.

### `Ack` for bodyless write responses

MCP tools must expose an output schema and a CLI command's return value is what gets printed —
a bare `None` return satisfies neither.  Writes whose API response carries no body (deletes,
clears, aborts) therefore surface a typed `ycli.yandex.models.Ack`
(`{ok: bool, detail: str}`): the MCP tool (and CLI command) constructs the `Ack` around the
bodyless client call, as in the example above.

### Binary payloads stay CLI/SDK-only

Raw-bytes **downloads** (attachments, exports, keyset files) never become MCP tools —
the matching *list* read does.  Upload endpoints may ship as MCP tools only in base64
form (pydantic `Base64Bytes` input — see `wiki_attachments_upload` and the
`wiki_uploadsessions_*` pipeline); raw file-path or multipart inputs stay on the CLI/SDK.

### Enforcement

`tests/test_architecture.py::test_arch8_mcp_write_tool_bodies_are_typed` AST-walks every
`mcp.py`, `client.py` and `endpoints.py` and fails the build on a bare `dict`/`dict[...]`
`body` parameter; `test_arch8_a_request_body_is_dumped_only_by_the_endpoint` fails on a
`.model_dump(` in any of the three. Both are fail-closed, with no exception today.

`tests/test_architecture.py::test_every_mcp_tool_has_description_and_output_schema`
asserts that every registered tool has a non-empty `description` and a non-`None`
`outputSchema`.  The test uses `fastmcp.Client` to list tools from the mounted root
server and checks the `tool.description` and `tool.output_schema` attributes (MCP spec
field `outputSchema`; the MCP SDK v2 types under fastmcp 4 spell it in snake_case).

---

## 5. Heterogeneous MCP output unions must be discriminated

fastmcp rebuilds `result.data` from the tool's output JSON schema and, for an undiscriminated
`anyOf`, picks the *first* branch that validates — silently reshaping one member into another
and dropping fields.  Any union a tool returns must carry a `Literal` discriminator tag via
`Field(discriminator=…)`, the way the Forms question union (`forms/questions/models.py`) does:

```python
class StringQuestion(_QuestionBase):
    type: Literal["string"] = Field(default="string", description="Discriminator: string.")
# … BooleanQuestion, IntegerQuestion, … one member per question type …
QuestionCreate = Annotated[
    StringQuestion | BooleanQuestion | IntegerQuestion | ..., Field(discriminator="type")
]
```

The CLI/SDK path carries the native model instance and is unaffected; only the MCP
`result.data` reconstruction depends on the schema being self-describing.

---

## 6. Writing a client and its CLI commands

`/new-endpoint` (`scripts/new_endpoint.py`) generates a new resource on the httpx2 core;
`tracker/issues/` and the Forms resources are worked examples.

**`endpoints.py`** — sans-IO declarations: one function per operation returning an `Endpoint`
(or a `Paged` listing with its core `Pagination`); every caller-supplied path part goes through
`segment()`; `effect=` only where the method misleads, listed in `ARCH3_EFFECT_OVERRIDES`.

**`client.py`** — HTTP only (ARCH-2):

- Subclass `ycli.yandex.core.resource.Resource`; each public method sends one declaration
  (`self._session.send(…)`, or `self._session.iterate(…, limit=…)` for a listing, returning the
  flat `ItemList[X]` of §2). A bodyless write returns `None` and the surfaces build the `Ack`; a binary
  download declares `response_type=bytes` and returns `bytes`.
- Every public method's docstring names its `METHOD /path`, has Google-style `Args:`,
  `Returns:` and `Raises:` sections that match the signature (ruff `D`, `pydoclint`), and an
  example that runs: `>>> tracker.boards.get(31).name` with the arguments of the operation's first
  contract case, whose reply answers it (the repository-root `conftest.py` puts the `tracker`,
  `wiki` and `forms` clients into every doctest). `+SKIP` only where an example needs a real file
  or the network.

**`models.py`** — `from __future__ import annotations`; inherit `APIModel` (§1); every field
carries `Field(description=…)`, which becomes the MCP schema text. Request bodies are typed
models (`XCreate` / `XUpdate`), discriminated where the API is polymorphic.

**What ycli checks.** Only what it needs to build the request: the names and types of a
body's fields, a required field, the syntax of its own options (JSON, `key=value`), the file
an option names, and limits of its own (`--limit`). Everything else is the API's to check: a
value's length or range, a value outside a known set, which arguments go together, a rule of
the service. ycli sends it as given and shows the API's answer; it does not fill in a value
the caller left out to make a request pass. ARCH-9 keeps a list of the refusals that remain,
each with its reason. A missing field of a request model is printed by one formatter
(`ycli.cli.errors.format_cli_error`, exit code 2: nothing was sent), so a command needs no
check of its own to say it. A reply that does not fit its model is another error,
`YandexUnexpectedReplyError`: the request went out, and the exit code is 1.

**`cli.py`**:

- `from __future__ import annotations`; `app = typer.Typer(name=…, help=…, no_args_is_help=True)`;
  `--help` works without credentials because a client is built only when a command runs.
- A command declares the clients it needs as keyword-only parameters
  (`*, tracker: TrackerClient`, or `config: AppConfig`); `ycli.cli.inject` fills them and hides
  them from Typer. It **returns** its result, annotated with the real type, and never prints
  (ARCH-4): a model renders through `--format`, a count returns `int`, raw text returns `str`, a
  binary download returns `BinaryResult(data, output)` behind `--output`.
- Every argument and option is `Annotated[…, typer.Argument(help=…)]` /
  `Annotated[…, typer.Option(help=…)]`. A write builds the typed request model from the options.
- A local file is a `Path` with `exists=True, dir_okay=False, readable=True`, so a missing file
  is a usage error, not a traceback; a JSON body file goes through `Model.model_validate_json`
  (`tests/test_cli_files.py` lists every such command).
- An option that is not given is `None` (`Annotated[str | None, typer.Option(…)] = None`), never
  `""` or `0`: an explicit empty string or zero is a value and is sent, so `--description ""`
  clears a field. A test asks `is not None`, not truthiness. An MCP tool parameter follows the
  same rule (`Annotated[str | None, Field(…)] = None`; `limit` is `int | None` with `ge=1`).
  `tests/test_not_given.py` fails on a `""` or `0` default in a `cli.py` or an `mcp.py`.
- An async trigger (export, clone, bulk change) takes `--wait/--no-wait`, default `--wait`, and
  polls through `ycli.cli.progress.wait_for`; the matching `operations get` read ships on every
  surface so an agent can poll it too.

---

## 7. Names

- **An acronym keeps its capitals inside a CapWords name** (PEP 8): `QueueID`, `HTTPSubscription`,
  `JSONRPCSubscription`, `SurveyAPIKey`, `ACL`; a plural adds a lower-case `s` (`UserIDs`). The
  list is `ACRONYMS` in `tests/test_conventions.py`. A name that has a spelling of its own keeps
  it and is recorded with its reason in `OWN_SPELLINGS` (`OAuth`). A snake_case name is all
  lower case as before (`queue_id`, `api_key`).
- **An `Annotated` alias is defined once.** The same text in two modules is one alias: it moves
  to the nearest shared module (`<domain>/typedefs.py` for CLI options and arguments,
  `<domain>/dependencies.py` for MCP parameters, `ycli/cli/typedefs.py` across domains) and is
  imported by name. Two aliases that share a name but differ in help, type or requiredness are
  different things and stay apart.

---

## 8. Where these rules are enforced

| Rule | Enforced by |
|---|---|
| `APIModel` base | `tests/test_conventions.py::test_every_model_inherits_apimodel` (exceptions in `MODEL_BASE_EXCEPTIONS`) |
| No list class of a resource's own | `tests/test_conventions.py::test_no_resource_defines_a_list_class_of_its_own` |
| `dependencies` import path | import-linter contract `conventions: a resource mcp.py imports from its domain dependencies` (`uv run lint-imports`) |
| MCP annotation honesty (each tool's hints against the strongest effect it sends, `write` tag) | `tests/test_contract.py`, `tests/test_architecture.py` ARCH-3 |
| Serialization confinement | `tests/test_architecture.py` ARCH-4 |
| Discriminated MCP output unions | `tests/test_conventions.py::test_every_union_a_tool_returns_is_discriminated` |
| MCP tool description + output schema | `tests/test_architecture.py::test_every_mcp_tool_has_description_and_output_schema` |
| Acronyms keep their capitals in a CapWords name | `tests/test_conventions.py::test_an_acronym_keeps_its_capitals_in_a_name` |
| An `Annotated` alias is defined once | `tests/test_conventions.py::test_an_annotated_alias_is_defined_once` |
