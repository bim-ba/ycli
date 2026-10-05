=== "CLI"

    ```bash
    ycli tracker issues get DE-7
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_issues_get",
      "arguments": {
        "issue_key": "DE-7"
      }
    }
    ```

=== "SDK"

    ```python
    tracker.issues.get("DE-7")
    ```
