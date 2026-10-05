=== "CLI"

    ```bash
    ycli tracker transitions list DE-51
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_transitions_list",
      "arguments": {
        "issue_key": "DE-51"
      }
    }
    ```

=== "SDK"

    ```python
    tracker.transitions.list("DE-51")
    ```
