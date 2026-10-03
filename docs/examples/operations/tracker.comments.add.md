=== "CLI"

    ```bash
    ycli tracker comments add DE-14 --text 'Готово ✅'
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_comments_add",
      "arguments": {
        "key": "DE-14",
        "body": {
          "text": "Готово ✅"
        }
      }
    }
    ```

=== "SDK"

    ```python
    tracker.comments.add("DE-14", CommentCreate(text="Готово ✅"))
    ```
