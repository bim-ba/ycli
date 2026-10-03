=== "CLI"

    ```bash
    ycli wiki pages create --slug eng/new --title 'New page' --content '# New'
    ```

=== "MCP"

    ```json
    {
      "name": "wiki_pages_create",
      "arguments": {
        "slug": "eng/new",
        "title": "New page",
        "content": "# New"
      }
    }
    ```

=== "SDK"

    ```python
    wiki.pages.create(PageCreate(slug="eng/new", title="New page", content="# New"))
    ```
