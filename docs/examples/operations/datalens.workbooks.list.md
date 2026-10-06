=== "CLI"

    ```bash
    ycli datalens workbooks list --collection-id col00000000001 --limit 45
    ```

=== "MCP"

    ```json
    {
      "name": "datalens_workbooks_list",
      "arguments": {
        "collection_id": "col00000000001",
        "limit": 45
      }
    }
    ```

=== "SDK"

    ```python
    datalens.workbooks.list(collection_id="col00000000001", limit=45)
    ```
