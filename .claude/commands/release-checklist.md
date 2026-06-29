---
description: Post-release checklist — run after a merge to main triggers python-semantic-release.
---

Every push to `main` runs python-semantic-release (PSR), which versions from Conventional
Commits and publishes to PyPI. Two footguns require manual follow-up.

## 1. Sync uv.lock after PSR bumps the version

PSR updates `pyproject.toml` with the new version but does **not** update `uv.lock`.
The next CI push will red because the lock file is out of date. Fix immediately after the
release tag appears:

```
uv lock
git add uv.lock
git commit -m "build: sync uv.lock project version to <version>"
```

Replace `<version>` with the version PSR just released (e.g. `0.7.0`).

## 2. Never write a skip-ci token — in any commit or squash-merge message

The `git_guard` pre-tool hook blocks skip-ci tokens in CLI `git`/`gh` commands, and the
`no-skip-ci` pre-commit hook blocks &#91;skip ci&#93; and &#91;ci skip&#93; in staged file content.
But neither can see text typed into the **GitHub UI** squash-merge title box.

Forbidden tokens — do not write any of these anywhere in a commit message, PR title, or
squash-merge message:

- `[no ci]`
- `[skip actions]`
- `[actions skip]`
- `skip-checks: true` (as a commit trailer)
- the bracket-enclosed forms of `skip ci` and `ci skip` (caught by hooks locally, but the
  GitHub-UI squash title is the human's responsibility — hooks never see it)

If a skip-ci token reaches a squash-merge title on GitHub, the workflow is silently cancelled
and the release never publishes. There is no error — just a missing tag and a missing PyPI
release.

## 3. Verify the release published

Before considering the release done, confirm:

1. The new tag exists: `git fetch --tags && git tag --sort=-v:refname | head -5`
2. The PyPI release is live: check <https://pypi.org/project/yandex-cli/#history>
3. The `uv.lock` sync commit is merged without triggering another PSR version bump
   (a `build:` prefix is non-releasing by PSR convention).
