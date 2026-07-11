#!/usr/bin/env bash
# Reproducible graphify rebuild for ycli — deep semantic graph over code + repo docs
# + the 5 shipped Yandex-360 API-doc domains. Uses GLM-5.2 via OpenRouter (openai-compatible
# backend), pinned to the cheapest provider with the `:floor` price shortcut.
#
# Prereqs: OPENROUTER_API_KEY in .env; the RU docs present locally (scripts/fetch_docs.py).
# Cost: ~$3-6 (GLM-5.2 is a reasoning model; output incl. reasoning tokens). Code = free AST.
set -euo pipefail
cd "$(dirname "$0")/.."
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_API_KEY="$(grep -m1 '^OPENROUTER_API_KEY=' .env | cut -d= -f2- | tr -d '"'\''')"

# references/yandex-360/* is git-ignored (yandex.ru is not open-licensed); re-include the 5
# shipped domains via `!` negation. yandex-cloud submodule (90k files) + .superpowers stay out.
graphify extract . --backend openai --model z-ai/glm-5.2:floor --mode deep \
  --exclude 'references/yandex-cloud/' \
  --exclude '.superpowers/' \
  --exclude 'graphify-out/' \
  --exclude '!references/yandex-360/tracker/' \
  --exclude '!references/yandex-360/wiki/' \
  --exclude '!references/yandex-360/forms/' \
  --exclude '!references/yandex-360/api360/' \
  --exclude '!references/yandex-360/id/'

graphify label . --backend openai --model z-ai/glm-5.2:floor   # name communities

# Derived navigation surfaces — free, deterministic, git-ignored (regenerate on demand,
# never commit). These read graph.json + labels only — no LLM, no API cost:
graphify export wiki                # -> graphify-out/wiki/ (index.md + one article per community)
graphify tree --label ycli          # -> graphify-out/GRAPH_TREE.html (D3 collapsible tree)
graphify export callflow-html       # -> graphify-out/ycli-callflow.html (Mermaid architecture)
