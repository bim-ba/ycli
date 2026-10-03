=== "CLI"

    ```bash
    ycli tracker transitions execute DE-52 close --field comment=done --field resolution=fixed -F storyPoints=3
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_transitions_execute",
      "arguments": {
        "key": "DE-52",
        "transition_id": "close",
        "body": {
          "comment": "done",
          "resolution": "fixed",
          "storyPoints": 3
        }
      }
    }
    ```

=== "SDK"

    ```python
    tracker.transitions.execute("DE-52", "close", {"comment": "done", "resolution": "fixed", "storyPoints": 3})
    ```
