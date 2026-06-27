#!/usr/bin/env bash
# Deterministic ycli demo. Real --help output; baked sample data (no network, no creds).
set -euo pipefail

ps1() { printf '\033[38;5;203m❯\033[0m %s\n' "$1"; }

ps1 "ycli --help"
uv run ycli --help

ps1 "ycli tracker issues get TRACKER-1"
cat <<'OUT'
TRACKER-1  ·  Set up project scaffolding
status:    In Progress      assignee: alice
priority:  Normal           updated:  2026-06-20
OUT

ps1 "ycli wiki pages get onboarding"
cat <<'OUT'
onboarding  ·  Team Onboarding Guide
author: bob   revision: 7   children: 4
OUT

ps1 "ycli-mcp   # read-only MCP server: wiki_*, tracker_*, forms_* tools"
cat <<'OUT'
Starting MCP server on stdio …
Tools: wiki_pages_get, wiki_pages_descendants, tracker_issues_get,
       tracker_issues_list, tracker_issues_search, forms_surveys_list, forms_answers_list
OUT
