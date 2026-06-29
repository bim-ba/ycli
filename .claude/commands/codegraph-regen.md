---
description: Build or refresh the local graphify code graph of src/ (AST + semantic communities). Output is gitignored.
---

`graphify` (installed via `uv tool install graphifyy`) builds a queryable AST + semantic
graph of the codebase. The graph is a **local navigation index** — it is gitignored
(`/graphify-out/`, `/.graphify/`), never committed, and rebuilt on demand.

## One-time setup

Install the graphify skill into this platform (writes to `~/.claude`, not the repo):

```bash
graphify install --platform claude
```

For the semantic community-naming pass, export an OpenRouter key (the naming backend
uses an LLM — **GLM-5.2** is the chosen model; verify current availability/pricing on
OpenRouter before a large run):

```bash
export OPENROUTER_API_KEY=...   # never commit this
```

## Build / refresh

- Full build (AST extraction + clustering + LLM community naming) — run the `/graphify`
  skill over `src/` (it orchestrates extraction → Leiden clustering → naming → `graph.json`
  + `GRAPH_REPORT.md` + `graph.html` under `graphify-out/`).
- AST-only refresh after code changes (no LLM, fast):

  ```bash
  graphify update src
  ```

- Re-cluster / re-name an existing graph (LLM naming only):

  ```bash
  graphify cluster-only . --backend=<openrouter-backend>   # --no-label to skip LLM naming
  ```

## Query

```bash
graphify path "A" "B"     # shortest path between two nodes
graphify explain "X"      # plain-language explanation of a node + neighbors
```

(Default graph location: `graphify-out/graph.json`; pass `--graph <path>` to override.)

## Notes

- Re-evaluate adopting a heavier committed graph only if the repo outgrows ripgrep +
  `ARCHITECTURE.md` navigation (roughly ~3× the current ~3.6k LOC).
- The semantic pass is nondeterministic — that is why the artifact stays gitignored rather
  than committed (it would fight the reproducible-artifact rule and the 100% coverage gate).
