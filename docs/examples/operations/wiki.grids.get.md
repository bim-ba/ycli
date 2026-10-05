=== "CLI"

    ```bash
    ycli wiki grids get 0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01 --fields attributes,user_permissions --row-filter '[owner] ~ vera' --only-cols name,owner --only-rows r1,r2 --revision 9 --sort -name
    ```

=== "MCP"

    ```json
    {
      "name": "wiki_grids_get",
      "arguments": {
        "grid_id": "0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01",
        "fields": "attributes,user_permissions",
        "row_filter": "[owner] ~ vera",
        "only_cols": "name,owner",
        "only_rows": "r1,r2",
        "revision": "9",
        "sort": "-name"
      }
    }
    ```

=== "SDK"

    ```python
    wiki.grids.get("0b5e6f7a-1c2d-4e3f-8a9b-0c1d2e3f4a01", fields="attributes,user_permissions", row_filter="[owner] ~ vera", only_cols="name,owner", only_rows="r1,r2", revision="9", sort="-name")
    ```
