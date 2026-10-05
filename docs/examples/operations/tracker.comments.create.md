=== "CLI"

    ```bash
    ycli tracker comments create DE-14 --text 'Готово ✅'
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_comments_create",
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
    tracker.comments.create("DE-14", CommentCreate(text="Готово ✅"))
    ```
