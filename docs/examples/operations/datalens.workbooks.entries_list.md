=== "CLI"

    ```bash
    ycli datalens workbooks entries-list wb000000000001 --limit 45
    ```

=== "MCP"

    ```json
    {
      "name": "datalens_workbooks_entries_list",
      "arguments": {
        "workbook_id": "wb000000000001",
        "limit": 45
      }
    }
    ```

=== "SDK"

    ```python
    datalens.workbooks.entries_list("wb000000000001", limit=45)
    ```
