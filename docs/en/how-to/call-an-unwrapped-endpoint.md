---
type: how-to
---

# Call an unwrapped endpoint

`ycli api PATH --service tracker|wiki|forms` calls any endpoint of a service, the way
[`gh api`](https://cli.github.com/manual/gh_api) does, with the same authentication, retries,
output and exit codes as every other command.

```bash
ycli api issues/TRACKER-1 --service tracker --jq .summary                # GET is the default
ycli api issues/TRACKER-1/comments --service tracker -F text=@note.md    # a field makes it a POST
ycli api pages/descendants --service wiki -f slug=docs --paginate        # every page, one JSON array
```

- `PATH` is relative to the service's base URL. A full URL of a service needs no `--service`;
  any other host is refused, so the token never leaves Yandex.
- `-f key=value` sends a string; `-F` is typed: `true`, `null`, numbers, JSON, `@file` for a
  file's text, `key[sub]=v` to nest and `key[]=v` for an array.
- Fields of a GET or DELETE go to the query string, otherwise to a JSON body. `--input FILE`
  sends a raw body instead.
- `-H 'Name: value'` adds a header and `-X` sets the method. `--dry-run`, `--yes` and `--jq`
  behave as everywhere.
- `--paginate` follows Tracker's `Link: rel="next"` and Wiki's `next_cursor`. Forms pages its
  listings in more than one way, so pass its paging parameters with `-f` yourself.

The full option list is in the [`ycli api` reference](../reference/cli/api.md).
