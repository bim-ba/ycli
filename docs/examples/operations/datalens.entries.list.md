=== "CLI"

    ```bash
    ycli datalens entries list --scope dash --limit 45
    ```

=== "MCP"

    ```json
    {
      "name": "datalens_entries_list",
      "arguments": {
        "scope": "dash",
        "limit": 45
      }
    }
    ```

=== "SDK"

    ```python
    datalens.entries.list(scope="dash", limit=45)
    ```
