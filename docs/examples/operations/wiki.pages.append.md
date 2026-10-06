=== "CLI"

    ```bash
    ycli wiki pages append 4601 --content '## Top note' --location top
    ```

=== "MCP"

    ```json
    {
      "name": "wiki_pages_append",
      "arguments": {
        "page_id": 4601,
        "body": {
          "content": "## Top note",
          "body": {
            "location": "top"
          }
        }
      }
    }
    ```

=== "SDK"

    ```python
    wiki.pages.append(4601, PageAppendContent(content="## Top note", body=PageAppendContentBody(location="top")))
    ```
