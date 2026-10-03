# Resource conventions

These rules fill the gap between the structural invariants in
[`ARCHITECTURE.md`](../../ARCHITECTURE.md) (ARCH-1..8) and the per-file conventions
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

`APIModel` sets `extra="ignore"` (unknown API fields are silently dropped),
`populate_by_name=True` (a field may be set by its Python name *or* its serialization
alias) and `serialize_by_alias=True` (every dump, CLI and MCP alike, keeps the API's field
names).  Never use bare `pydantic.BaseModel` inside `ycli.yandex`.

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

---

## 2. List-model naming: `XList` is flat, `XResponse` is the envelope

| Convention | Class signature | Used as |
|---|---|---|
| Flat list | `class XList(RootModel[list[X]]): root: list[X] = []` | Public return type of `client.list()` and MCP `list_` tool |
| Envelope | `class XResponse(APIModel): links: ...; result: list[X]` | Internal parse type of `client._list_page()` |

```python
# models.py
class SurveyList(RootModel[list[Survey]]):  # flat — public
    root: list[Survey] = []


class SurveysResponse(APIModel):  # envelope — internal
    links: dict[str, Any] = Field(default_factory=dict)
    result: list[Survey] = Field(default_factory=list)
```

The envelope type (`XResponse`) is an implementation detail of the client and must not
appear in the public `client.list()` signature or in MCP tool return types.

---

## 3. MCP annotation sets / tags / `<domain>_client` come from the domain `dependencies`

Every `mcp.py` imports the annotation sets (`RO`, `WRITE`, `WRITE_IDEMPOTENT`,
`DESTRUCTIVE`), the tag constants (`TAGS`, `WRITE_TAGS`), and the domain client provider
from the domain's `dependencies` module — not from the shared `ycli.yandex.mcp`:

```python
# src/ycli/yandex/tracker/issues/mcp.py
from ycli.yandex.tracker.dependencies import (
    DESTRUCTIVE,
    RO,
    TAGS,
    WRITE,
    WRITE_TAGS,
    tracker_client,
)
```

The `dependencies` module re-exports the annotation sets (from `ycli.yandex.mcp`) in its
`__all__` and defines the domain tags (`TAGS = {"<domain>"}`,
`WRITE_TAGS = TAGS | {WRITE_TAG}`), so import-linter and IDEs resolve the canonical source
correctly.  The scaffold (`scripts/new_endpoint.py`) generates this single-line import
automatically.

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
`Depends(tracker_client)`.  This is the only approved sharing pattern — fastmcp's deprecated
`import_server` must not be used.

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
| parameters | `Annotated[T, Field(description=…)]` | **Every** input property carries a non-empty description (`tests/test_mcp_metadata.py`). Reuse the shared aliases in `<domain>/dependencies.py` (`IssueKey`, `QueueId`, `Version`, `SurveyId`, `Slug`, …) instead of repeating a description per tool; a request `body` model describes itself through its fields |
| `annotations` | `@mcp.tool(annotations={**<SET>, "title": "…"})` | `<SET>` matches the verb class exactly: `RO` for reads, `WRITE` for additive creates, `WRITE_IDEMPOTENT` for PATCH-style edits, `DESTRUCTIVE` for delete/clear/abort — plus an imperative title. Explicit because the MCP-spec default for an unannotated tool is `destructiveHint=true` |
| `tags` | `@mcp.tool(tags=…)` | `TAGS` for reads, `WRITE_TAGS` for writes — the `write` tag is what `ycli mcp start --read-only` disables wholesale |

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
    tags=TAGS,
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
    tags=WRITE_TAGS,
)
def delete(key: str, comment_id: str, client: TrackerClient = Depends(tracker_client)) -> Ack:
    """Permanently delete one comment from a Tracker issue (irreversible)."""
    client.comments.delete(key, comment_id)
    return Ack(detail=f"deleted comment {comment_id} on {key}")
```

### Typed request body — never `dict`

A write tool that sends a request body types that parameter as the resource's pydantic
request model — the **same model the CLI command builds** — never a bare `body: dict`. The
model becomes the tool's input schema, so an agent sees the field names, types, and aliases
instead of an opaque `object`, and a malformed payload fails schema validation before the
HTTP call rather than at the live API:

```python
@mcp.tool(
    name="bulk_update",
    annotations={**WRITE, "title": "Bulk-update issues"},
    tags=WRITE_TAGS,
)
def update(body: BulkUpdate, client: TrackerClient = Depends(tracker_client)) -> BulkChange:
    """Start an async bulk field update over many Tracker issues; returns the operation."""
    return client.bulk.update(body.model_dump(by_alias=True, exclude_none=True))
```

The client method itself takes a plain dict — the MCP tool converts the validated model with `.model_dump(by_alias=True, exclude_none=True)`, the same call the CLI
command already makes, so both surfaces produce byte-identical wire JSON from one model.

The only exceptions are a binary upload, which takes `Base64Bytes` (see below), and exactly one
documented allowlist entry (`ARCH8_BODY_DICT_ALLOWLIST` in `tests/test_architecture.py`) for an
endpoint whose live wire shape no existing model correctly represents — see Enforcement below.

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
`mcp.py` for `@mcp.tool`-decorated functions and fails the build on a bare `dict`/`dict[...]`
`body` parameter — fail-closed, with exactly one documented exception in
`ARCH8_BODY_DICT_ALLOWLIST` (`entities_set_permissions`: its live wire shape nests
READ/WRITE/GRANT under `grant`/`revoke` verbs, which the existing
`ExtendedPermissionsUpdate`/`AclInput` models do not represent).

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
  flat `XList` of §2). A bodyless write returns `None` and the surfaces build the `Ack`; a binary
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
- An async trigger (export, clone, bulk change) takes `--wait/--no-wait`, default `--wait`, and
  polls through `ycli.cli.progress.wait_for`; the matching `operations get` read ships on every
  surface so an agent can poll it too.

---

## 7. Where these rules are enforced

| Rule | Enforced by |
|---|---|
| `APIModel` base | code review only — no automated check (ARCH-1 verifies the files exist, not what they subclass) |
| `XList` / `XResponse` naming | code review only — model class names are not snapshotted (snapshots track command and tool signatures) |
| `dependencies` import path | `scripts/new_endpoint.py` scaffold + code review |
| MCP annotation honesty (each tool's hints against the strongest effect it sends, `write` tag) | `tests/test_contract.py`, `tests/test_architecture.py` ARCH-3 |
| Serialization confinement | `tests/test_architecture.py` ARCH-4 |
| Discriminated MCP output unions | code review + regression test (`status_get` me round-trip) |
| MCP tool description + output schema | `tests/test_architecture.py::test_every_mcp_tool_has_description_and_output_schema` |
