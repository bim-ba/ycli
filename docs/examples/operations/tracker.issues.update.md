=== "CLI"

    ```bash
    ycli tracker issues update DE-7 --summary Renamed --priority critical
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_issues_update",
      "arguments": {
        "key": "DE-7",
        "body": {
          "summary": "Renamed",
          "priority": {
            "key": "critical"
          }
        }
      }
    }
    ```

=== "SDK"

    ```python
    tracker.issues.update("DE-7", {"summary": "Renamed", "priority": {"key": "critical"}})
    ```
