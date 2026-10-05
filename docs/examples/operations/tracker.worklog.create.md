=== "CLI"

    ```bash
    ycli tracker worklog create DE-66 --duration PT2H --start 2021-03-04T10:00:00.000+0300 --comment pairing
    ```

=== "MCP"

    ```json
    {
      "name": "tracker_worklog_create",
      "arguments": {
        "issue_key": "DE-66",
        "body": {
          "duration": "PT2H",
          "start": "2021-03-04T10:00:00.000+0300",
          "comment": "pairing"
        }
      }
    }
    ```

=== "SDK"

    ```python
    tracker.worklog.create("DE-66", WorklogCreate(duration="PT2H", start="2021-03-04T10:00:00.000+0300", comment="pairing"))
    ```
