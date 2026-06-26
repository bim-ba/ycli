# YFM Content Authoring — Quick Reference — Wiki API

← Back to [docs.md](../docs.md)

Content is stored as YFM (Yandex Flavored Markdown). Rules for agent-generated content:

- **Use `# Title` as the first line** only when the page title differs from the H1 you want rendered
- **Note blocks** — `{% note info/warning/alert/tip "Title" %} ... {% endnote %}`
- **Cuts** — `{% cut "Label" %} ... {% endcut %}` for content > 20 lines or supplementary detail
- **Tabs** — `{% list tabs %}\n- Tab\n    Content\n{% endlist %}` for alternative paths only
- **Tables** — standard markdown for simple data; `#| || ... || |#` for multi-line cells
- **Code** — always specify language: `` ```sql ``, `` ```python ``, `` ```bash ``
- **Mermaid diagrams** — `` ```mermaid `` block, use `flowchart LR` for data flows
- **Grids** — `{% wgrid id="uuid" %}` — requires an existing grid created via API

Full YFM reference: `../../05-edit-page/`
