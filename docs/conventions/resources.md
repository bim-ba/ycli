# Resource conventions

These rules fill the gap between the structural invariants in
[`ARCHITECTURE.md`](../../ARCHITECTURE.md) (ARCH-1..10) and the per-file conventions
documented in [`skills-and-commands.md`](skills-and-commands.md).  They apply to every
`yandex/<domain>/<resource>/` package, including the singleton `me` resources.

---

## 1. Every model inherits `APIModel`

All pydantic models — including sub-models and singleton `me` models — inherit from
`ycli.yandex.models.APIModel`:

```python
from ycli.yandex.models import APIModel

class MyModel(APIModel):
    ...
```

`APIModel` sets `extra="ignore"` (unknown API fields are silently dropped) and
`populate_by_name=True` (a field may be set by its Python name *or* its serialization
alias).  Never use bare `pydantic.BaseModel` inside `ycli.yandex`.

---

## 2. List-model naming: `XList` is flat, `XResponse` is the envelope

| Convention | Class signature | Used as |
|---|---|---|
| Flat list | `class XList(RootModel[list[X]]): root: list[X] = []` | Public return type of `client.list()` and MCP `list_` tool |
| Envelope | `class XResponse(APIModel): links: ...; result: list[X]` | Internal parse type of `client._list_page()` |

```python
# models.py
class SurveyList(RootModel[list[Survey]]):          # flat — public
    root: list[Survey] = []

class SurveysResponse(APIModel):                    # envelope — internal
    links: dict[str, Any] = Field(default_factory=dict)
    result: list[Survey] = Field(default_factory=list)
```

The envelope type (`XResponse`) is an implementation detail of the client and must not
appear in the public `client.list()` signature or in MCP tool return types.

---

## 3. MCP `RO` / `TAGS` / `<domain>_client` come from the domain `_deps`

Every `mcp.py` imports `RO`, `TAGS`, and the domain client provider from the domain's
`_deps` module — not from the shared `ycli.yandex._mcp`:

```python
# src/ycli/yandex/tracker/issues/mcp.py
from ycli.yandex.tracker._deps import RO, TAGS, tracker_client
```

The `_deps` module re-exports `RO` (from `ycli.yandex._mcp`) in its `__all__`, so
import-linter and IDEs resolve the canonical source correctly.  The scaffold
(`scripts/new_endpoint.py`) generates this single-line import automatically.

---

## 4. Raw / full unpruned accessor (`_raw` / `full` MCP tool)

When a resource's pruned model omits fields that callers might need, offer a companion
accessor that returns the raw `dict[str, Any]`:

```python
# client.py
@uplink.returns.json()
@uplink.get("issues/{key}")
def get_raw(self, key: uplink.Path) -> dict:  # ty: ignore[empty-body]
    """GET one issue — raw dict, all fields."""
```

```python
# mcp.py  — exposed as a separate tool with the _full verb
@mcp.tool(name="issues_full", annotations={**RO, "title": "Get full Tracker issue (raw)"}, tags=TAGS)
def full(key: str, client: TrackerClient = Depends(tracker_client)) -> dict[str, Any]:
    """A single Tracker issue as a raw dict (all fields)."""
    return client.issues.get_raw(key)
```

Wrap the dict in `RawMapping` before passing it to `Serializer.serialize` in `cli.py`
(ARCH-4).  Only add the raw accessor when the pruned model is intentionally incomplete
and users are known to need the omitted fields.

---

## 5. Where these rules are enforced

| Rule | Enforced by |
|---|---|
| `APIModel` base | code review only — no automated check (ARCH-1 verifies the files exist, not what they subclass) |
| `XList` / `XResponse` naming | code review only — model class names are not snapshotted (snapshots track command/tool names) |
| `_deps` import path | `scripts/new_endpoint.py` scaffold + code review |
| Read-only MCP | `tests/test_architecture.py` ARCH-3 |
| Serialization confinement | `tests/test_architecture.py` ARCH-4 |

---

*For MCP tool metadata standards (title format, tag taxonomy, annotation fields), see
Task E4 (forthcoming).*
