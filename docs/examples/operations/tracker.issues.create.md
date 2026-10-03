=== "CLI"

    ```bash
    ycli tracker issues create --queue DE --summary New --type bug --tag ui
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_issues_create",
      "arguments": {
        "body": {
          "queue": "DE",
          "summary": "New",
          "type": {
            "key": "bug"
          },
          "tags": [
            "ui"
          ]
        }
      }
    }
    ```

=== "SDK"

    ```python
    tracker.issues.create(IssueCreate(queue="DE", summary="New", type={"key": "bug"}, tags=["ui"]))
    ```
