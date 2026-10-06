=== "CLI"

    ```bash
    ycli datalens collections content-list col00000000001 --limit 45
    ```

=== "MCP"

    ```json
    {
      "name": "datalens_collections_content_list",
      "arguments": {
        "collection_id": "col00000000001",
        "limit": 45
      }
    }
    ```

=== "SDK"

    ```python
    datalens.collections.content_list("col00000000001", limit=45)
    ```
