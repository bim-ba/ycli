=== "CLI"

    ```bash
    ycli wiki pages get-meta team/roadmap
    ```

=== "MCP"

    ```json
    {
      "name": "wiki_pages_get_meta",
      "arguments": {
        "slug": "team/roadmap"
      }
    }
    ```

=== "SDK"

    ```python
    wiki.pages.get("team/roadmap", fields="attributes,owner")
    ```
