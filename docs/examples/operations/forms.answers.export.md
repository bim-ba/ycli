=== "CLI"

    ```bash
    ycli forms answers export 686d0a1b2c3d4e5f00000030 --format csv --upload disk --started-at 2026-01-01T00:00:00 --finished-at 2026-02-01T00:00:00 --pk 11 --pk 12 --column answer_short_text_1 --limit 30 --upload-files --no-wait
    ```

=== "MCP"

    ```json
    {
      "name": "forms_answers_export",
      "arguments": {
        "survey_id": "686d0a1b2c3d4e5f00000030",
        "body": {
          "format": "csv",
          "upload": "disk",
          "started_at": "2026-01-01T00:00:00",
          "finished_at": "2026-02-01T00:00:00",
          "pks": [
            11,
            12
          ],
          "columns": [
            "answer_short_text_1"
          ],
          "limit": 30,
          "upload_files": true
        }
      }
    }
    ```

=== "SDK"

    ```python
    forms.answers.export("686d0a1b2c3d4e5f00000030", AnswerExport(format="csv", upload="disk", started_at="2026-01-01T00:00:00", finished_at="2026-02-01T00:00:00", pks=[11, 12], columns=["answer_short_text_1"], limit=30, upload_files=True))
    ```
