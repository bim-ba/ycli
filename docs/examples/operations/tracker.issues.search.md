=== "CLI"

    ```bash
    ycli tracker issues list --queue DE --status open --assignee alice
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_issues_list",
      "arguments": {
        "queue": "DE",
        "status": "open",
        "assignee": "alice"
      }
    }
    ```

=== "SDK"

    ```python
    tracker.issues.search({"filter": {"queue": "DE", "status": "open", "assignee": "alice"}}, limit=500)
    ```
