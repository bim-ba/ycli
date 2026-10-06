# Changelog

All notable changes to this project are documented here, newest first, following
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). From v0.2.0 on, every
entry below is generated automatically by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) from the
[Conventional Commits](https://www.conventionalcommits.org/) on `main` — do not edit
released sections by hand.

<!-- version list -->

## v0.95.0 (2026-10-06)

### Build System

- Pydantic-core is a dependency ycli names itself
  ([`fe555c0`](https://github.com/bim-ba/ycli/commit/fe555c0101f071127d05dc7b224bcd44f0da81dd))

- Re-lock uv.lock for 0.94.0
  ([`c8250f2`](https://github.com/bim-ba/ycli/commit/c8250f27730a228fbd8cec6274dd1efae84b7f4f))

### Chores

- The future import goes from 39 files that do not need it
  ([`1a40fee`](https://github.com/bim-ba/ycli/commit/1a40feefca4c62b1c24128a239b842127f0c03c4))

### Continuous Integration

- **e2e**: The live jobs are given the account the access steps grant to
  ([`ecf514e`](https://github.com/bim-ba/ycli/commit/ecf514ea3698a8363cc79adead74799add4ab111))

### Refactoring

- Two properties of the models that nothing reads are gone
  ([`dd15bc9`](https://github.com/bim-ba/ycli/commit/dd15bc939fb4b0cf4720a6983c47144b9f0c1bb0))

### Testing

- A three-valued boolean option is checked to be a --x/--no-x pair
  ([`a8aedff`](https://github.com/bim-ba/ycli/commit/a8aedffa342b0024882a8be1c4075e029ba3ec9c))

- **e2e**: A number under a key nothing knows never reaches a fixture
  ([`d6275aa`](https://github.com/bim-ba/ycli/commit/d6275aac3ac9543ee7b78ca8a5ba903a56c8111b))

- **e2e**: Access is granted to a named account and taken back, on a page, a form and a project
  ([#141](https://github.com/bim-ba/ycli/pull/141),
  [`eee6ad0`](https://github.com/bim-ba/ycli/commit/eee6ad0a591e5a61838a3b5b00a6ca92dc574c7b))

- **e2e**: DataLens has a live scenario, run by hand, and its real replies are recorded
  ([`f4b04cc`](https://github.com/bim-ba/ycli/commit/f4b04cc9cc7598d056c90de3135bec6780804476))

- **e2e**: No key twice is asserted on the issues nobody touched today
  ([`6a76914`](https://github.com/bim-ba/ycli/commit/6a76914785e3bdca5bda212e3f282aadc3a21ce6))

### Breaking Changes

- SDK: `ycli.yandex.wiki.pages.models.PageDetails.owner_username` and
  `ycli.yandex.tracker.links.models.Link.object_display` are removed; read `owner.user.username` and
  `object.display`. The output of the CLI and of the MCP tools does not change: a property was never
  part of it.


## v0.94.0 (2026-10-06)

### Build System

- Re-lock uv.lock for 0.93.0
  ([`6e8d432`](https://github.com/bim-ba/ycli/commit/6e8d432e1cff6eb73b4a8f6c1d3b025d51a33735))

### Documentation

- Service cards on the home page and an overview page for each service
  ([#383](https://github.com/bim-ba/ycli/pull/383),
  [`8069a3b`](https://github.com/bim-ba/ycli/commit/8069a3b69d2bb082be701c4cc5571b2902e8d658))

### Features

- **datalens**: A secret of a request is a SecretStr, masked wherever it is printed
  ([#388](https://github.com/bim-ba/ycli/pull/388),
  [`53abece`](https://github.com/bim-ba/ycli/commit/53abecef0fecbca198b5126a494bf924d257a456))


## v0.93.0 (2026-10-06)

### Build System

- Re-lock uv.lock for 0.92.0
  ([`0606c33`](https://github.com/bim-ba/ycli/commit/0606c33c4524e99229f03ca715a2cc1a1d8e08f5))

### Features

- **datalens**: A kind the specification does not list is read as it came
  ([#391](https://github.com/bim-ba/ycli/pull/391),
  [`99554cf`](https://github.com/bim-ba/ycli/commit/99554cf078bcc853db0626a9df6e13af08b65b1c))


## v0.92.0 (2026-10-06)

### Build System

- Re-lock uv.lock for 0.91.0
  ([`9a784b3`](https://github.com/bim-ba/ycli/commit/9a784b3f5851f08e05cf63f574b252139d8b767c))

### Documentation

- **datalens**: The skill names everything ycli wraps today
  ([`3656c64`](https://github.com/bim-ba/ycli/commit/3656c642f98a08125b700e643016a8be637ea0f7))

### Features

- **tracker**: The user of an absence is the user of the directory, and a file names its comment
  ([`5164aa1`](https://github.com/bim-ba/ycli/commit/5164aa1c0de9bb6de9a1d0d8fa7c3e4abd7103f3))

### Testing

- **e2e**: A step may wait for what only the owner can name, and imports and absences are written
  ([#141](https://github.com/bim-ba/ycli/pull/141),
  [`3c98f06`](https://github.com/bim-ba/ycli/commit/3c98f06e14770a44e6cda729ff2fb26835a4d875))

### Breaking Changes

- **tracker**: SDK: `ycli.yandex.tracker.gaps.models.GapUser` is gone; the `user` of a `Gap` and of
  a `UserGaps` is `ycli.yandex.tracker.models.User`. `tracker gaps create` and `gaps search` print
  three more keys of the user (`groups`, `welcomeMailSent`, `position`), `null` or `[]` when the API
  leaves them out.


## v0.91.0 (2026-10-06)

### Build System

- Re-lock uv.lock for 0.90.0
  ([`3b09d13`](https://github.com/bim-ba/ycli/commit/3b09d132d90f0cef1b429ddf2ede8c77aca88c63))

### Features

- **datalens**: Entries are found, their relations, revisions and permissions read
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`78b9b1f`](https://github.com/bim-ba/ycli/commit/78b9b1f96a66eb0bc0516d166d41f65c2e326c5d))

### Testing

- **e2e**: Live scenarios write what hangs on an issue, a board, a queue and a project
  ([#141](https://github.com/bim-ba/ycli/pull/141),
  [`af4d9c8`](https://github.com/bim-ba/ycli/commit/af4d9c863c2b1c7bfbbae3eed6a074fe0b416f3a))


## v0.90.0 (2026-10-06)

### Build System

- Re-lock uv.lock for 0.89.3
  ([`d48a540`](https://github.com/bim-ba/ycli/commit/d48a5406fd5b0e7967dfb49b7b4c535c51d1c106))

### Features

- **tracker**: A checklist change returns the issue, and four more replies name their fields
  ([`65db9ff`](https://github.com/bim-ba/ycli/commit/65db9ff0a7545d8ccc34819518654c8a0ca8d00c))

### Breaking Changes

- **tracker**: `tracker checklists create` / `update` / `delete` / `clear` print the issue as
  `tracker issues get` does: `status`, `type`, `priority` and `queue` are a key, `createdBy` is a
  name (each was the object the API sent), and the fields of an issue the reply leaves out are
  printed as `null`. The MCP tools return the same.

- SDK: `tracker.checklists.models.Checklist`, `tracker.links.models.LinkObject`,
  `tracker.remotelinks.models.RemoteApplication` and the module `tracker.applications.models` are
  gone; use `Issue`, `KeyedReference` and `Application` of `ycli.yandex.tracker.models`. The class
  of an issue's checklist item is named `IssueChecklistItem`;
  `tracker.checklists.models.ChecklistItem` is still that class.


## v0.89.3 (2026-10-06)

### Bug Fixes

- **forms**: The name of an image clone is said to be ignored, and a key set to only grow
  ([`4938405`](https://github.com/bim-ba/ycli/commit/49384058e5f4d143846f2e7e7a0075a3b965c71b))

### Build System

- Re-lock uv.lock for 0.89.2
  ([`b45f18e`](https://github.com/bim-ba/ycli/commit/b45f18efab481ff0d3ee8f7281eeaf4c73e11e06))

### Continuous Integration

- **e2e**: The nightly live run is one job per service
  ([`e109c0b`](https://github.com/bim-ba/ycli/commit/e109c0b148a2bddf17e831e12e688c532d567d62))


## v0.89.2 (2026-10-06)

### Bug Fixes

- **datalens**: A boolean option says yes, no or nothing
  ([`7f8f2d7`](https://github.com/bim-ba/ycli/commit/7f8f2d7f1865c95ec9707c27274ead1e7811e33a))

### Build System

- Re-lock uv.lock for 0.89.1
  ([`954072b`](https://github.com/bim-ba/ycli/commit/954072be7bba1932b3b763355be215db97125894))


## v0.89.1 (2026-10-06)

### Bug Fixes

- **datalens**: A whole number is sent whole, not as a fraction
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`dad6a8a`](https://github.com/bim-ba/ycli/commit/dad6a8a37e82de33626d74a28eb1fef19187b41e))

### Build System

- Re-lock uv.lock for 0.89.0
  ([`dbf3090`](https://github.com/bim-ba/ycli/commit/dbf3090cb8607b24f77a2bac5ba3789f44530254))

### Testing

- **e2e**: A live scenario writes what a form is made of
  ([#141](https://github.com/bim-ba/ycli/pull/141),
  [`3209e19`](https://github.com/bim-ba/ycli/commit/3209e19c5efa5504a0367d868808ea15263208c6))

- **e2e**: A live scenario writes what lives on a Wiki page
  ([#141](https://github.com/bim-ba/ycli/pull/141),
  [`4835d4c`](https://github.com/bim-ba/ycli/commit/4835d4c64191f25a7a3673d276b793fac9524e50))


## v0.89.0 (2026-10-06)

### Bug Fixes

- **wiki**: A listing of attachments declares every field of an attached file
  ([`0c0625c`](https://github.com/bim-ba/ycli/commit/0c0625cb45b2af10f25c681694312de828832ada))

### Build System

- Re-lock uv.lock for 0.88.0
  ([`95972f8`](https://github.com/bim-ba/ycli/commit/95972f817c4f2271efc5d4f2cfc30f3332ada722))

### Breaking Changes

- **wiki**: SDK: `ycli.yandex.wiki.attachments.models.Attachment` is gone; `wiki.attachments.list`
  returns `AttachedFile`, which has the same four fields and seven more.


## v0.88.0 (2026-10-06)

### Build System

- Re-lock uv.lock for 0.87.0
  ([`837e4cd`](https://github.com/bim-ba/ycli/commit/837e4cd924ebac2d5e686ce9505beed2d6b2ea4b))

### Features

- **datalens**: The members of the organization are listed
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`6b12a6d`](https://github.com/bim-ba/ycli/commit/6b12a6df18d129625c484fd4f06cd827f01edb73))


## v0.87.0 (2026-10-06)

### Build System

- Re-lock uv.lock for 0.86.0
  ([`ab8e41f`](https://github.com/bim-ba/ycli/commit/ab8e41fa935e7accee0ecf83f4186deb59c15118))

### Features

- **wiki**: The reply models name the fields Wiki sends, and a closed issue its resolution
  ([#377](https://github.com/bim-ba/ycli/pull/377),
  [`6211ed4`](https://github.com/bim-ba/ycli/commit/6211ed4b1ea366d9c0d13158309b9b0e9c465e06))


## v0.86.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.85.0
  ([`e58e66d`](https://github.com/bim-ba/ycli/commit/e58e66d230ec7420216630ab4a143a36f29fa6bd))

### Features

- **datalens**: Locks on entries, taken, extended and released
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`a95b729`](https://github.com/bim-ba/ycli/commit/a95b729c7aa97bb6b2d88c7e08cdaab607ccde17))


## v0.85.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.84.1
  ([`03ba5ed`](https://github.com/bim-ba/ycli/commit/03ba5ed2615bd59e19f5f468fb3c0a3dcbcd8656))

### Features

- **tracker**: The reply models name the fields Tracker sends and documents
  ([#377](https://github.com/bim-ba/ycli/pull/377),
  [`a47f917`](https://github.com/bim-ba/ycli/commit/a47f917cc1d2fe41023591bc5c70acab3496ce76))

### Breaking Changes

- **tracker**: SDK: `ycli.yandex.tracker.transitions.models.StatusRef` is gone. With `id` and `self`
  it had the shape of `ycli.yandex.tracker.models.KeyedReference`, which `Transition.to` now is.


## v0.84.1 (2026-10-05)

### Bug Fixes

- **datalens**: A validation error names the field wherever DataLens lists it
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`306876d`](https://github.com/bim-ba/ycli/commit/306876d72b86dbbde35a3a71f06c97bd58413524))

### Build System

- Re-lock uv.lock for 0.84.0
  ([`c5a04e5`](https://github.com/bim-ba/ycli/commit/c5a04e516961a19b2b86165da314b8c1466ba18c))

### Testing

- **e2e**: A recorded reply gives the same fixture whatever ycli knows elsewhere
  ([`a6e278c`](https://github.com/bim-ba/ycli/commit/a6e278ce96a511227c79d06407bdf81020df7432))


## v0.84.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.83.1
  ([`5e05c67`](https://github.com/bim-ba/ycli/commit/5e05c67fd6a697439dc0c5a76b219ff1f5c933f2))

### Features

- **datalens**: Workbooks, read and written from the CLI, the MCP server and Python
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`a90cec5`](https://github.com/bim-ba/ycli/commit/a90cec55d0f64f8220c79568592fde449fa7b2c6))


## v0.83.1 (2026-10-05)

### Bug Fixes

- **datalens**: A validation error names the field DataLens refused
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`cd60db4`](https://github.com/bim-ba/ycli/commit/cd60db471257cb59e3245b1eb69b40b84576b589))

### Build System

- Re-lock uv.lock for 0.83.0
  ([`e6ab973`](https://github.com/bim-ba/ycli/commit/e6ab97393462d5e4064c82855d2083ce9979b12d))


## v0.83.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.82.1
  ([`a94b954`](https://github.com/bim-ba/ycli/commit/a94b9549ab024af094e484c0ce7dd444b0dfbcc6))

### Features

- **datalens**: Collections, read and written from the CLI, the MCP server and Python
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`d5a225d`](https://github.com/bim-ba/ycli/commit/d5a225dedff207c127428a2adb4e6470e6939c06))


## v0.82.1 (2026-10-05)

### Bug Fixes

- **datalens**: A generated model requires only what tells a kind; the arguments of an operation
  stay ([#376](https://github.com/bim-ba/ycli/pull/376),
  [`d98881d`](https://github.com/bim-ba/ycli/commit/d98881d4688691b82d87ec0ee1f6ba0c598c050f))

### Build System

- Re-lock uv.lock for 0.82.0
  ([`c83b754`](https://github.com/bim-ba/ycli/commit/c83b754e67a6ec3800056fe0a483c16e5414efc0))

### Testing

- **e2e**: The real replies of the API are recorded as fixtures, scrubbed
  ([#143](https://github.com/bim-ba/ycli/pull/143),
  [`c0b2fae`](https://github.com/bim-ba/ycli/commit/c0b2faeba6f12673e7680d24c0a6232a2d9daa4f))


## v0.82.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.81.2
  ([`7178ce5`](https://github.com/bim-ba/ycli/commit/7178ce5fad94968c0e91e8170b9913f8294b2212))

### Features

- **mcp**: A tool lists at most 32 KB of schema; a larger body is read with schema_get
  ([#365](https://github.com/bim-ba/ycli/pull/365),
  [`ebc0d7a`](https://github.com/bim-ba/ycli/commit/ebc0d7ad062102cb9681326acd489481eac058e6))


## v0.81.2 (2026-10-05)

### Bug Fixes

- **datalens**: A reply is read even when DataLens leaves out a field its document requires
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`5b5b335`](https://github.com/bim-ba/ycli/commit/5b5b33569d7ccde5b4074f86fa9de97ff6d2d80c))

### Build System

- Re-lock uv.lock for 0.81.1
  ([`ae58625`](https://github.com/bim-ba/ycli/commit/ae5862569566124ff837f2da2cd5b13b099c431f))


## v0.81.1 (2026-10-05)

### Bug Fixes

- **settings**: An error about the credentials never quotes the value that failed
  ([`da7ef04`](https://github.com/bim-ba/ycli/commit/da7ef04e0fb0009bc4519b6e188613ee258b0bfd))

### Build System

- Re-lock uv.lock for 0.81.0
  ([`57d54f6`](https://github.com/bim-ba/ycli/commit/57d54f6149dfa9e73317377237483aaf8b9e22c9))


## v0.81.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.80.0
  ([`0aaceeb`](https://github.com/bim-ba/ycli/commit/0aaceeba19b5a71eef74d554fef74a09ce2a2a3f))

- **deps**: FastMCP 4.0.11, which stops inlining a schema that would grow past its limits
  ([#372](https://github.com/bim-ba/ycli/pull/372),
  [`e14bef0`](https://github.com/bim-ba/ycli/commit/e14bef0d1175d7ae4a0dd5252c8926c3ed95ad27))

### Features

- **cli**: -F and --body-file set any field of a request body on every command
  ([#354](https://github.com/bim-ba/ycli/pull/354),
  [`b2851bd`](https://github.com/bim-ba/ycli/commit/b2851bd3c86aecd7d3309ed2e42913bc02b6691e))

### Breaking Changes

- **cli**: A flag of the command now wins over `-F`, and `-F` over `--body-file`. `tracker issues
  create` / `update` and `forms surveys create` / `update`: `--summary A -F summary=B` sends A (it
  sent B). `forms questions create` / `update` and the eight `forms conditions ... create` /
  `update`: a flag given beside `--body-file` is no longer dropped, it wins over the file.

- `tracker entities create` / `update`: `-F priority=high` becomes `-F 'fields[priority]=high'`;
  `-F` names a key of the body everywhere.

- `forms subscriptions create` / `update` and `forms filling submit`: `--body-file` is no longer a
  required option of its own; the body comes from `--body-file` and `-F` together. `forms filling
  submit` with neither is still refused, and a body that does not fit the model is refused as
  before.

- SDK: `ycli.yandex.core.session.BeforeSend` returns `httpx2.Request | None`, and a request it
  returns is sent in place of the one it was shown. A hook that returns `None` works as before; only
  a hook that returned something else, which was ignored, has to change.


## v0.80.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.79.1
  ([`5f4fb2e`](https://github.com/bim-ba/ycli/commit/5f4fb2e54ae1ea676b2b48da822630a615ddc433))

### Features

- **datalens**: DataLens joins the services, with the details of its instance
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`999265e`](https://github.com/bim-ba/ycli/commit/999265e57ffc19be7f5c30bd369f2ee438bfeef9))


## v0.79.1 (2026-10-05)

### Bug Fixes

- **datalens**: A generated model copies no limit on a value from the specification
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`6ccdfbd`](https://github.com/bim-ba/ycli/commit/6ccdfbd81f43306689c63e570adc3f80aa72126a))

### Build System

- Re-lock uv.lock for 0.79.0
  ([`116bf90`](https://github.com/bim-ba/ycli/commit/116bf901d183a40d9fd6bd3187638ca5dfb92e98))


## v0.79.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.78.0
  ([`67822d6`](https://github.com/bim-ba/ycli/commit/67822d623073d95ccdfcdca6c448ba8fd151dc6b))

### Features

- **datalens**: The models of every DataLens schema are generated from its specification
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`07abea7`](https://github.com/bim-ba/ycli/commit/07abea7418ed2234d17354be092444dbae1b4d6b))

### Refactoring

- **api**: A body field that differs for ycli's own reason says so above itself
  ([#332](https://github.com/bim-ba/ycli/pull/332),
  [`7db6991`](https://github.com/bim-ba/ycli/commit/7db699186ef087888cc92b62cd186957eed5ced4))


## v0.78.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.77.0
  ([`6334be5`](https://github.com/bim-ba/ycli/commit/6334be51e6baf774c8e688bb4c585b9be4949140))

### Features

- **core**: An RPC operation is written with RPC(), and a listing can page in its body
  ([#352](https://github.com/bim-ba/ycli/pull/352),
  [`b28412c`](https://github.com/bim-ba/ycli/commit/b28412c8281771805b6967a32764315e482e8e44))

### Refactoring

- **api**: A field the API ignores is explained by its mark, not by a second list
  ([#332](https://github.com/bim-ba/ycli/pull/332),
  [`0a104ac`](https://github.com/bim-ba/ycli/commit/0a104ac03f4e947c21d3a803102b7492befccc3b))


## v0.77.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.76.0
  ([`b56121f`](https://github.com/bim-ba/ycli/commit/b56121f6b4738aa2096045c9681eca810b73b6e9))

### Features

- A service account's key and a Yandex Cloud organization sign in
  ([#251](https://github.com/bim-ba/ycli/pull/251),
  [`77536c7`](https://github.com/bim-ba/ycli/commit/77536c78bb3bc13515fca84a6c7d6bad734a6bf0))


## v0.76.0 (2026-10-05)

### Bug Fixes

- Nine places where a command and its tool behaved differently
  ([#328](https://github.com/bim-ba/ycli/pull/328),
  [`c1c78e4`](https://github.com/bim-ba/ycli/commit/c1c78e432158d46e645c2ab6226875bf7acf7906))

### Build System

- Re-lock uv.lock for 0.75.0
  ([`d727e13`](https://github.com/bim-ba/ycli/commit/d727e131d72ff429e49742c8597da4948e298f2b))

### Chores

- **api**: The DataLens snapshot holds the 141 operations published today
  ([#268](https://github.com/bim-ba/ycli/pull/268),
  [`845332b`](https://github.com/bim-ba/ycli/commit/845332bcedc4850f9e20417f63c9c5e6282c8643))

### Refactoring

- From __future__ import annotations stays only where a module needs it
  ([#312](https://github.com/bim-ba/ycli/pull/312),
  [`a015b18`](https://github.com/bim-ba/ycli/commit/a015b189bbdb605c5aed2001b5f1bafe25270e45))

### Testing

- An option that names a set's values by hand says why above itself
  ([#332](https://github.com/bim-ba/ycli/pull/332),
  [`d892d3a`](https://github.com/bim-ba/ycli/commit/d892d3af93944b715846ffb02ed4558b28617f3e))

- The checks of conventions and of the public surface live in tests/architecture
  ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`4ad7c01`](https://github.com/bim-ba/ycli/commit/4ad7c01ff994037bccd6cfaeba2f0e28ec607570))

- The tests of the SDK live in tests/unit/yandex, the contract in tests/contract
  ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`838240a`](https://github.com/bim-ba/ycli/commit/838240a2946c6e9c5ccec3241524c9687f488b20))

- The tests of the tools around the package live in tests/tooling
  ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`472d877`](https://github.com/bim-ba/ycli/commit/472d877ac283c4604bb5de43de3a9077ff46202a))

- The tests of what is published live in tests/docs
  ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`c5f228f`](https://github.com/bim-ba/ycli/commit/c5f228f8698f116c0490415d04aea714313a6c5b))

### Breaking Changes

- Tool parameters: `tracker_entities_search` takes `body` instead of `input_text` and `order_by`;
  `tracker_worklog_list_global` takes `created_from` / `created_to` instead of `created_at`;
  `tracker_attachments_import` takes `data` as base64 instead of text.

- Options: `tracker triggers webhook-log-list --date-from/--date-to` (were `--from/--to`), `tracker
  worklog list-global --created-from/--created-to` (were `--from/--to`); `tracker entities
  events-list` without `--all` stops at the configured cap; `tracker entities comments list --all
  --limit N` is `--limit N`.


## v0.75.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.74.0
  ([`87033ee`](https://github.com/bim-ba/ycli/commit/87033ee0c5f87be4f5d810b1730b87ce1338c8ac))

### Refactoring

- The HTTP method is http.HTTPMethod and the effect is an enum
  ([#312](https://github.com/bim-ba/ycli/pull/312),
  [`23c8717`](https://github.com/bim-ba/ycli/commit/23c8717b8792e1e2713898acd8dd2e53a2ff42c3))

### Testing

- A status error built by hand says why above the raise
  ([#332](https://github.com/bim-ba/ycli/pull/332),
  [`ddf89e2`](https://github.com/bim-ba/ycli/commit/ddf89e299e1e58c62590b4f50e5c4b5b197c0de1))

- The tests of the CLI live in tests/unit/cli ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`87c7573`](https://github.com/bim-ba/ycli/commit/87c75735fac818d59979e55f62520f90354628dc))

- The tests of the MCP server live in tests/unit/mcp
  ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`20716aa`](https://github.com/bim-ba/ycli/commit/20716aada88826287bf8c69d641538b42135b4df))

### Breaking Changes

- The type aliases `ycli.yandex.core.endpoint.Method` and the `Literal` `Effect` are gone.
  `Endpoint.method` is typed `http.HTTPMethod` and `Endpoint.effect` is an `Effect` member; code
  that builds an `Endpoint` with a string still runs, and a type checker now reports it.


## v0.74.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.73.0
  ([`1d2ff22`](https://github.com/bim-ba/ycli/commit/1d2ff22a5a36e45592100f41b20da41043649add))

### Features

- Ycli sends what the caller gave and nothing of its own
  ([#296](https://github.com/bim-ba/ycli/pull/296),
  [`494fc4c`](https://github.com/bim-ba/ycli/commit/494fc4c6f6400ac06c7ce92495fae459fb60daa2))

### Testing

- A refusal says why where it is, not in a list ([#332](https://github.com/bim-ba/ycli/pull/332),
  [`3d44b4f`](https://github.com/bim-ba/ycli/commit/3d44b4f62dc7a7066520c73aa6725b6cb580da51))

- An effect that differs from the method says why above the endpoint
  ([#332](https://github.com/bim-ba/ycli/pull/332),
  [`7593dd2`](https://github.com/bim-ba/ycli/commit/7593dd25c114b839391e17e4723a4c8cfbfceb16))

- An operation served by one surface says why above its method
  ([#332](https://github.com/bim-ba/ycli/pull/332),
  [`10e20b5`](https://github.com/bim-ba/ycli/commit/10e20b5846fa862ff73e2eb29feb89985c92fee6))

- The architecture checks are a package, a module per invariant
  ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`6f5b851`](https://github.com/bim-ba/ycli/commit/6f5b8517e69c68c1cdd5a58ef4476e702136f020))

### Breaking Changes

- Options that ycli used to fill are required: `tracker statuses create --type`, `tracker
  remotelinks create --relationship`, `tracker worklog create --start`, `tracker entities
  reports-create --type` (a new option) and `--field`, `tracker workflows create --step`, `wiki
  uploadsessions parts-upload --part-number`, `wiki grids rows move --row-id`, `wiki grids columns
  move --column-slug --position`.

- Options that go together: `--deadline` needs `--deadline-type` (a new option; checklist items),
  `--option` needs `--options-type` (Tracker fields and local fields); `wiki pages append` needs
  `--location`; every column of `wiki grids columns create` needs `slug` and `required`.

- Defaults of ycli's own are no longer sent, the API's apply: Wiki search `cursor`, `limit`,
  `order_by`, `highlight`, `show_obsolete`; `with_data` of a grid clone; `subscribe_me` of a page
  clone; `fallback` and `regex` of an append anchor; `format` and `upload` of a Forms export;
  `format` and `orderAsc` of a Tracker report and of an entity search; `backlink=false` of a remote
  link; `copy_inherited_access=false` of a page move; `page: 1` of `forms questions move
  --position`; `fields=content` of `wiki pages get-by-id` on the command line.

- Booleans are three-valued. 38 options send `false` for `--no-x` (36 had no such form); 23 tool
  parameters and the SDK arguments behind them are `bool | None = None`. `backlink` of a remote link
  is a boolean on every surface (it was the string "true" in the SDK and the tool).

- The input schema of 37 MCP tools changes: 20 in their own parameters, 17 inside `body`
  (`tracker_worklog_create`, the five checklist tools, `tracker_entities_reports_create`,
  `wiki_grids_columns_create`, `wiki_grids_columns_move`, `wiki_grids_rows_move`,
  `wiki_grids_cells_update` among them).

- SDK: `ycli.yandex.core.endpoint.flag` is removed; an empty string is sent as given;
  `subscriptions.create` / `update` no longer cut `id` from the body. Body models:
  `RemoteLinkCreate.relationship`, `WorklogCreate.start`, `ReportParameters.type`,
  `DeadlineInput.deadline_type`, `NewColumnSchema.slug` / `.required`, `RowsMove.row_id`,
  `ColumnsMove.column_slug` / `.position` and `UpdateCellSchema.value` are required; `revision` is
  optional in eight Wiki grid bodies; the fields that carried a default are `None` unless given.


## v0.73.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.72.0
  ([`26621f3`](https://github.com/bim-ba/ycli/commit/26621f3288965c60d4889d3ca6ad36192f224701))

### Refactoring

- A survey is `survey_id` and a bulk change is `bulk_id` in every method
  ([#328](https://github.com/bim-ba/ycli/pull/328),
  [`8b7ee59`](https://github.com/bim-ba/ycli/commit/8b7ee59cfbfdd1e9e5a16262ef1bdcc956307ecc))

### Breaking Changes

- The argument `survey` is renamed to `survey_id` in `forms.filling.get`, `forms.filling.submit` and
  `forms.filling.suggest`, in the `endpoints` functions of the same names and in the tools
  `forms_filling_get`, `forms_filling_submit`, `forms_filling_suggest`. The argument `operation_id`
  is renamed to `bulk_id` in `tracker.entities.bulk_get`, its `endpoints` function and the tool
  `tracker_entities_bulk_get`. A call that passes the value by position is not affected. On the CLI
  the positionals are shown as `SURVEY_ID` and `BULK_ID`; commands are typed as before.


## v0.72.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.71.0
  ([`cb656e3`](https://github.com/bim-ba/ycli/commit/cb656e3f3e858127125628b6587d1df7cf344254))

### Refactoring

- The key of an issue is `issue_key` on every surface (#328)
  ([#328](https://github.com/bim-ba/ycli/pull/328),
  [`8e17e2f`](https://github.com/bim-ba/ycli/commit/8e17e2f640eded801a2c11a304bf0ca20e88d47e))

### Breaking Changes

- The argument `key` is renamed to `issue_key` in these SDK methods, in the `endpoints` functions of
  the same names and in their MCP tools (`tracker_<resource>_<method>`):


## v0.71.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.70.0
  ([`27bacaf`](https://github.com/bim-ba/ycli/commit/27bacaf74cc26d2cfb0d762bd4bf6b87ff5c7cef))

### Refactoring

- A parameter has one name, the SDK argument's ([#328](https://github.com/bim-ba/ycli/pull/328),
  [`5891751`](https://github.com/bim-ba/ycli/commit/589175150143c5c38f6e34cde7f7058dad75628a))

### Breaking Changes

- These CLI options changed; the old spellings no longer work.


## v0.70.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.69.0
  ([`71c3304`](https://github.com/bim-ba/ycli/commit/71c3304387928f8861a535282b8c0b837fc91198))

### Refactoring

- Five more operations take the name the convention gives them
  ([#268](https://github.com/bim-ba/ycli/pull/268),
  [`14025ed`](https://github.com/bim-ba/ycli/commit/14025ed1b0d4822fd56d76f34a6a447f81ec2c72))

### Breaking Changes

- These names changed; the old ones no longer answer.


## v0.69.0 (2026-10-05)

### Build System

- Re-lock uv.lock for 0.68.0
  ([`5f05b76`](https://github.com/bim-ba/ycli/commit/5f05b76e7df0f330c2331b95b20aebeff464dde2))

### Documentation

- How to call the API asynchronously through the endpoints
  ([#321](https://github.com/bim-ba/ycli/pull/321),
  [`4a0d36f`](https://github.com/bim-ba/ycli/commit/4a0d36fcd188383b784fc52ddbeaf8a8d4fc2ced))

### Refactoring

- A set of ycli's own is a StrEnum: LogLevel, LogFormat, CredentialKind
  ([#312](https://github.com/bim-ba/ycli/pull/312),
  [`c28e42e`](https://github.com/bim-ba/ycli/commit/c28e42e07de1bceeff4d041f423c7fd12d832a86))

- An operation has one name, formed by one convention
  ([#268](https://github.com/bim-ba/ycli/pull/268),
  [`c4f904f`](https://github.com/bim-ba/ycli/commit/c4f904f3252ef10f48fbc2ea740baee166cf39fe))

- Core clean-up from the code audit, no behaviour change
  ([`0130ea6`](https://github.com/bim-ba/ycli/commit/0130ea6c087428567fbe84af13d8faa7114667dc))

- Reading the environment outside settings.py is caught by ruff
  ([#323](https://github.com/bim-ba/ycli/pull/323),
  [`9dd1838`](https://github.com/bim-ba/ycli/commit/9dd1838980ecd1065b05f8f4c385af083f9db5e3))

### Breaking Changes

- These names changed; the old ones no longer answer. Each line is the SDK method, then the new CLI
  command and MCP tool.


## v0.68.0 (2026-10-05)

### Bug Fixes

- **mcp**: A tool returns what the API answered instead of judging an empty reply
  ([#314](https://github.com/bim-ba/ycli/pull/314),
  [`a74872f`](https://github.com/bim-ba/ycli/commit/a74872f6beac1c2efed099cbbc25f9e334b3d0b6))

### Build System

- Re-lock uv.lock for 0.67.1
  ([`50c3bc8`](https://github.com/bim-ba/ycli/commit/50c3bc8b17ed06583d0f8b848dfddd1bae1805dc))

### Chores

- **api**: The kind-of-action markup of published operations is deleted
  ([#313](https://github.com/bim-ba/ycli/pull/313),
  [`826ec69`](https://github.com/bim-ba/ycli/commit/826ec693e940dba67a1d18d47689d68f9d8a8f43))

### Testing

- The per-resource model tests that covered nothing of their own are deleted
  ([#319](https://github.com/bim-ba/ycli/pull/319),
  [`609d3ef`](https://github.com/bim-ba/ycli/commit/609d3efdf88430779d6948bf2cbfe4eebd3ad5e7))

### Breaking Changes

- **mcp**: `ycli.yandex.models.require_found` is removed, and these tools return the API's reply
  instead of raising on an empty one: tracker_issues_get, tracker_queues_get,
  tracker_localfields_get, tracker_me_get, wiki_me_get, forms_me_get, forms_surveys_get,
  forms_questions_get, forms_operations_get, forms_filling_get, forms_hooks_get,
  forms_conditions_question_get, forms_conditions_page_get, forms_conditions_submit_get,
  forms_conditions_hook_get.


## v0.67.1 (2026-10-04)

### Bug Fixes

- **wiki**: The texts say what a grid revision guards: a cell, not the whole grid
  ([#300](https://github.com/bim-ba/ycli/pull/300),
  [`b0454ac`](https://github.com/bim-ba/ycli/commit/b0454acef75f8389d5254993d90c5c1d223a4807))

### Build System

- Re-lock uv.lock for 0.67.0
  ([`82280a7`](https://github.com/bim-ba/ycli/commit/82280a71d9bd9208242d2b1c52534c97a4902024))

### Documentation

- Design of files in git, one pull / diff / push for every service
  ([#212](https://github.com/bim-ba/ycli/pull/212),
  [`0648bd5`](https://github.com/bim-ba/ycli/commit/0648bd59c4c93fd4ce77f129d91c245ab7c5c878))

- What the grid revision guards, in the design of files in git
  ([#300](https://github.com/bim-ba/ycli/pull/300),
  [`e570c1b`](https://github.com/bim-ba/ycli/commit/e570c1bbfde7bff10fce663b6c6eb05313c48afb))

### Refactoring

- The name of an alias means one thing ([#301](https://github.com/bim-ba/ycli/pull/301),
  [`29a09c0`](https://github.com/bim-ba/ycli/commit/29a09c0aa69a89399cefa362a649ac108d3b98a7))


## v0.67.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.66.2
  ([`d01cc8e`](https://github.com/bim-ba/ycli/commit/d01cc8e021a4f3cf1eddf0e504d5cb0bd7300e16))

### Features

- **cli**: How long --wait waits is a setting, http.max_wait_seconds
  ([#301](https://github.com/bim-ba/ycli/pull/301),
  [`3c3495f`](https://github.com/bim-ba/ycli/commit/3c3495f356996297310e6b4f7337c9e87fce109e))

### Breaking Changes

- **cli**: `ycli.yandex.polling.poll` no longer takes `attempts`; `max_wait_seconds` is required and
  counts the seconds slept.


## v0.66.2 (2026-10-04)

### Bug Fixes

- **models**: Every model field carries a description
  ([#159](https://github.com/bim-ba/ycli/pull/159),
  [`2524104`](https://github.com/bim-ba/ycli/commit/25241044f878447be55499e9b1f47acc06af9a59))

### Build System

- Re-lock uv.lock for 0.66.1
  ([`a4d57de`](https://github.com/bim-ba/ycli/commit/a4d57de11085a3fa9c29bc8edfef5feaad2ebd53))


## v0.66.1 (2026-10-04)

### Bug Fixes

- **api**: Eight operations carry the kind of action they really have
  ([#303](https://github.com/bim-ba/ycli/pull/303),
  [`e8ea7d8`](https://github.com/bim-ba/ycli/commit/e8ea7d84e82d89ad653c6c1899882484ed728618))

### Build System

- Re-lock uv.lock for 0.66.0
  ([`074efae`](https://github.com/bim-ba/ycli/commit/074efaefe687bf3ef2f43f4bb3b1e67be8199a20))

### Documentation

- The agent instructions name nine invariants (ARCH-1..9)
  ([#308](https://github.com/bim-ba/ycli/pull/308),
  [`fd17fe5`](https://github.com/bim-ba/ycli/commit/fd17fe5014392eb9a8a95e66e4786266c98888f7))

### Refactoring

- A resource with no model of its own has no models.py
  ([#234](https://github.com/bim-ba/ycli/pull/234),
  [`8770055`](https://github.com/bim-ba/ycli/commit/8770055217a0ee820c3a444eee8ee8c6f094e718))

- **sdk**: An endpoint function is named like the method that sends it
  ([#306](https://github.com/bim-ba/ycli/pull/306),
  [`b7ba294`](https://github.com/bim-ba/ycli/commit/b7ba294d27997071b45f8b37a60dac478f1b8f74))


## v0.66.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.65.0
  ([`4cbea2a`](https://github.com/bim-ba/ycli/commit/4cbea2a5875f53d27d250ab49a2ce0747f5ab44b))

### Refactoring

- Code and tests that nothing uses are deleted ([#234](https://github.com/bim-ba/ycli/pull/234),
  [`d9ebfea`](https://github.com/bim-ba/ycli/commit/d9ebfeae8fa061ab435c3322e776436519fe7efc))

### Breaking Changes

- Two public SDK names are removed, neither was reachable from a client operation:
  ycli.yandex.core.pagination.HeaderCursorPagination and
  ycli.yandex.tracker.entities.models.ExtendedPermissionsUpdate.


## v0.65.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.64.0
  ([`2b52111`](https://github.com/bim-ba/ycli/commit/2b521113de7f0e3313c12ee9e32109c98a1bab76))

### Refactoring

- An acronym keeps its capitals in a name; an alias is defined once
  ([#160](https://github.com/bim-ba/ycli/pull/160),
  [`629ebae`](https://github.com/bim-ba/ycli/commit/629ebae701850ef16b26da0935c1970df5c76e55))

### Breaking Changes

- Nine public SDK names are renamed, with no alias for the old spelling: Acl -> ACL, AclInput ->
  ACLInput, AclPrincipals -> ACLPrincipals, AclPrincipalsInput -> ACLPrincipalsInput,
  HttpSubscription -> HTTPSubscription, JsonRpcSubscription -> JSONRPCSubscription, SurveyApiKey ->
  SurveyAPIKey, RelativeIdPagination -> RelativeIDPagination, IdStr -> IDStr.


## v0.64.0 (2026-10-04)

### Bug Fixes

- **sdk**: A reply that does not parse and a request that cannot be built are told apart
  ([#298](https://github.com/bim-ba/ycli/pull/298),
  [`ecb3029`](https://github.com/bim-ba/ycli/commit/ecb30295e67e643cf4ecc096854628e9e8e56ac0))

### Build System

- Re-lock uv.lock for 0.63.0
  ([`533d8b3`](https://github.com/bim-ba/ycli/commit/533d8b3c18a8e1f554bca5f60812b3d996792a96))

### Breaking Changes

- **sdk**: A reply that does not parse raises YandexUnexpectedReplyError, a YandexError, instead of
  pydantic.ValidationError.


## v0.63.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.62.0
  ([`94669c0`](https://github.com/bim-ba/ycli/commit/94669c023015d49870d31bfbff7c3a7a393b9dbc))

### Features

- Ycli refuses a request only where it cannot be built; the API answers for the rest
  ([#297](https://github.com/bim-ba/ycli/pull/297),
  [`f288e61`](https://github.com/bim-ba/ycli/commit/f288e61ab904d48454bbbf6d0d726286d0dfeb14))

### Breaking Changes

- Requests ycli refused before are now sent, and the API's own error (or its silent acceptance) is
  what the caller sees: a value longer or shorter than a published limit, both or neither of
  `answer_id` / `answer_key`, an incomplete option group, an empty list, a grant with both or
  neither of user and group, a search window with one end, a non-object `--filter`. `wiki grids
  columns add` no longer derives a column's `slug` from its title: give `slug`, the API requires it.
  `forms questions move` sends a bare `position` from the SDK and MCP as given (the API answers 200
  and moves nothing). `forms.answers.get` no longer raises `YandexInvalidRequestError`. A missing
  field of a request model is a validation error (exit code 1) where the CLI printed a usage error
  (exit code 2).


## v0.62.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.61.0
  ([`60f9cc4`](https://github.com/bim-ba/ycli/commit/60f9cc441c10cf32f126e7f33578076f2c0fd252))

### Features

- The five Tracker sets left strict take any string too
  ([#295](https://github.com/bim-ba/ycli/pull/295),
  [`6544dd4`](https://github.com/bim-ba/ycli/commit/6544dd45c06c9b829f9f238e0f33132fbfcd97f4))

### Breaking Changes

- A value outside these sets is sent to the API instead of being refused: the entity type, the link
  relationship, the reaction name (CLI: usage error before), the project status and the kind of
  absence (also refused by the SDK and the MCP tools before, as `ProjectStatus` and `GapWorkflow`
  typed request-body fields), and a workflow layout `type`. `ProjectStatus`, `GapWorkflow`,
  `EntityType`, `Relationship` and `Reaction` are no longer enum classes: `ProjectStatus.DRAFT`
  becomes the string "DRAFT". `EntityType`, `Relationship` and `Reaction` moved from the resource's
  `cli.py` to its `models.py`.


## v0.61.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.60.0
  ([`a156ecc`](https://github.com/bim-ba/ycli/commit/a156ecc8a34fdb14983e6735119631c336eb63f1))

### Features

- **sdk**: A reply field with a set of values names its set
  ([#294](https://github.com/bim-ba/ycli/pull/294),
  [`c23aeee`](https://github.com/bim-ba/ycli/commit/c23aeee5c8e77eea951738abee3b5e05efa1e8de))


## v0.60.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.59.0
  ([`b9b7093`](https://github.com/bim-ba/ycli/commit/b9b70933f3574a6ef654610f1a531c1abfe1bba3))

### Chores

- **api**: Every listed operation has a kind of action and the API's own verb
  ([#289](https://github.com/bim-ba/ycli/pull/289),
  [`c3ea868`](https://github.com/bim-ba/ycli/commit/c3ea8681b0b1b386680a5ca4713d2f7287dd0256))

### Features

- **cli**: The --jq option is removed; pipe the JSON output to jq
  ([#293](https://github.com/bim-ba/ycli/pull/293),
  [`0f919e5`](https://github.com/bim-ba/ycli/commit/0f919e551238fa0d04df63ffc6aac8476ff8721d))

### Breaking Changes

- **cli**: `--jq EXPR` is no longer an option of any command, and the `yandex-cli[jq]` extra no
  longer exists. Pipe the output instead: `ycli tracker issues get TRACKER-1 -o json | jq -r
  .summary`.


## v0.59.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.58.0
  ([`e8d3ca6`](https://github.com/bim-ba/ycli/commit/e8d3ca69f00d9e04ceecc0454ab2fd5660b138ab))

### Chores

- **api**: A version is v1, v4.1, v3.0, v1beta, v2alpha or v1beta1
  ([#287](https://github.com/bim-ba/ycli/pull/287),
  [`6cb1d60`](https://github.com/bim-ba/ycli/commit/6cb1d6020b815726a371846badb71e02f8ec911d))

- **api**: The snapshot lists six services whose reference is written by hand, and Disk's
  documentation ([#282](https://github.com/bim-ba/ycli/pull/282),
  [`86667b2`](https://github.com/bim-ba/ycli/commit/86667b2abaa12f995a218f3465da66a1e344a7ae))

### Features

- A set of values is the known values plus any string
  ([#288](https://github.com/bim-ba/ycli/pull/288),
  [`9dfc748`](https://github.com/bim-ba/ycli/commit/9dfc7484abc3a5f4f9f83f02f4a7481743bf8d77))

### Refactoring

- **sdk**: A request body is dumped by pydantic's own serializer
  ([#281](https://github.com/bim-ba/ycli/pull/281),
  [`dc50452`](https://github.com/bim-ba/ycli/commit/dc5045234fd91fc93be54759864dff73beeb1a06))

### Testing

- **e2e**: The sweep after a live run removes only what that run named
  ([#285](https://github.com/bim-ba/ycli/pull/285),
  [`5b7db55`](https://github.com/bim-ba/ycli/commit/5b7db55d77206fe9957018a15425fa3e7469255d))

### Breaking Changes

- A value outside a known set is sent to the API instead of being refused by ycli (CLI exit code 2,
  an MCP tool error or a validation error before). In MCP input and output schemas such a field
  changes from `enum` to `anyOf` of the `enum` and a string: 46 tools' input schemas and 60 tools'
  output schemas. CLI options with a set show `TEXT` and "One of: ..." in the help instead of
  `[a|b]`. The sets: AccessAction (forms/access), AccessLevel (forms/access), ExportFormat
  (forms/answers), ExportUpload (forms/answers), AnswerFormat (forms/answers), ConditionOperatorType
  (forms), ConditionItemKind (forms), ConditionComparison (forms), RunStatus (forms/notifications),
  IntegrationType (forms/notifications), WidgetType (forms/questions), ModifyChoicesType
  (forms/questions), ValidatorType (forms/questions), SortDirection (models), GroupSource (models),
  ReportFormat (tracker/entities), ScrollType (tracker/issues), SprintStatus (tracker/sprints),
  StatusType (tracker/statuses), AccessRole (wiki/access), AccessInheritance (wiki/access),
  AttachmentOrder (wiki/attachments), ColumnType (wiki/grids), WidthUnits (wiki/grids),
  ColumnPinType (wiki/grids), BGColor (wiki/grids), TextFormat (wiki/grids), TicketField
  (wiki/grids), OperationType (wiki), Location (wiki), OrderPosition (wiki), PageAccessType (wiki),
  ResolveStatus (wiki), OperationStatus (wiki/operations), GridOrder (wiki/pages), ResourceOrder
  (wiki/resources), SearchDocumentType (wiki/search), SearchOrder (wiki/search)


## v0.58.0 (2026-10-04)

### Build System

- Re-lock uv.lock for 0.57.1
  ([`5bd7453`](https://github.com/bim-ba/ycli/commit/5bd7453315284d7681b7c5ed8407e0a511022157))

### Chores

- **api**: The snapshot lists api360, Metrika, Audience and AdMetrica; a service's own prefix is
  part of base ([#280](https://github.com/bim-ba/ycli/pull/280),
  [`ab9edaa`](https://github.com/bim-ba/ycli/commit/ab9edaa0e24c7f5ea5cf04b08565dfbf6ecd7641))

- **api**: The snapshot lists six more Yandex APIs, with each operation's own name
  ([#275](https://github.com/bim-ba/ycli/pull/275),
  [`8ecb9e7`](https://github.com/bim-ba/ycli/commit/8ecb9e7f30bfb91dcdb989cd9682823f6eb3a345))

### Refactoring

- **mcp**: A tool's tags are derived from its name and its read-only hint
  ([#277](https://github.com/bim-ba/ycli/pull/277),
  [`d9063eb`](https://github.com/bim-ba/ycli/commit/d9063eb2d80cfe4a70048dd66e6d3a5a5f86a20a))

- **sdk**: A closed set of values is defined once ([#279](https://github.com/bim-ba/ycli/pull/279),
  [`ab51c0f`](https://github.com/bim-ba/ycli/commit/ab51c0fa548fb446b8ab299f78c9d312453dd09d))

### Breaking Changes

- **sdk**: SortDirection and GroupSource are imported from ycli.yandex.models, no longer from
  ycli.yandex.wiki.grids.models and ycli.yandex.wiki.access.models.


## v0.57.1 (2026-10-04)

### Bug Fixes

- **cli**: The sign-in wait ends when the code expires, and a question flag of the wrong type is
  refused ([#274](https://github.com/bim-ba/ycli/pull/274),
  [`23e5fd3`](https://github.com/bim-ba/ycli/commit/23e5fd34240fa3d1510e531bdb6bf6c660d538e7))

### Build System

- Re-lock uv.lock for 0.57.0
  ([`4ff1622`](https://github.com/bim-ba/ycli/commit/4ff1622f41028c9abb85ccb2358416dcf156dddb))

### Documentation

- A robots.txt that names both sitemaps ([#273](https://github.com/bim-ba/ycli/pull/273),
  [`b069b44`](https://github.com/bim-ba/ycli/commit/b069b441b3474d2272f948195702e2fd7fb120c7))


## v0.57.0 (2026-10-04)

### Bug Fixes

- **sdk**: A wrong request form is one typed error, and a file option checks its file
  ([#271](https://github.com/bim-ba/ycli/pull/271),
  [`e3deae5`](https://github.com/bim-ba/ycli/commit/e3deae52f9f3b3272f5ae1bd075b46c607eeb8c8))

### Build System

- Re-lock uv.lock for 0.56.0
  ([`832e65a`](https://github.com/bim-ba/ycli/commit/832e65a8db96807b05bb5825e46a9e911962e92f))

### Documentation

- The Russian menu links the MCP prompts and resources page
  ([#270](https://github.com/bim-ba/ycli/pull/270),
  [`7e4d096`](https://github.com/bim-ba/ycli/commit/7e4d096410968a41211bcfac91d62ea020bf1c46))

### Breaking Changes

- **sdk**: Forms.answers.get, forms.answers.integrations_list and tracker.issues.search raise
  YandexInvalidRequestError instead of ValueError for a request of the wrong form.


## v0.56.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.55.0
  ([`90ce6ad`](https://github.com/bim-ba/ycli/commit/90ce6adbd65cf9b09622a9a0cd36376e3e8b04d7))

### Features

- **mcp**: A tool parameter that is not given is None, as in the CLI
  ([#269](https://github.com/bim-ba/ycli/pull/269),
  [`2a74a25`](https://github.com/bim-ba/ycli/commit/2a74a25559a9143969221ec9c9219977dc1ff3d9))

### Testing

- **e2e**: The janitor counts an issue that is already closed as done
  ([#266](https://github.com/bim-ba/ycli/pull/266),
  [`777e114`](https://github.com/bim-ba/ycli/commit/777e114635c374b35797f3c254ada87d4546924a))

### Breaking Changes

- **mcp**: In the input schemas of these MCP tools the default of the listed parameters is null
  instead of "" or 0, an explicit "" is sent to the API instead of being ignored, and `limit` has
  minimum 1 (`limit: 0` is refused; leave it out for the configured cap): forms_answers_list:
  answer_format, date_from, date_to, ordering, questions


## v0.55.0 (2026-10-03)

### Bug Fixes

- **mcp**: The sprint prompt takes a board and a sprint, as approved
  ([#264](https://github.com/bim-ba/ycli/pull/264),
  [`b2ac423`](https://github.com/bim-ba/ycli/commit/b2ac423d29bce7404ce1df99773213327f16f64b))

### Build System

- Re-lock uv.lock for 0.54.0 ([#267](https://github.com/bim-ba/ycli/pull/267),
  [`73b43f0`](https://github.com/bim-ba/ycli/commit/73b43f098d181ee4ec164365c2f02ea262f480fb))

### Features

- **mcp**: Prompts and resources next to the tools ([#264](https://github.com/bim-ba/ycli/pull/264),
  [`b2ac423`](https://github.com/bim-ba/ycli/commit/b2ac423d29bce7404ce1df99773213327f16f64b))

### Testing

- Regenerate the CLI snapshot on main after #265 ([#264](https://github.com/bim-ba/ycli/pull/264),
  [`b2ac423`](https://github.com/bim-ba/ycli/commit/b2ac423d29bce7404ce1df99773213327f16f64b))


## v0.54.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.53.1
  ([`de12aeb`](https://github.com/bim-ba/ycli/commit/de12aeba0f50ef584cda3d1329b0c2113d198b0c))

### Features

- **cli**: An option that is not given is None, so an empty value can be sent
  ([#265](https://github.com/bim-ba/ycli/pull/265),
  [`dda7c09`](https://github.com/bim-ba/ycli/commit/dda7c0937726017a59871bc67826d4d226c6f608))

### Refactoring

- **mcp**: A service's MCP server is a package, mcp/server.py
  ([#263](https://github.com/bim-ba/ycli/pull/263),
  [`766753c`](https://github.com/bim-ba/ycli/commit/766753ce9a8b7143dfbafa8f2427105b3316993f))

### Breaking Changes

- **cli**: An explicit empty string or zero in a CLI option is sent instead of being read as "not
  given": `--name ""`, `--queue ""`, `--answer-id 0`, `--version 0` reach the API. `forms surveys
  update --max-count 0` removes the response cap. `--limit 0` is a usage error (exit code 2); leave
  `--limit` out for the default cap.


## v0.53.1 (2026-10-03)

### Bug Fixes

- **mcp**: A server started with --tools or --exclude-tools accepts a connection
  ([#261](https://github.com/bim-ba/ycli/pull/261),
  [`c839442`](https://github.com/bim-ba/ycli/commit/c8394427eb2a410cd71261089c2d9d7ffcfd764d))

### Build System

- Re-lock uv.lock for 0.53.0
  ([`0de8d10`](https://github.com/bim-ba/ycli/commit/0de8d103e419a7d3808496205e6eb8931a1b9de4))

### Refactoring

- **cli**: Read the --profile option in one place ([#259](https://github.com/bim-ba/ycli/pull/259),
  [`98c08f8`](https://github.com/bim-ba/ycli/commit/98c08f849767f05ff54c4468362108b0d70c0953))

- **mcp**: A tool function is named like its tool ([#260](https://github.com/bim-ba/ycli/pull/260),
  [`9244e95`](https://github.com/bim-ba/ycli/commit/9244e955515e7b090841394e5e0e3323d6420eae))


## v0.53.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.52.0
  ([`98d0af5`](https://github.com/bim-ba/ycli/commit/98d0af5c1a205e4fc4bc966401ab475844d1520f))

### Features

- **sdk**: An SDK method is named like its MCP tool and CLI command
  ([#257](https://github.com/bim-ba/ycli/pull/257),
  [`e260df9`](https://github.com/bim-ba/ycli/commit/e260df9cd3334de1921862ff8a50a63ebb51aea0))

### Breaking Changes

- **sdk**: SDK methods are renamed, with no aliases: forms.answers.list_all -> forms.answers.list
  forms.conditions.hook_modify -> forms.conditions.hook_update forms.conditions.page_modify ->
  forms.conditions.page_update forms.conditions.question_modify -> forms.conditions.question_update
  forms.conditions.submit_modify -> forms.conditions.submit_update forms.hooks.modify ->
  forms.hooks.update forms.keysets.modify -> forms.keysets.update forms.questions.modify ->
  forms.questions.update forms.subscriptions.modify -> forms.subscriptions.update
  forms.surveys.modify -> forms.surveys.update tracker.autoactions.log_detail ->
  tracker.autoactions.logs_get tracker.autoactions.logs -> tracker.autoactions.logs_list
  tracker.boards.edit -> tracker.boards.update tracker.bulk.issues -> tracker.bulk.issues_list
  tracker.checklists.edit -> tracker.checklists.update tracker.columns.edit ->
  tracker.columns.update tracker.comments.edit -> tracker.comments.update tracker.components.edit ->
  tracker.components.update tracker.components.group_permissions ->
  tracker.components.group_permissions_get tracker.components.user_permissions ->
  tracker.components.user_permissions_get tracker.entities.attachment_download ->
  tracker.entities.attachments_download tracker.entities.bulk_status ->
  tracker.entities.bulk_status_get tracker.entities.checklists_edit ->
  tracker.entities.checklists_update tracker.entities.checklists_edit_item ->
  tracker.entities.checklists_update_item tracker.entities.comments_edit ->
  tracker.entities.comments_update tracker.entities.comments_relative ->
  tracker.entities.comments_relative_list tracker.entities.direct_permissions ->
  tracker.entities.direct_permissions_get tracker.entities.edit -> tracker.entities.update
  tracker.entities.history -> tracker.entities.events_list tracker.entities.permissions ->
  tracker.entities.permissions_get tracker.fields.category_edit -> tracker.fields.category_update
  tracker.fields.edit -> tracker.fields.update tracker.filters.edit -> tracker.filters.update
  tracker.issuetypes.edit -> tracker.issuetypes.update tracker.localfields.edit ->
  tracker.localfields.update tracker.macros.edit -> tracker.macros.update tracker.priorities.edit ->
  tracker.priorities.update tracker.projects.edit -> tracker.projects.update tracker.queues.fields
  -> tracker.queues.fields_list tracker.queues.group_permissions ->
  tracker.queues.group_permissions_get tracker.queues.tags -> tracker.queues.tags_list
  tracker.queues.user_permissions -> tracker.queues.user_permissions_get tracker.queues.version_edit
  -> tracker.queues.version_update tracker.queues.versions -> tracker.queues.versions_list
  tracker.resolutions.edit -> tracker.resolutions.update tracker.sprints.edit ->
  tracker.sprints.update tracker.statuses.edit -> tracker.statuses.update tracker.triggers.edit ->
  tracker.triggers.update tracker.triggers.webhook_log -> tracker.triggers.webhook_log_list
  tracker.workflows.edit -> tracker.workflows.update tracker.workflows.edit_action ->
  tracker.workflows.update_action tracker.worklog.edit -> tracker.worklog.update
  wiki.comments.thread -> wiki.comments.thread_list wiki.grids.add_columns -> wiki.grids.columns_add
  wiki.grids.add_rows -> wiki.grids.rows_add wiki.grids.move_columns -> wiki.grids.columns_move
  wiki.grids.move_rows -> wiki.grids.rows_move wiki.grids.remove_columns ->
  wiki.grids.columns_remove wiki.grids.remove_rows -> wiki.grids.rows_remove
  wiki.grids.suggest_column -> wiki.grids.columns_suggest wiki.grids.update_cells ->
  wiki.grids.cells_update wiki.grids.update_column -> wiki.grids.columns_update
  wiki.grids.update_row -> wiki.grids.rows_update wiki.pages.append_content -> wiki.pages.append
  wiki.pages.backlinks -> wiki.pages.backlinks_list wiki.pages.grids -> wiki.pages.grids_list
  wiki.pages.revisions -> wiki.pages.revisions_list forms.answers.list (one page) is removed;
  forms.answers.list is the former list_all. CLI: `tracker attachments thumbnail` -> `tracker
  attachments download-thumbnail`.


## v0.52.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.51.0
  ([`c92dc8d`](https://github.com/bim-ba/ycli/commit/c92dc8ded1d52d5e25fef2f82d78a15b3612e983))

### Features

- **auth**: Named profiles for several organizations
  ([#256](https://github.com/bim-ba/ycli/pull/256),
  [`0d44bbc`](https://github.com/bim-ba/ycli/commit/0d44bbc64d96adf67e560d659f4d30492e1a1e7e))


## v0.51.0 (2026-10-03)

### Bug Fixes

- **drift**: A body a reply also reads is still compared with the published one
  ([#255](https://github.com/bim-ba/ycli/pull/255),
  [`bd3e7fd`](https://github.com/bim-ba/ycli/commit/bd3e7fd44156ef09e6555afbb1da4bb64e00ecd1))

### Build System

- Re-lock uv.lock for 0.50.0
  ([`4095c28`](https://github.com/bim-ba/ycli/commit/4095c283cb46b65d75583f5a2f015d224a6d915b))

### Features

- **sdk**: A reply keeps the fields Yandex adds, a request body refuses unknown ones
  ([#255](https://github.com/bim-ba/ycli/pull/255),
  [`bd3e7fd`](https://github.com/bim-ba/ycli/commit/bd3e7fd44156ef09e6555afbb1da4bb64e00ecd1))


## v0.50.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.49.1
  ([`81ae0ae`](https://github.com/bim-ba/ycli/commit/81ae0aea92d373162478ff6d916d605b341cc6dc))

### Features

- **auth**: Sign in with a ready IAM token, in the CLI, the MCP server and the SDK
  ([#253](https://github.com/bim-ba/ycli/pull/253),
  [`3f3d552`](https://github.com/bim-ba/ycli/commit/3f3d5526bf29923a44596b8b3c3e0b7aa2228ca6))


## v0.49.1 (2026-10-03)

### Bug Fixes

- **sdk**: A service account's key is exchanged for a token on a real connection
  ([#250](https://github.com/bim-ba/ycli/pull/250),
  [`c2d8e3d`](https://github.com/bim-ba/ycli/commit/c2d8e3d42e371cc319a4f0a266fa91be84f1c4ab))

### Build System

- Re-lock uv.lock for 0.49.0
  ([`204eb4b`](https://github.com/bim-ba/ycli/commit/204eb4b6c3aa559b410be27ac7eb3883cd409fc0))


## v0.49.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.48.0
  ([`2b3a7f6`](https://github.com/bim-ba/ycli/commit/2b3a7f65a97f3f228c52a0e32f0d35d4b7a50c03))

### Chores

- Remove a Cloudflare CLI cache file committed by mistake
  ([#249](https://github.com/bim-ba/ycli/pull/249),
  [`3b12a02`](https://github.com/bim-ba/ycli/commit/3b12a02a94bed3d63094a8b88c13edfe0bd7feee))

### Documentation

- Three states per operation in the coverage tables
  ([#248](https://github.com/bim-ba/ycli/pull/248),
  [`07ef5e1`](https://github.com/bim-ba/ycli/commit/07ef5e165ac73e8a7e87c15e65cdb8116b636c3d))

### Features

- **sdk**: A request body is a model from the call down to the endpoint
  ([#252](https://github.com/bim-ba/ycli/pull/252),
  [`3a30706`](https://github.com/bim-ba/ycli/commit/3a307066f9983fa7f6358bdf50d3b21890fdbeb8))

### Breaking Changes

- **sdk**: SDK methods that took `body: dict` take the request model
  (`tracker.issues.create(IssueCreate(...))`, `wiki.pages.update(page_id, PageUpdate(...))`); build
  one with the model's constructor or `Model.model_validate(a_dict)`. `forms.notifications.list`
  takes a `NotificationFilter` instead of twelve keyword arguments.
  `tracker.issues.models.count_body` and `filter_body` return an `IssueSearch`. `AccessHolders` and
  `AccessPermissions` moved from `tracker.queues.models` to `tracker.models`, `FileOut` from
  `forms.files.models` to `forms.models`.


## v0.48.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.47.0
  ([`9f68db7`](https://github.com/bim-ba/ycli/commit/9f68db77097793c75328adf74a4bd600f643399e))

### Features

- **cli**: Ycli doctor says what is broken and how to fix it
  ([#247](https://github.com/bim-ba/ycli/pull/247),
  [`a3aeb66`](https://github.com/bim-ba/ycli/commit/a3aeb66b341191a51cf505615fb2152341f884c5))

- **cli**: Ycli doctor says when a newer release is out
  ([#247](https://github.com/bim-ba/ycli/pull/247),
  [`a3aeb66`](https://github.com/bim-ba/ycli/commit/a3aeb66b341191a51cf505615fb2152341f884c5))


## v0.47.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.46.1
  ([`1d35212`](https://github.com/bim-ba/ycli/commit/1d3521286ba027603083c7dec10f9cd59d3ce126))

### Features

- **tracker**: Send every published query parameter
  ([#246](https://github.com/bim-ba/ycli/pull/246),
  [`4b0f4ef`](https://github.com/bim-ba/ycli/commit/4b0f4ef49ac29d6bddb2d624697e4f03d8d5c0c3))


## v0.46.1 (2026-10-03)

### Bug Fixes

- **config**: An empty YCLI__ variable reads as unset, and the settings models share one base
  ([#245](https://github.com/bim-ba/ycli/pull/245),
  [`2968f9a`](https://github.com/bim-ba/ycli/commit/2968f9a5a197bed8c6fd10607b6732fcc69e7e40))

### Build System

- Re-lock uv.lock for 0.46.0
  ([`38394b2`](https://github.com/bim-ba/ycli/commit/38394b26914ef47b9c36582d02164fa9853c75c1))

### Chores

- The docs fetcher no longer re-implements cloning the Yandex Cloud docs
  ([#244](https://github.com/bim-ba/ycli/pull/244),
  [`f619483`](https://github.com/bim-ba/ycli/commit/f619483b73da8b69db231f0f2c79d6b2aee085ec))

### Refactoring

- Status codes by name, and the core's boolean arguments by keyword
  ([#243](https://github.com/bim-ba/ycli/pull/243),
  [`241a9c0`](https://github.com/bim-ba/ycli/commit/241a9c024f28a2b81ffdfc9d6ea6c37be5c3c00c))


## v0.46.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.45.0
  ([`4e6bbb8`](https://github.com/bim-ba/ycli/commit/4e6bbb88f41d73a443a1e333832c17c54f238942))

### Documentation

- A README of short examples that link to the site ([#241](https://github.com/bim-ba/ycli/pull/241),
  [`f1744e4`](https://github.com/bim-ba/ycli/commit/f1744e4744c6c91b0a0d4752082b0c7a604ff120))

### Features

- **forms**: Match the published API, and say which fields it ignores
  ([#242](https://github.com/bim-ba/ycli/pull/242),
  [`2bfc5c8`](https://github.com/bim-ba/ycli/commit/2bfc5c86fb1c8ee75f661630fc37862116274b0c))

### Breaking Changes

- **forms**: Models shared by Forms resources moved to `ycli.yandex.forms.models`: `Condition`,
  `ConditionItem` and the `ConditionOperatorType`, `ConditionItemKind`, `ConditionComparison`
  aliases (were in `forms.questions.models`), `ConditionsResponse` (was in
  `forms.conditions.models`), `UserIdentity` and `UserRef` (were in `forms.access.models`).
  `SubmitResult` loses `results`, `scores` and `total_scores`, which the API never sends: a quiz
  result is in `quiz_result`. `Answer.data` is a list or, in the raw format, an object.


## v0.45.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.44.0
  ([`6976c32`](https://github.com/bim-ba/ycli/commit/6976c320945c370b50f6118c00bd012e726a496e))

### Features

- **cli**: Jq is an extra, so a plain install no longer needs a compiled package
  ([#239](https://github.com/bim-ba/ycli/pull/239),
  [`826a8c1`](https://github.com/bim-ba/ycli/commit/826a8c1502dd5c8cd6416a9b4cab1af4968636b0))

### Breaking Changes

- **cli**: Pip install yandex-cli no longer installs jq, so --jq exits with code 2 until the extra
  is installed: uv tool install 'yandex-cli[jq]' (or 'yandex-cli[mcp,jq]' with the MCP server).


## v0.44.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.43.0
  ([`1481935`](https://github.com/bim-ba/ycli/commit/1481935a33444e7ba45bbbcb3fa59105c27e345f))

### Features

- **config**: The page cap and the longest Retry-After are settings
  ([#237](https://github.com/bim-ba/ycli/pull/237),
  [`4ec54b4`](https://github.com/bim-ba/ycli/commit/4ec54b456a32b39eab3283e153c438d92704f523))

### Breaking Changes

- **config**: Ycli.yandex.core.session.DEFAULT_MAX_PAGES and MAX_RETRY_AFTER_SECONDS are removed;
  read HTTPConfig().max_pages and .max_retry_after_seconds. SyncSession and AsyncSession take
  http=HTTPConfig(...) instead of retries=, and iterate() no longer takes max_pages=: set it on the
  HTTPConfig the session is built with.


## v0.43.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.42.0
  ([`f53e4a0`](https://github.com/bim-ba/ycli/commit/f53e4a03ff7c926f05f4c8e7c82643c184e68a45))

### Documentation

- The site lives at ycli.savaznatnov.dev ([#238](https://github.com/bim-ba/ycli/pull/238),
  [`bfeeda6`](https://github.com/bim-ba/ycli/commit/bfeeda69fa4e8be5896557bb3e756ea364b86560))

### Refactoring

- **sdk**: Delete what nothing uses ([#236](https://github.com/bim-ba/ycli/pull/236),
  [`ce474d6`](https://github.com/bim-ba/ycli/commit/ce474d6110dc0a13e72576bca51cf5071b874484))

### Breaking Changes

- **sdk**: Service.cli_app() is removed with no replacement; resolve Service.cli with
  pkgutil.resolve_name.


## v0.42.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.41.0
  ([`fe95644`](https://github.com/bim-ba/ycli/commit/fe95644710fe9f078859e62a9f930c7bb2ba8a8b))

### Chores

- Conventions say what the code does, and the scaffold passes the gates as generated
  ([#228](https://github.com/bim-ba/ycli/pull/228),
  [`32456f8`](https://github.com/bim-ba/ycli/commit/32456f8a70a469226836f56c06810c610fc0f8af))

### Documentation

- Say when a field with a set of values is a str and when a Literal
  ([#231](https://github.com/bim-ba/ycli/pull/231),
  [`52c1cc9`](https://github.com/bim-ba/ycli/commit/52c1cc9b4542769d48db9df24a9d9a315fc762b0))

### Features

- **wiki**: Send every published query parameter and read every published field
  ([#231](https://github.com/bim-ba/ycli/pull/231),
  [`52c1cc9`](https://github.com/bim-ba/ycli/commit/52c1cc9b4542769d48db9df24a9d9a315fc762b0))

### Testing

- Every convention has a check that was seen failing, or is gone
  ([#235](https://github.com/bim-ba/ycli/pull/235),
  [`e55697a`](https://github.com/bim-ba/ycli/commit/e55697a4a8c4e74f660c205bcebdc157516c23ff))


## v0.41.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.40.0
  ([`10d6a41`](https://github.com/bim-ba/ycli/commit/10d6a4183d81eee0b383b2a9cc9ff01f4d9e542d))

### Features

- **cli**: A renamed command no longer answers to its old name
  ([#226](https://github.com/bim-ba/ycli/pull/226),
  [`b704c54`](https://github.com/bim-ba/ycli/commit/b704c548e6b2bd75f76324b53ba6cbf49bfc9b73))

### Breaking Changes

- **cli**: The old command names stop working; use the new ones: `forms answers integrations` →
  `forms answers integrations-list`; `forms conditions hook modify` → `forms conditions hook
  update`; `forms conditions page modify` → `forms conditions page update`; `forms conditions
  question modify` → `forms conditions question update`; `forms conditions submit modify` → `forms
  conditions submit update`; `forms hooks modify` → `forms hooks update`; `forms keysets modify` →
  `forms keysets update`; `forms notifications errors` → `forms notifications errors-list`; `forms
  notifications status` → `forms notifications status-get`; `forms questions modify` → `forms
  questions update`; `forms subscriptions modify` → `forms subscriptions update`; `forms surveys
  modify` → `forms surveys update`; `tracker autoactions log-detail` → `tracker autoactions
  logs-get`; `tracker autoactions logs` → `tracker autoactions logs-list`; `tracker boards edit` →
  `tracker boards update`; `tracker bulk issues` → `tracker bulk issues-list`; `tracker checklists
  add` → `tracker checklists create`; `tracker checklists edit` → `tracker checklists update`;
  `tracker columns edit` → `tracker columns update`; `tracker comments edit` → `tracker comments
  update`; `tracker components edit` → `tracker components update`; `tracker components
  group-permissions` → `tracker components group-permissions-get`; `tracker components
  user-permissions` → `tracker components user-permissions-get`; `tracker dashboards add-widget
  cycletime` → `tracker dashboards add-cycle-time-widget`; `tracker entities bulk` → `tracker
  entities bulk-update`; `tracker entities bulk-status` → `tracker entities bulk-status-get`;
  `tracker entities checklists edit` → `tracker entities checklists update`; `tracker entities
  checklists edit-item` → `tracker entities checklists update-item`; `tracker entities comments
  edit` → `tracker entities comments update`; `tracker entities direct-permissions` → `tracker
  entities direct-permissions-get`; `tracker entities edit` → `tracker entities update`; `tracker
  entities history` → `tracker entities events-list`; `tracker entities permissions` → `tracker
  entities permissions-get`; `tracker fields category-edit` → `tracker fields category-update`;
  `tracker fields edit` → `tracker fields update`; `tracker filters edit` → `tracker filters
  update`; `tracker issuetypes edit` → `tracker issuetypes update`; `tracker localfields edit` →
  `tracker localfields update`; `tracker macros edit` → `tracker macros update`; `tracker priorities
  edit` → `tracker priorities update`; `tracker projects edit` → `tracker projects update`; `tracker
  queues fields` → `tracker queues fields-list`; `tracker queues group-permissions` → `tracker
  queues group-permissions-get`; `tracker queues permissions` → `tracker queues set-permissions`;
  `tracker queues tags` → `tracker queues tags-list`; `tracker queues user-permissions` → `tracker
  queues user-permissions-get`; `tracker queues version-edit` → `tracker queues version-update`;
  `tracker queues versions` → `tracker queues versions-list`; `tracker resolutions edit` → `tracker
  resolutions update`; `tracker sprints edit` → `tracker sprints update`; `tracker statuses edit` →
  `tracker statuses update`; `tracker triggers edit` → `tracker triggers update`; `tracker triggers
  webhook-log` → `tracker triggers webhook-log-list`; `tracker workflows edit` → `tracker workflows
  update`; `tracker workflows edit-action` → `tracker workflows update-action`; `tracker worklog
  add` → `tracker worklog create`; `tracker worklog edit` → `tracker worklog update`; `wiki comments
  thread` → `wiki comments thread-list`; `wiki operations clone` → `wiki operations clone-get`;
  `wiki operations gridclone` → `wiki operations gridclone-get`; `wiki pages backlinks` → `wiki
  pages backlinks-list`; `wiki pages grids` → `wiki pages grids-list`; `wiki pages revisions` →
  `wiki pages revisions-list`.


## v0.40.0 (2026-10-03)

### Build System

- PyPI topic classifiers for what ycli is used for ([#224](https://github.com/bim-ba/ycli/pull/224),
  [`82f867f`](https://github.com/bim-ba/ycli/commit/82f867fcca3b18ff697f95d93dc58096de3eb67a))

- Re-lock uv.lock for 0.39.0
  ([`eac4f59`](https://github.com/bim-ba/ycli/commit/eac4f59d6cd62de4f87ec7d7c5e43a517a4fc6e8))

### Documentation

- A comparison page, ycli next to Yandex's own servers and the community ones
  ([#223](https://github.com/bim-ba/ycli/pull/223),
  [`d976f8a`](https://github.com/bim-ba/ycli/commit/d976f8ae73cb2d94775f48886c9b0d53ae1ab98d))

### Features

- **sdk**: One generic list in place of the per-resource list classes
  ([#225](https://github.com/bim-ba/ycli/pull/225),
  [`469eead`](https://github.com/bim-ba/ycli/commit/469eeadaa22ef9b8e3418052fca108efff0e1a74))

### Breaking Changes

- **sdk**: The per-resource list classes are gone; use `ItemList[X]` from `ycli.yandex.models` with
  the item class instead of `XList` (`ItemList[Board]` for `BoardList`, `ItemList[Queue]` for
  `QueueList`, and so on for every `…List` model of Tracker, Wiki and Forms). A list can no longer
  be built without an argument: `SurveyList()` becomes `ItemList[Survey]([])`.


## v0.39.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.38.0
  ([`794dc0a`](https://github.com/bim-ba/ycli/commit/794dc0a5d4c4868139f5d4aceb8f187e9d2bcb2c))

### Documentation

- Llms.txt, a description and a preview card for every page
  ([#220](https://github.com/bim-ba/ycli/pull/220),
  [`c238ba8`](https://github.com/bim-ba/ycli/commit/c238ba8a5a816897a7d615a9fd25b19d4dca2696))

- Serve llms.txt, describe every page, and keep the theme's copy button
  ([#220](https://github.com/bim-ba/ycli/pull/220),
  [`c238ba8`](https://github.com/bim-ba/ycli/commit/c238ba8a5a816897a7d615a9fd25b19d4dca2696))

- Social cards for every page, with the card fonts cached in CI
  ([#220](https://github.com/bim-ba/ycli/pull/220),
  [`c238ba8`](https://github.com/bim-ba/ycli/commit/c238ba8a5a816897a7d615a9fd25b19d4dca2696))

### Features

- **sdk**: One generic page for the Wiki cursor listings
  ([#222](https://github.com/bim-ba/ycli/pull/222),
  [`b6800dc`](https://github.com/bim-ba/ycli/commit/b6800dc777650a7b1bc2b8d16ef7893c381e73aa))

### Breaking Changes

- **sdk**: These Wiki model names are gone; use `ycli.yandex.wiki.models.CursorPage` with the item
  type instead.


## v0.38.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.37.0
  ([`c220a75`](https://github.com/bim-ba/ycli/commit/c220a75963e62b42a16204e56730b578dc32cc6b))

### Continuous Integration

- Check the theme partial with --frozen, so a release can publish the docs
  ([#219](https://github.com/bim-ba/ycli/pull/219),
  [`963a99a`](https://github.com/bim-ba/ycli/commit/963a99ac567ccace1242851970ec618f9c5b57b1))

- Fail the docs build when the overridden theme partial changes upstream
  ([#216](https://github.com/bim-ba/ycli/pull/216),
  [`0a6014f`](https://github.com/bim-ba/ycli/commit/0a6014f2b4fd53f7b8063d2390cc4c22ad79cc1c))

### Documentation

- A landing page that gets to a working call, and no edit link on generated pages
  ([#216](https://github.com/bim-ba/ycli/pull/216),
  [`0a6014f`](https://github.com/bim-ba/ycli/commit/0a6014f2b4fd53f7b8063d2390cc4c22ad79cc1c))

- A landing page with a pitch, the smallest example and cards; no edit link on generated pages
  ([#216](https://github.com/bim-ba/ycli/pull/216),
  [`0a6014f`](https://github.com/bim-ba/ycli/commit/0a6014f2b4fd53f7b8063d2390cc4c22ad79cc1c))

- An animated terminal on the home page, and the language switch keeps the page
  ([#218](https://github.com/bim-ba/ycli/pull/218),
  [`fc606d1`](https://github.com/bim-ba/ycli/commit/fc606d171e9a56d8c53e0979d245b82217db13f0))

- Give the same-page check a timeout ([#218](https://github.com/bim-ba/ycli/pull/218),
  [`fc606d1`](https://github.com/bim-ba/ycli/commit/fc606d171e9a56d8c53e0979d245b82217db13f0))

### Features

- **sdk**: One class per concept, and no old names ([#217](https://github.com/bim-ba/ycli/pull/217),
  [`b882c70`](https://github.com/bim-ba/ycli/commit/b882c70019b5d2d3ab2d7c5ac679c0df64442ab1))

### Breaking Changes

- **sdk**: These model names are gone; import the class on the right instead.


## v0.37.0 (2026-10-03)

### Build System

- Re-lock uv.lock for 0.36.3
  ([`93848e5`](https://github.com/bim-ba/ycli/commit/93848e538b635540a8a86bacbedc99b7f16c85c7))

### Chores

- Drop the Codex converter marker nothing reads any more
  ([#194](https://github.com/bim-ba/ycli/pull/194),
  [`e019f2f`](https://github.com/bim-ba/ycli/commit/e019f2fd5c0d7fd5af65b9e1a152927c98bd7b1b))

### Continuous Integration

- Build the docs site at a release tag, whose lockfile lags the version
  ([#184](https://github.com/bim-ba/ycli/pull/184),
  [`4573105`](https://github.com/bim-ba/ycli/commit/45731057c1692e6c9eb86e770345772fff69393c))

### Documentation

- Add a Compose file for self-hosting, included from the page and checked in CI
  ([#214](https://github.com/bim-ba/ycli/pull/214),
  [`fb13cff`](https://github.com/bim-ba/ycli/commit/fb13cffdcc06d23330349b3e0e85fd408331bdfe))

- Add a page on using ycli in CI, and shell completion
  ([#214](https://github.com/bim-ba/ycli/pull/214),
  [`fb13cff`](https://github.com/bim-ba/ycli/commit/fb13cffdcc06d23330349b3e0e85fd408331bdfe))

- An install page a newcomer can follow, CI and Compose guides
  ([#214](https://github.com/bim-ba/ycli/pull/214),
  [`fb13cff`](https://github.com/bim-ba/ycli/commit/fb13cffdcc06d23330349b3e0e85fd408331bdfe))

- Compare request bodies with the published API ([#195](https://github.com/bim-ba/ycli/pull/195),
  [`6a0bf39`](https://github.com/bim-ba/ycli/commit/6a0bf3991e02d8d262e8785f88bb9f50e83fd4ef))

- Describe the image as ycli itself, and add the Glama maintainer file
  ([#214](https://github.com/bim-ba/ycli/pull/214),
  [`fb13cff`](https://github.com/bim-ba/ycli/commit/fb13cffdcc06d23330349b3e0e85fd408331bdfe))

- Let the release stamp the version the copy-paste examples pin
  ([#214](https://github.com/bim-ba/ycli/pull/214),
  [`fb13cff`](https://github.com/bim-ba/ycli/commit/fb13cffdcc06d23330349b3e0e85fd408331bdfe))

- Publish an OpenAPI document per service, derived from ycli
  ([#185](https://github.com/bim-ba/ycli/pull/185),
  [`f4e1e6c`](https://github.com/bim-ba/ycli/commit/f4e1e6c36e551f8b2f84e62f74bd070bb322048b))

- Rewrite the client install page: one order per client, one-click links, more clients
  ([#214](https://github.com/bim-ba/ycli/pull/214),
  [`fb13cff`](https://github.com/bim-ba/ycli/commit/fb13cffdcc06d23330349b3e0e85fd408331bdfe))

- Show one operation as CLI, MCP and SDK tabs, generated from the contract cases
  ([#215](https://github.com/bim-ba/ycli/pull/215),
  [`f171449`](https://github.com/bim-ba/ycli/commit/f17144985bb6e2d2f3ad6ea4a74c61ec635ba691))

- Stop the Claude Code command from writing the token into its config
  ([#214](https://github.com/bim-ba/ycli/pull/214),
  [`fb13cff`](https://github.com/bim-ba/ycli/commit/fb13cffdcc06d23330349b3e0e85fd408331bdfe))

- Type the OpenAPI parameters and name its schemas by resource
  ([#200](https://github.com/bim-ba/ycli/pull/200),
  [`b0f16f9`](https://github.com/bim-ba/ycli/commit/b0f16f9e1c6f8ddbb6625ba92a80fae99eb58a41))

- **site**: Turn on the navigation, code and tab features the theme already ships
  ([#204](https://github.com/bim-ba/ycli/pull/204),
  [`7357535`](https://github.com/bim-ba/ycli/commit/7357535b4083844d0842984526e25621a39fe668))

### Features

- **sdk**: Address the review of the shared models ([#213](https://github.com/bim-ba/ycli/pull/213),
  [`c1d48b0`](https://github.com/bim-ba/ycli/commit/c1d48b0ce5ba28df82c9bbca6f49000d7350324b))

- **sdk**: One shared class for each shape several resources read
  ([#213](https://github.com/bim-ba/ycli/pull/213),
  [`c1d48b0`](https://github.com/bim-ba/ycli/commit/c1d48b0ce5ba28df82c9bbca6f49000d7350324b))

### Refactoring

- **core**: Carry the endpoint on its request instead of only its effect
  ([#198](https://github.com/bim-ba/ycli/pull/198),
  [`cc6458f`](https://github.com/bim-ba/ycli/commit/cc6458f757ecfac1ecb13d3cea796f0eb3d8e312))

- **core**: Say that every page of a listing carries it
  ([#198](https://github.com/bim-ba/ycli/pull/198),
  [`cc6458f`](https://github.com/bim-ba/ycli/commit/cc6458f757ecfac1ecb13d3cea796f0eb3d8e312))


## v0.36.3 (2026-10-03)

### Bug Fixes

- Print API text verbatim in pretty output and close three smaller leaks
  ([#180](https://github.com/bim-ba/ycli/pull/180),
  [`6065d1e`](https://github.com/bim-ba/ycli/commit/6065d1e1a2aea73226db565e195e5520a0cd65aa))

### Build System

- Re-lock uv.lock for 0.36.2
  ([`fb05456`](https://github.com/bim-ba/ycli/commit/fb05456c31c65bd08d806aa70a5993146d12d2a2))

### Chores

- Correct stale tooling hints and tighten two workflows
  ([#183](https://github.com/bim-ba/ycli/pull/183),
  [`e81f056`](https://github.com/bim-ba/ycli/commit/e81f056b70d386e477eedd12933a61eba6f05e94))

### Continuous Integration

- Compare ycli with the API Yandex publishes, in README and weekly
  ([#181](https://github.com/bim-ba/ycli/pull/181),
  [`9777230`](https://github.com/bim-ba/ycli/commit/97772308617ad6de0f0692b8a9a8d290187b0ae7))

- Run pydoclint in its own environment so main stays green
  ([#177](https://github.com/bim-ba/ycli/pull/177),
  [`037fe51`](https://github.com/bim-ba/ycli/commit/037fe518adde3b9155cd5d55f3555c2b68c594df))

### Documentation

- Add the Russian README and documentation site ([#176](https://github.com/bim-ba/ycli/pull/176),
  [`48b3465`](https://github.com/bim-ba/ycli/commit/48b34659285c7f2ff6f18f763cf929dd80811ca9))

- Enforce a Google-style docstring contract and run every example
  ([#174](https://github.com/bim-ba/ycli/pull/174),
  [`0173b4a`](https://github.com/bim-ba/ycli/commit/0173b4a4f6480b872f5271125570a4ce5cd904da))

- Keep the key-set constraints in the CLI listing and correct four Returns texts
  ([#174](https://github.com/bim-ba/ycli/pull/174),
  [`0173b4a`](https://github.com/bim-ba/ycli/commit/0173b4a4f6480b872f5271125570a4ce5cd904da))

- Note the doctest, docs-site and pydoclint conventions for agents
  ([#179](https://github.com/bim-ba/ycli/pull/179),
  [`e8f0ac9`](https://github.com/bim-ba/ycli/commit/e8f0ac934e92c2276699cb33c3077e4ec5a215da))

- Publish a Diátaxis documentation site built with Zensical
  ([#175](https://github.com/bim-ba/ycli/pull/175),
  [`8e4f709`](https://github.com/bim-ba/ycli/commit/8e4f709afe551e89b1dc3b9f97f6f7b32721207e))

- **readme**: Fix the DeepWiki badge, link the Yandex auth docs, drop the stale layout tree
  ([#173](https://github.com/bim-ba/ycli/pull/173),
  [`d03aa14`](https://github.com/bim-ba/ycli/commit/d03aa1416f6fbbba0a572f7ac5a41faba282a3f8))

- **readme**: Fix the DeepWiki badge, link the Yandex docs, preview coverage as an SVG
  ([#173](https://github.com/bim-ba/ycli/pull/173),
  [`d03aa14`](https://github.com/bim-ba/ycli/commit/d03aa1416f6fbbba0a572f7ac5a41faba282a3f8))

- **readme**: Preview coverage as an SVG and fold each service's tables
  ([#173](https://github.com/bim-ba/ycli/pull/173),
  [`d03aa14`](https://github.com/bim-ba/ycli/commit/d03aa1416f6fbbba0a572f7ac5a41faba282a3f8))

### Testing

- Load the contract cases on the first doctest only, so the live e2e run needs no mcp extra
  ([#174](https://github.com/bim-ba/ycli/pull/174),
  [`0173b4a`](https://github.com/bim-ba/ycli/commit/0173b4a4f6480b872f5271125570a4ce5cd904da))

- **e2e**: Confirm deletes in the live runner ([#178](https://github.com/bim-ba/ycli/pull/178),
  [`3dd6716`](https://github.com/bim-ba/ycli/commit/3dd6716f66dd9ee34fb6230df764366d092fbfcb))


## v0.36.2 (2026-10-02)

### Bug Fixes

- **docker**: Build the image with the frozen lock so a release tag builds
  ([#172](https://github.com/bim-ba/ycli/pull/172),
  [`c34eae4`](https://github.com/bim-ba/ycli/commit/c34eae4b356d273c2bfd63f8ce1d4564285b33a5))

### Build System

- Re-lock uv.lock for 0.36.1
  ([`2ec28aa`](https://github.com/bim-ba/ycli/commit/2ec28aa865774337b2ce5dd29eb049b292fc23e1))


## v0.36.1 (2026-10-02)

### Bug Fixes

- Close the gaps the E3 review found across #164-#170
  ([#171](https://github.com/bim-ba/ycli/pull/171),
  [`54eea7b`](https://github.com/bim-ba/ycli/commit/54eea7b850f32e251916d8324dbd014849ed01fd))

- Close the gaps the E3 review found across the milestone
  ([#171](https://github.com/bim-ba/ycli/pull/171),
  [`54eea7b`](https://github.com/bim-ba/ycli/commit/54eea7b850f32e251916d8324dbd014849ed01fd))

### Build System

- Re-lock uv.lock for 0.36.0
  ([`834801d`](https://github.com/bim-ba/ycli/commit/834801d7e596d6899587c56e922be0b90e715fd4))

### Documentation

- **drift-log**: A PR's CI can start between a release and its re-lock
  ([#171](https://github.com/bim-ba/ycli/pull/171),
  [`54eea7b`](https://github.com/bim-ba/ycli/commit/54eea7b850f32e251916d8324dbd014849ed01fd))


## v0.36.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.35.0
  ([`015c3c8`](https://github.com/bim-ba/ycli/commit/015c3c8dddc874984c7a78fc2d43bf380f433a22))

### Documentation

- The MCP name rule is ARCH-1's name parity, not a verb map
  ([#170](https://github.com/bim-ba/ycli/pull/170),
  [`0365fd0`](https://github.com/bim-ba/ycli/commit/0365fd0fa6be06c99976a1e2f6f4130bdb0fb26c))

### Features

- **cli,mcp**: One verb per action, and one name for a command and its MCP tool
  ([#170](https://github.com/bim-ba/ycli/pull/170),
  [`0365fd0`](https://github.com/bim-ba/ycli/commit/0365fd0fa6be06c99976a1e2f6f4130bdb0fb26c))


## v0.35.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.34.0
  ([`4b8ea39`](https://github.com/bim-ba/ycli/commit/4b8ea39b2e8f5ed19af1e3c13c702a066657fe4d))

### Features

- **api**: --paginate follows Tracker's Link rel=next
  ([#169](https://github.com/bim-ba/ycli/pull/169),
  [`6ab149e`](https://github.com/bim-ba/ycli/commit/6ab149eb641e82093a84685385c488470ea7b2a6))

- **cli**: Add `ycli api`, a raw passthrough for endpoints ycli has not wrapped
  ([#169](https://github.com/bim-ba/ycli/pull/169),
  [`6ab149e`](https://github.com/bim-ba/ycli/commit/6ab149eb641e82093a84685385c488470ea7b2a6))

- **cli**: Ycli api — a raw passthrough for endpoints ycli has not wrapped
  ([#169](https://github.com/bim-ba/ycli/pull/169),
  [`6ab149e`](https://github.com/bim-ba/ycli/commit/6ab149eb641e82093a84685385c488470ea7b2a6))


## v0.34.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.33.0
  ([`08f8d4c`](https://github.com/bim-ba/ycli/commit/08f8d4c0d0f03d66c0f8d77f3c94116f3b0deaa9))

### Features

- **mcp**: Serve MCP over HTTP, signing every caller in through Yandex ID (#108)
  ([#168](https://github.com/bim-ba/ycli/pull/168),
  [`1c1b1ab`](https://github.com/bim-ba/ycli/commit/1c1b1ab9af7fbc69faf40b03174f242fb42ad2ad))


## v0.33.0 (2026-10-02)

### Bug Fixes

- **mcpb**: Start the bundle through python -m ycli.mcp
  ([#167](https://github.com/bim-ba/ycli/pull/167),
  [`5dfbedf`](https://github.com/bim-ba/ycli/commit/5dfbedf074f121b7d4f85a03e17ba3e5a892f907))

### Build System

- Re-lock uv.lock for 0.32.0
  ([`f7baded`](https://github.com/bim-ba/ycli/commit/f7baded87b060c1eaf8e1c8e6a8df1f21f911ea6))

### Features

- **mcp**: Toolsets, a curated core profile and a 74% lighter tools/list
  ([#167](https://github.com/bim-ba/ycli/pull/167),
  [`5dfbedf`](https://github.com/bim-ba/ycli/commit/5dfbedf074f121b7d4f85a03e17ba3e5a892f907))

- **mcp**: Toolsets, a curated core profile and a lighter tools/list
  ([#167](https://github.com/bim-ba/ycli/pull/167),
  [`5dfbedf`](https://github.com/bim-ba/ycli/commit/5dfbedf074f121b7d4f85a03e17ba3e5a892f907))


## v0.32.0 (2026-10-02)

### Bug Fixes

- **cli**: Public exit for a refused delete, one context for commands that declare their own
  ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

### Build System

- Re-lock uv.lock for 0.31.0
  ([`c9b126f`](https://github.com/bim-ba/ycli/commit/c9b126f3d888f6291a2d18185b220df5308ce95d))

### Features

- **cli**: --dry-run prints the request a write would send
  ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

- **cli**: --jq filters a command's JSON result ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

- **cli**: Accept the global options after the subcommand
  ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

- **cli**: Ask before an operation that deletes data; --yes skips it
  ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

- **cli**: Exit codes by error kind ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

- **cli**: Exit codes by error kind, --jq, delete confirmations and --dry-run
  ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

### Testing

- Plain help output under GitHub Actions for every test
  ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))

- **cli**: Read the leaf's declared options, not its colour-coded help
  ([#166](https://github.com/bim-ba/ycli/pull/166),
  [`ef71747`](https://github.com/bim-ba/ycli/commit/ef71747d10ce99d48092c2c9be608d26ba2cbb98))


## v0.31.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.30.0
  ([`e1f657e`](https://github.com/bim-ba/ycli/commit/e1f657e5e46e7175284ae966e1b0edaf604cb292))

### Features

- **auth**: Identity from Yandex ID, organization from API 360, probes from the registry (#145)
  ([#165](https://github.com/bim-ba/ycli/pull/165),
  [`0bb7e7e`](https://github.com/bim-ba/ycli/commit/0bb7e7e7089d7dc324bfcb3c9fb35c0e22f0f9cf))

### Breaking Changes

- **auth**: The `auth status` / `status_get` report changes shape: the per-service `account` and the
  top-level `organization_id` are gone; the report is now {configured, identity, organization {id,
  name, detail}, services [{service, valid, detail}]}.


## v0.30.0 (2026-10-02)

### Bug Fixes

- Drop the dev-only skill mirrors instead of duplicating the commands
  ([#164](https://github.com/bim-ba/ycli/pull/164),
  [`431a9e0`](https://github.com/bim-ba/ycli/commit/431a9e0ecfd9b0021cde9c71ee56a4df0136d382))

- Keep the dev-only skills out of `npx skills add bim-ba/ycli`
  ([#164](https://github.com/bim-ba/ycli/pull/164),
  [`431a9e0`](https://github.com/bim-ba/ycli/commit/431a9e0ecfd9b0021cde9c71ee56a4df0136d382))

### Build System

- Re-lock uv.lock for 0.29.0
  ([`7033ee4`](https://github.com/bim-ba/ycli/commit/7033ee4c34a9063f09f903356b3db643d626fa17))

### Documentation

- The repository ships only the four user skills ([#164](https://github.com/bim-ba/ycli/pull/164),
  [`431a9e0`](https://github.com/bim-ba/ycli/commit/431a9e0ecfd9b0021cde9c71ee56a4df0136d382))

### Features

- Publish every release to the MCP Registry, GHCR and as a Claude Desktop bundle
  ([#164](https://github.com/bim-ba/ycli/pull/164),
  [`431a9e0`](https://github.com/bim-ba/ycli/commit/431a9e0ecfd9b0021cde9c71ee56a4df0136d382))

- Ship every release to the MCP Registry, GHCR and as a .mcpb bundle
  ([#164](https://github.com/bim-ba/ycli/pull/164),
  [`431a9e0`](https://github.com/bim-ba/ycli/commit/431a9e0ecfd9b0021cde9c71ee56a4df0136d382))


## v0.29.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.28.1
  ([`e8abffb`](https://github.com/bim-ba/ycli/commit/e8abffb46c88a493ad9397bc83d868e3ba8d62f0))

### Features

- **wiki**: Wrap the nine operations the live OpenAPI has and the docs do not (#150)
  ([#163](https://github.com/bim-ba/ycli/pull/163),
  [`bed0630`](https://github.com/bim-ba/ycli/commit/bed0630860fd107de4ed8725f24a118bc62c2124))


## v0.28.1 (2026-10-02)

### Bug Fixes

- Read Forms validation errors as text, and refuse workflow edits Tracker rejects
  ([#158](https://github.com/bim-ba/ycli/pull/158),
  [`fa8762c`](https://github.com/bim-ba/ycli/commit/fa8762c12d8a31f18781a9bbe70712df15b79a6a))

### Build System

- Re-lock uv.lock for 0.28.0
  ([`e43fcf8`](https://github.com/bim-ba/ycli/commit/e43fcf863338bade75c6881be40b613ef36ed617))


## v0.28.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.27.0
  ([`405dbda`](https://github.com/bim-ba/ycli/commit/405dbda385cf363dfc7280a942e03e03fadaa7b4))

### Features

- **tracker**: Cover every documented Tracker endpoint
  ([#154](https://github.com/bim-ba/ycli/pull/154),
  [`f8fa7f6`](https://github.com/bim-ba/ycli/commit/f8fa7f69ae690e76dc0e350c690472273ea1bd90))


## v0.27.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.26.0
  ([`b7a06ad`](https://github.com/bim-ba/ycli/commit/b7a06ad32115918017b041b595b0857da52edca8))

### Features

- **wiki**: Wrap full-text search, page access and the server comment thread
  ([#153](https://github.com/bim-ba/ycli/pull/153),
  [`a519866`](https://github.com/bim-ba/ycli/commit/a51986603a9009732d685364342d18147330fe3a))

### Refactoring

- **wiki**: Cap the server thread with HTTPConfig.cap
  ([#153](https://github.com/bim-ba/ycli/pull/153),
  [`a519866`](https://github.com/bim-ba/ycli/commit/a51986603a9009732d685364342d18147330fe3a))


## v0.26.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.25.0
  ([`27ccced`](https://github.com/bim-ba/ycli/commit/27cccedd5a14e904e647d496d136480f3ae80687))

### Documentation

- **forms**: Teach the forms skill the integrations, conditions, access, history and notification
  commands ([#152](https://github.com/bim-ba/ycli/pull/152),
  [`6c91611`](https://github.com/bim-ba/ycli/commit/6c916110c64c8592250ed85506dec52e362c9338))

### Features

- **forms**: Cover every documented Forms endpoint ([#152](https://github.com/bim-ba/ycli/pull/152),
  [`6c91611`](https://github.com/bim-ba/ycli/commit/6c916110c64c8592250ed85506dec52e362c9338))

- **forms**: Display conditions of questions, pages, the submit button and hooks
  ([#152](https://github.com/bim-ba/ycli/pull/152),
  [`6c91611`](https://github.com/bim-ba/ycli/commit/6c916110c64c8592250ed85506dec52e362c9338))

- **forms**: Integration groups, their integrations and the variable catalogue
  ([#152](https://github.com/bim-ba/ycli/pull/152),
  [`6c91611`](https://github.com/bim-ba/ycli/commit/6c916110c64c8592250ed85506dec52e362c9338))

- **forms**: Integration runs (notifications), answer integrations, answer delete and restore, image
  clone ([#152](https://github.com/bim-ba/ycli/pull/152),
  [`6c91611`](https://github.com/bim-ba/ycli/commit/6c916110c64c8592250ed85506dec52e362c9338))

- **forms**: Survey access and the change log ([#152](https://github.com/bim-ba/ycli/pull/152),
  [`6c91611`](https://github.com/bim-ba/ycli/commit/6c916110c64c8592250ed85506dec52e362c9338))

### Refactoring

- **forms**: Cap the new listings with HTTPConfig.cap
  ([#152](https://github.com/bim-ba/ycli/pull/152),
  [`6c91611`](https://github.com/bim-ba/ycli/commit/6c916110c64c8592250ed85506dec52e362c9338))


## v0.25.0 (2026-10-02)

### Build System

- Fetch vendored docs with httpx2 instead of requests
  ([#151](https://github.com/bim-ba/ycli/pull/151),
  [`6958358`](https://github.com/bim-ba/ycli/commit/695835886ad3103472b463dab69d6f1d3f0af0d7))

- Re-lock uv.lock for 0.24.3
  ([`a8088ce`](https://github.com/bim-ba/ycli/commit/a8088ce668c19b80dd4ff2431bca947c133cb1d5))

### Refactoring

- Drop uplink, requests and the legacy transport ([#151](https://github.com/bim-ba/ycli/pull/151),
  [`6958358`](https://github.com/bim-ba/ycli/commit/695835886ad3103472b463dab69d6f1d3f0af0d7))

- **arch**: Retire the uplink-era ARCH-3 verb maps and resource ratchet
  ([#149](https://github.com/bim-ba/ycli/pull/149),
  [`c7f82d1`](https://github.com/bim-ba/ycli/commit/c7f82d1124d51f83f87326e460cb96a983c0fd4a))

- **auth**: Move the OAuth login client from requests to httpx2
  ([#151](https://github.com/bim-ba/ycli/pull/151),
  [`6958358`](https://github.com/bim-ba/ycli/commit/695835886ad3103472b463dab69d6f1d3f0af0d7))

- **wiki**: Move Wiki to the httpx2 core and retire the uplink-era checks
  ([#149](https://github.com/bim-ba/ycli/pull/149),
  [`c7f82d1`](https://github.com/bim-ba/ycli/commit/c7f82d1124d51f83f87326e460cb96a983c0fd4a))

- **wiki**: Move Wiki to the httpx2 core with contract tests
  ([#149](https://github.com/bim-ba/ycli/pull/149),
  [`c7f82d1`](https://github.com/bim-ba/ycli/commit/c7f82d1124d51f83f87326e460cb96a983c0fd4a))

### Testing

- State the Wiki results no single reply holds ([#149](https://github.com/bim-ba/ycli/pull/149),
  [`c7f82d1`](https://github.com/bim-ba/ycli/commit/c7f82d1124d51f83f87326e460cb96a983c0fd4a))


## v0.24.3 (2026-10-02)

### Bug Fixes

- **tracker**: Start a time report now when no start is given
  ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

### Build System

- Re-lock uv.lock for 0.24.2
  ([`f87fc5b`](https://github.com/bim-ba/ycli/commit/f87fc5ba87785346178a1efc0a11876a789f2de2))

### Documentation

- Say Forms and Tracker run on the core ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

### Refactoring

- **tracker**: Move entities, bulk, import, dashboards and attachments to the httpx2 core
  ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

- **tracker**: Move group C resources to the httpx2 core
  ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

- **tracker**: Move queues, fields and the reference resources to the httpx2 core
  ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

- **tracker**: Move Tracker to the httpx2 core with contract tests
  ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

- **tracker**: Wire resources to one core session ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

### Testing

- State the queues a limit keeps ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))

- **contract**: Count a nested CLI command as covered by a case
  ([#148](https://github.com/bim-ba/ycli/pull/148),
  [`2b8882c`](https://github.com/bim-ba/ycli/commit/2b8882c8aa68308ca1d3109469c7bce7a449db71))


## v0.24.2 (2026-10-02)

### Bug Fixes

- **core**: Accept only an unfollowed redirect as success, and check SDK results in the contract
  ([#147](https://github.com/bim-ba/ycli/pull/147),
  [`8440de2`](https://github.com/bim-ba/ycli/commit/8440de28b2e7046ebe7b0b432cf4a62ca557ae86))

### Build System

- Re-lock uv.lock for 0.24.1
  ([`4a0ee8f`](https://github.com/bim-ba/ycli/commit/4a0ee8fe5ff285dbea144207d141005006d50c28))

### Refactoring

- Drop redundant snapshots, the unused integration marker and no-op CLI anchors
  ([#138](https://github.com/bim-ba/ycli/pull/138),
  [`9e1297d`](https://github.com/bim-ba/ycli/commit/9e1297d470661dc7e8e1e39463dc72cb668fffa4))

- **cli**: Drop the no-op _group callback anchors ([#138](https://github.com/bim-ba/ycli/pull/138),
  [`9e1297d`](https://github.com/bim-ba/ycli/commit/9e1297d470661dc7e8e1e39463dc72cb668fffa4))

- **forms**: Move Forms to the httpx2 core with contract tests
  ([#147](https://github.com/bim-ba/ycli/pull/147),
  [`8440de2`](https://github.com/bim-ba/ycli/commit/8440de28b2e7046ebe7b0b432cf4a62ca557ae86))

### Testing

- Check that the SDK keeps what the API returned, and state made-up results
  ([#147](https://github.com/bim-ba/ycli/pull/147),
  [`8440de2`](https://github.com/bim-ba/ycli/commit/8440de28b2e7046ebe7b0b432cf4a62ca557ae86))

- Compare only one-request contract cases with their reply
  ([#147](https://github.com/bim-ba/ycli/pull/147),
  [`8440de2`](https://github.com/bim-ba/ycli/commit/8440de28b2e7046ebe7b0b432cf4a62ca557ae86))

- Drop snapshot copies that carry no information of their own
  ([#138](https://github.com/bim-ba/ycli/pull/138),
  [`9e1297d`](https://github.com/bim-ba/ycli/commit/9e1297d470661dc7e8e1e39463dc72cb668fffa4))

- Drop the unused integration marker and its enforcer
  ([#138](https://github.com/bim-ba/ycli/pull/138),
  [`9e1297d`](https://github.com/bim-ba/ycli/commit/9e1297d470661dc7e8e1e39463dc72cb668fffa4))

- Live e2e scenarios against the test organization ([#133](https://github.com/bim-ba/ycli/pull/133),
  [`0109ef5`](https://github.com/bim-ba/ycli/commit/0109ef5511782edb882b06acb576ae55b65ca063))

- Make every contract result checked or stated, and prove the harness checks bite
  ([#147](https://github.com/bim-ba/ycli/pull/147),
  [`8440de2`](https://github.com/bim-ba/ycli/commit/8440de28b2e7046ebe7b0b432cf4a62ca557ae86))

- Run the suite on four pytest-xdist workers ([#146](https://github.com/bim-ba/ycli/pull/146),
  [`f8cf658`](https://github.com/bim-ba/ycli/commit/f8cf658a4b6da939c8d9be559975db344e0ccdcf))

- State the Ack of a Forms file delete ([#147](https://github.com/bim-ba/ycli/pull/147),
  [`8440de2`](https://github.com/bim-ba/ycli/commit/8440de28b2e7046ebe7b0b432cf4a62ca557ae86))

- **e2e**: Drop the integration marker removed in #138
  ([#133](https://github.com/bim-ba/ycli/pull/133),
  [`0109ef5`](https://github.com/bim-ba/ycli/commit/0109ef5511782edb882b06acb576ae55b65ca063))

- **e2e**: Live scenarios against the test organization
  ([#133](https://github.com/bim-ba/ycli/pull/133),
  [`0109ef5`](https://github.com/bim-ba/ycli/commit/0109ef5511782edb882b06acb576ae55b65ca063))


## v0.24.1 (2026-10-02)

### Bug Fixes

- **auth**: Keep the device code copyable and name the missing org permission
  ([#139](https://github.com/bim-ba/ycli/pull/139),
  [`e299e86`](https://github.com/bim-ba/ycli/commit/e299e86a73ea3a66621b2acf7fac39fd13874ac3))

### Build System

- Re-lock uv.lock for 0.24.0
  ([`f24f3eb`](https://github.com/bim-ba/ycli/commit/f24f3eb72fa44533102bbd2ed611375a92b0cef2))


## v0.24.0 (2026-10-02)

### Build System

- Re-lock uv.lock for 0.23.1
  ([`b258711`](https://github.com/bim-ba/ycli/commit/b25871157f3b2f7b78ef4b2196e6cf0fd01c51fd))

### Features

- **mcp**: Run on fastmcp 4 and keep the API's field names in every dump
  ([#128](https://github.com/bim-ba/ycli/pull/128),
  [`58a9600`](https://github.com/bim-ba/ycli/commit/58a9600e6bc7bcd73513445694c7f55f9b24904f))

### Breaking Changes

- **mcp**: The [mcp] extra requires fastmcp>=4.0.10,<5. In the SDK, model_dump() without arguments
  now returns the API's field names (createdAt) instead of attribute names; pass by_alias=False for
  the old shape.


## v0.23.1 (2026-10-02)

### Bug Fixes

- **core**: Sign the service-account JWT for the endpoint it is sent to
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

- **tracker**: Send an empty --description on issues update
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

### Build System

- Re-lock uv.lock for 0.23.0
  ([`a6dd10d`](https://github.com/bim-ba/ycli/commit/a6dd10dbc54058daeb2915bdbf6d3cab1abb19a4))

### Documentation

- Drop hand-kept tool counts and fix stale claims ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

- **mcp**: Describe the listing cap by its setting, not a hardcoded 500
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

### Refactoring

- Plain code and single sources after the E1 review
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

- **core**: Declare Endpoint as a plain frozen dataclass
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

- **http**: Drop the second copy of the HTTP defaults
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

- **mcp**: Import the server from ycli.mcp.server directly
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

- **sdk**: Build clients with a generic function and close them per MCP call
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

- **settings**: Spell the credential variable names once
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))

### Testing

- Pass the now-required timeout to OAuthClient in the new failure test
  ([#132](https://github.com/bim-ba/ycli/pull/132),
  [`32fe1ef`](https://github.com/bim-ba/ycli/commit/32fe1efd6c9c999ea50a60bb54a2543fce6b7782))


## v0.23.0 (2026-10-02)

### Bug Fixes

- **auth**: Type OAuth login failures and make the ARCH-1/4/8 checks bite
  ([#131](https://github.com/bim-ba/ycli/pull/131),
  [`5d0be08`](https://github.com/bim-ba/ycli/commit/5d0be08d8384f4ef58b7a78c993789bf85ea0b61))

- **auth**: Type OAuth login failures and make the architecture checks bite
  ([#131](https://github.com/bim-ba/ycli/pull/131),
  [`5d0be08`](https://github.com/bim-ba/ycli/commit/5d0be08d8384f4ef58b7a78c993789bf85ea0b61))

### Build System

- Re-lock uv.lock for 0.22.2
  ([`38f586e`](https://github.com/bim-ba/ycli/commit/38f586ef872cca68f342912ef492c0f5feca756f))

### Features

- **scaffold**: Generate new resources on the httpx2 core
  ([#131](https://github.com/bim-ba/ycli/pull/131),
  [`5d0be08`](https://github.com/bim-ba/ycli/commit/5d0be08d8384f4ef58b7a78c993789bf85ea0b61))

### Testing

- **arch**: Let require_found raise its not-found error locally
  ([#131](https://github.com/bim-ba/ycli/pull/131),
  [`5d0be08`](https://github.com/bim-ba/ycli/commit/5d0be08d8384f4ef58b7a78c993789bf85ea0b61))


## v0.22.2 (2026-10-02)

### Bug Fixes

- **auth**: Update .env keys with python-dotenv set_key
  ([#130](https://github.com/bim-ba/ycli/pull/130),
  [`c731020`](https://github.com/bim-ba/ycli/commit/c731020f906516c412587f218ff5404facb44813))

- **cli**: Send checklist text verbatim and let edit flags turn properties off
  ([#130](https://github.com/bim-ba/ycli/pull/130),
  [`c731020`](https://github.com/bim-ba/ycli/commit/c731020f906516c412587f218ff5404facb44813))

- **cli**: Send checklist text verbatim and let flags turn properties off
  ([#130](https://github.com/bim-ba/ycli/pull/130),
  [`c731020`](https://github.com/bim-ba/ycli/commit/c731020f906516c412587f218ff5404facb44813))

- **models**: Raise YandexNotFoundError from require_found
  ([#130](https://github.com/bim-ba/ycli/pull/130),
  [`c731020`](https://github.com/bim-ba/ycli/commit/c731020f906516c412587f218ff5404facb44813))

### Build System

- Re-lock uv.lock for 0.22.1
  ([`0899566`](https://github.com/bim-ba/ycli/commit/08995661ea50e39c2caf549f7d45a9db80908d43))

### Testing

- Block unmocked requests on the legacy HTTP stack too
  ([#130](https://github.com/bim-ba/ycli/pull/130),
  [`c731020`](https://github.com/bim-ba/ycli/commit/c731020f906516c412587f218ff5404facb44813))

- Compare the usage error without ANSI codes ([#130](https://github.com/bim-ba/ycli/pull/130),
  [`c731020`](https://github.com/bim-ba/ycli/commit/c731020f906516c412587f218ff5404facb44813))


## v0.22.1 (2026-10-01)

### Bug Fixes

- **core**: Refuse request paths that reach another endpoint
  ([#127](https://github.com/bim-ba/ycli/pull/127),
  [`8311e50`](https://github.com/bim-ba/ycli/commit/8311e502cf256fbdda2ddfd7b092f7e46570e4d8))

### Build System

- Re-lock uv.lock for 0.22.0
  ([`3b2f947`](https://github.com/bim-ba/ycli/commit/3b2f94748706be641f4fb6566cb20247f629e2a2))

### Refactoring

- **arch**: Eight principle-based invariants, each with its check
  ([#126](https://github.com/bim-ba/ycli/pull/126),
  [`92dcd48`](https://github.com/bim-ba/ycli/commit/92dcd48b2bb93c7616aabd70514e16c4e1664385))

### Testing

- **arch**: Close the gaps review found in the eight invariants
  ([#126](https://github.com/bim-ba/ycli/pull/126),
  [`92dcd48`](https://github.com/bim-ba/ycli/commit/92dcd48b2bb93c7616aabd70514e16c4e1664385))


## v0.22.0 (2026-10-01)

### Bug Fixes

- **core**: Harden the httpx2 core after review ([#125](https://github.com/bim-ba/ycli/pull/125),
  [`818e128`](https://github.com/bim-ba/ycli/commit/818e128b2e12402543918d9aff336a38fd818d4c))

### Build System

- Re-lock uv.lock for 0.21.1
  ([`1d0416c`](https://github.com/bim-ba/ycli/commit/1d0416c9d2fc07de37ba231be47e951ddfc87c98))

### Features

- **core**: Httpx2 core with pluggable auth; Tracker issues paginate on it
  ([#125](https://github.com/bim-ba/ycli/pull/125),
  [`818e128`](https://github.com/bim-ba/ycli/commit/818e128b2e12402543918d9aff336a38fd818d4c))


## v0.21.1 (2026-10-01)

### Build System

- Re-lock uv.lock for 0.21.0
  ([`af2099d`](https://github.com/bim-ba/ycli/commit/af2099d229af6bc27519973fe16dff3d8408a762))

### Performance Improvements

- **cli**: Load each service's commands only when that service runs
  ([#124](https://github.com/bim-ba/ycli/pull/124),
  [`5414e5f`](https://github.com/bim-ba/ycli/commit/5414e5f89daa857deb0306d10e886ff980c6b01d))

### Testing

- **package**: Narrow the smoke test's group types for ty
  ([#124](https://github.com/bim-ba/ycli/pull/124),
  [`5414e5f`](https://github.com/bim-ba/ycli/commit/5414e5f89daa857deb0306d10e886ff980c6b01d))

- **package**: Smoke-check the lazily listed sub-apps through Click's API
  ([#124](https://github.com/bim-ba/ycli/pull/124),
  [`5414e5f`](https://github.com/bim-ba/ycli/commit/5414e5f89daa857deb0306d10e886ff980c6b01d))


## v0.21.0 (2026-10-01)

### Bug Fixes

- **cli**: Defer client building and tighten the stdout guard after review
  ([#123](https://github.com/bim-ba/ycli/pull/123),
  [`34aeb78`](https://github.com/bim-ba/ycli/commit/34aeb78d31050f4d23878d474e1de989c129c1c4))

### Build System

- Re-lock uv.lock for 0.20.0
  ([`8c1e361`](https://github.com/bim-ba/ycli/commit/8c1e361385b9421591d76aebfb91a2f2880d49cd))

### Refactoring

- **cli**: Commands return their results and receive clients by injection
  ([#123](https://github.com/bim-ba/ycli/pull/123),
  [`34aeb78`](https://github.com/bim-ba/ycli/commit/34aeb78d31050f4d23878d474e1de989c129c1c4))

### Testing

- **cli**: Assert the usage-error exit code, not the wrapped message
  ([#123](https://github.com/bim-ba/ycli/pull/123),
  [`34aeb78`](https://github.com/bim-ba/ycli/commit/34aeb78d31050f4d23878d474e1de989c129c1c4))

### Breaking Changes

- **cli**: `ycli.yandex.tracker.utils` is gone; `parse_fields` lives in `ycli.cli.fields`.


## v0.20.0 (2026-10-01)

### Build System

- Re-lock uv.lock for 0.19.0
  ([`edff598`](https://github.com/bim-ba/ycli/commit/edff59807145600b4aa32b5951609e127d5fdb7d))

### Refactoring

- **core**: One service registry and per-request MCP credentials
  ([#122](https://github.com/bim-ba/ycli/pull/122),
  [`208eab5`](https://github.com/bim-ba/ycli/commit/208eab5725bed4def010126faa7ae7b696ff89f8))

### Breaking Changes

- **core**: The `status_get` MCP tool and `ycli auth status` report `account` instead of the
  service-specific `me` payload. `ycli.yandex.mcp.make_cached_client` is replaced by
  `client_provider`.


## v0.19.0 (2026-10-01)

### Build System

- Re-lock uv.lock for 0.18.0
  ([`aceae84`](https://github.com/bim-ba/ycli/commit/aceae84c0b691b0ce93aa4c8b14a6a905bed572c))

### Features

- **logging**: Replace loguru with stdlib logging and log HTTP traffic
  ([#121](https://github.com/bim-ba/ycli/pull/121),
  [`da42c66`](https://github.com/bim-ba/ycli/commit/da42c66d70e81288035f6970f2a163175b2e22df))

### Breaking Changes

- **logging**: The default log level is `WARNING` (was `INFO`), and the `loguru` dependency is gone;
  configure the stdlib `ycli` logger instead.


## v0.18.0 (2026-10-01)

### Build System

- Re-lock uv.lock for 0.17.2
  ([`a51f9e6`](https://github.com/bim-ba/ycli/commit/a51f9e617c4b8a474c6fc41f65df95c3c28b0da6))

### Chores

- **graphify**: Stop committing the code graph and build it locally on demand
  ([#115](https://github.com/bim-ba/ycli/pull/115),
  [`5856adb`](https://github.com/bim-ba/ycli/commit/5856adb96c20782d38fa70ac3e287287a53279c5))

### Continuous Integration

- Add a stable `tests` gate over the Python matrix
  ([`eb009db`](https://github.com/bim-ba/ycli/commit/eb009db7a16e2ccb6b2173821fded401e5bbf538))

- Gate PRs on rulesync drift, skill frontmatter and a dist smoke test
  ([#117](https://github.com/bim-ba/ycli/pull/117),
  [`286655f`](https://github.com/bim-ba/ycli/commit/286655fc2b02458898f35139319d339ed2f46420))

- Test on Python 3.14 and list the current required checks in the instructions
  ([`eb009db`](https://github.com/bim-ba/ycli/commit/eb009db7a16e2ccb6b2173821fded401e5bbf538))

### Documentation

- Drop docs/superpowers history and keep its two live decisions
  ([#116](https://github.com/bim-ba/ycli/pull/116),
  [`9a7ba2c`](https://github.com/bim-ba/ycli/commit/9a7ba2cb78ae9ec21e48b752e38a1d0f0071a2da))

- **skills**: Teach agents to read Yandex API docs as Markdown
  ([`37cd8ef`](https://github.com/bim-ba/ycli/commit/37cd8eff4565b442ebeef638eedb92a704242c8b))

### Features

- **settings**: Group settings as YCLI__<GROUP>__<SETTING> and reject invalid values
  ([#120](https://github.com/bim-ba/ycli/pull/120),
  [`152441f`](https://github.com/bim-ba/ycli/commit/152441f3eff63742c36ed48e90cc58e5741098aa))

### Breaking Changes

- **settings**: `YCLI_TIMEOUT_SECONDS`, `YCLI_RETRIES`, `YCLI_MAX_ITEMS` and `YCLI_LOG_LEVEL` are
  renamed to `YCLI__HTTP__TIMEOUT_SECONDS`, `YCLI__HTTP__RETRIES`, `YCLI__HTTP__MAX_ITEMS` and
  `YCLI__LOGGING__LEVEL`. `Credentials.oauth_token` and `OAuthAppConfig.client_secret` are
  `SecretStr`.


## v0.17.2 (2026-10-01)

### Bug Fixes

- **scripts**: Make the /new-endpoint scaffold import against the current package layout
  ([`6a40659`](https://github.com/bim-ba/ycli/commit/6a40659b1d6e03bba02655bf4d63fc8a7e3f7269))

- **sdk**: Keep fractional request timeouts instead of truncating them to an integer
  ([`f7bc7f0`](https://github.com/bim-ba/ycli/commit/f7bc7f0757778aff66de93ccce9edc1e32ef7ad5))

### Build System

- Re-lock uv.lock for 0.17.1
  ([`2dbdbd1`](https://github.com/bim-ba/ycli/commit/2dbdbd1e83d634e6e27d03ff0b739404b6b29277))

- **deps**: Bump the actions group across 1 directory with 2 updates
  ([`9165419`](https://github.com/bim-ba/ycli/commit/91654192c419589f5b48de2c14ed434eabd4e896))


## v0.17.1 (2026-09-28)

### Bug Fixes

- **mcp**: Anchor the generated-config ignore patterns to the repository root
  ([`04fa561`](https://github.com/bim-ba/ycli/commit/04fa561846786b516a2d16569f9fcde93cec292c))

### Build System

- Re-lock uv.lock for 0.17.0
  ([`2ba8acd`](https://github.com/bim-ba/ycli/commit/2ba8acdb2390cf038da98ad413b43a6dccf54965))

### Chores

- Drop the obsolete .mcp.example.json (rulesync owns the MCP source)
  ([`882cfa4`](https://github.com/bim-ba/ycli/commit/882cfa48bd593ead96f842c204ca2dd12d34bd31))

- **ai-config**: Migrate project config to a rulesync canon
  ([`68e7a7b`](https://github.com/bim-ba/ycli/commit/68e7a7b5ae1242e0a080bed195c7843bdd6722c9))

- **claude**: Drop retired bim-ba marketplace settings
  ([`e42d298`](https://github.com/bim-ba/ycli/commit/e42d298f5c9c9e1aec85d496259b368767db5444))

- **codex**: Drop the orphaned example config
  ([`1818f2a`](https://github.com/bim-ba/ycli/commit/1818f2a1db8c21e98adb9fd3b3a2ebfef45f3cb4))

- **codex**: Track the rendered Codex MCP example config
  ([`697af65`](https://github.com/bim-ba/ycli/commit/697af65cf95945349dfd50eb2961229accd9d21d))

- **mcp**: Drop the github MCP leftovers from the docs
  ([`1c018c5`](https://github.com/bim-ba/ycli/commit/1c018c592e9b927d79b558b892b5a58ca40777cd))

- **mcp**: Drop the github MCP server
  ([`af41dfe`](https://github.com/bim-ba/ycli/commit/af41dfe103e0e448875ec2e847714c865aa06f27))

- **mcp**: Resolve Yandex 360 credentials into a gitignored local overlay
  ([`364d2b0`](https://github.com/bim-ba/ycli/commit/364d2b099596b3cbe816f78da15c0ad74d4f005f))

- **rulesync**: Drop the retired bim-ba plugins from the canon
  ([`3f9e58b`](https://github.com/bim-ba/ycli/commit/3f9e58b29daee32753d7c0be144c704f7fa318a9))

- **settings**: Disable the clickhouse plugin in this project
  ([`606b0ea`](https://github.com/bim-ba/ycli/commit/606b0eaa5529b62f87e4842e35083756aea407a7))

- **settings**: Drop stale plugin enablement entries
  ([`e9c7959`](https://github.com/bim-ba/ycli/commit/e9c7959a94fb951e79333be4655e1e9a7746c900))

- **settings**: Stop re-enabling plugins that are off globally
  ([`58a0b61`](https://github.com/bim-ba/ycli/commit/58a0b61c6b7a7e81ab69028394d74c67bc7c84b7))

- **skills**: Drop two duplicated skills and thin the Yandex descriptions
  ([`8bc90ab`](https://github.com/bim-ba/ycli/commit/8bc90ab7afcbe58e0941a2c02879090fccbb37e8))


## v0.17.0 (2026-09-03)

### Build System

- Re-lock uv.lock for 0.16.1
  ([`c9dba07`](https://github.com/bim-ba/ycli/commit/c9dba075c936e08bcd1675ed82d72192ca37398c))

- **deps**: Bump astral-sh/setup-uv ([#64](https://github.com/bim-ba/ycli/pull/64),
  [`dea50bd`](https://github.com/bim-ba/ycli/commit/dea50bdb2a80f9ffdcf0ff9d0b3d98bbc0952e3d))

- **deps**: Bump the actions group with 2 updates ([#60](https://github.com/bim-ba/ycli/pull/60),
  [`2019793`](https://github.com/bim-ba/ycli/commit/2019793a03ee02f3070435eee447b8b93db524ff))

### Chores

- Add .mcp.example.json (secrets moved to ~/.secrets/mcp.env)
  ([`3b3c999`](https://github.com/bim-ba/ycli/commit/3b3c99904035f00de9345cfdeb9255e323838ef5))

- Agent-environment hygiene and the yandex-cloud docs bump
  ([#61](https://github.com/bim-ba/ycli/pull/61),
  [`c5981a1`](https://github.com/bim-ba/ycli/commit/c5981a1d2c27757f418f9ce39f13ad853f134385))

- Drop the retired parallel plugin and the dead graphify stub
  ([#61](https://github.com/bim-ba/ycli/pull/61),
  [`c5981a1`](https://github.com/bim-ba/ycli/commit/c5981a1d2c27757f418f9ce39f13ad853f134385))

- Move the per-clone ignore rules into the tracked .gitignore
  ([#61](https://github.com/bim-ba/ycli/pull/61),
  [`c5981a1`](https://github.com/bim-ba/ycli/commit/c5981a1d2c27757f418f9ce39f13ad853f134385))

- Remove claudelint
  ([`c8b8688`](https://github.com/bim-ba/ycli/commit/c8b8688c3e1e11409dfb9273806396f2cd7aa774))

- **claude**: AutoUpdate on every marketplace, fix inert declarations
  ([`bbfaf72`](https://github.com/bim-ba/ycli/commit/bbfaf72095cd91a29d6e484f3fe34ccb429d9aaf))

- **marketplace**: Follow the ai marketplace to bim-ba-ai/marketplace
  ([#61](https://github.com/bim-ba/ycli/pull/61),
  [`c5981a1`](https://github.com/bim-ba/ycli/commit/c5981a1d2c27757f418f9ce39f13ad853f134385))

- **plugins**: Enable the five bim-ba plugins after the split
  ([#62](https://github.com/bim-ba/ycli/pull/62),
  [`7b04722`](https://github.com/bim-ba/ycli/commit/7b047226e93baa8e48f19e1b5a64e2a0b8c3069b))

- **plugins**: Follow the ai marketplace to bim-ba/ai as core@bim-ba
  ([#62](https://github.com/bim-ba/ycli/pull/62),
  [`7b04722`](https://github.com/bim-ba/ycli/commit/7b047226e93baa8e48f19e1b5a64e2a0b8c3069b))

- **refs**: Bump the yandex-cloud docs submodule ([#61](https://github.com/bim-ba/ycli/pull/61),
  [`c5981a1`](https://github.com/bim-ba/ycli/commit/c5981a1d2c27757f418f9ce39f13ad853f134385))

- **skills**: De-vendor graphify to user-level ~/.claude/skills/graphify
  ([`5523623`](https://github.com/bim-ba/ycli/commit/552362357025bce23d2bccbd578395080453871c))

- **skills**: Declare type/category frontmatter per skills-authoring-standard
  ([`a8a8558`](https://github.com/bim-ba/ycli/commit/a8a85585e0ea993fc587d71db26e02c1eab9f34e))

### Documentation

- Re-home ycli facts from agent memory (refract pointer, skip-ci mechanism, verify gate)
  ([`51e9b12`](https://github.com/bim-ba/ycli/commit/51e9b12adb0f759a3e1ddcf5da92240098ae9b4f))

- Refresh social-preview card (svg + regenerated png)
  ([#56](https://github.com/bim-ba/ycli/pull/56),
  [`9f272a4`](https://github.com/bim-ba/ycli/commit/9f272a4a26e41cf9fd47febfc69328df07fa2201))

- **claude**: Drop duplicates of the personal layer ([#65](https://github.com/bim-ba/ycli/pull/65),
  [`5c434db`](https://github.com/bim-ba/ycli/commit/5c434db6285048704ddb8da417776cd3a6690915))

### Features

- **tracker**: Expose issue response fields ([#66](https://github.com/bim-ba/ycli/pull/66),
  [`b8d00f4`](https://github.com/bim-ba/ycli/commit/b8d00f452953ea79acafb4a5981a1b272bbe18c1))


## v0.16.1 (2026-07-13)

### Bug Fixes

- Guard cursor drains against a non-advancing cursor (infinite-loop protection)
  ([#54](https://github.com/bim-ba/ycli/pull/54),
  [`98b0505`](https://github.com/bim-ba/ycli/commit/98b0505e3ea0ff4b123560351134a817ba73dfbc))

### Build System

- Re-lock uv.lock for 0.16.0
  ([`7b87bab`](https://github.com/bim-ba/ycli/commit/7b87bab43b45d163d773443826f3f3e23d91c44e))

### Testing

- Backfill @pytest.mark.integration on 97 wiring files + enforcement
  ([#53](https://github.com/bim-ba/ycli/pull/53),
  [`14e990f`](https://github.com/bim-ba/ycli/commit/14e990f79dfa4d1e81b0ed8a4a9023e38ce0f967))

- Dedup creds fixture (100->1) and BASE constant (143->3 domain hosts)
  ([#52](https://github.com/bim-ba/ycli/pull/52),
  [`8605c67`](https://github.com/bim-ba/ycli/commit/8605c67093e79dbc0d8c01579ae04d77938b98b7))


## v0.16.0 (2026-07-13)

### Build System

- Re-lock uv.lock for 0.15.0
  ([`2c7d435`](https://github.com/bim-ba/ycli/commit/2c7d435c064a52717c0775d4c43aa7d624dd0e2e))

### Refactoring

- Pagination fold+clamp, shared not-found guard, QuestionMove errors on bare position
  ([#51](https://github.com/bim-ba/ycli/pull/51),
  [`c938228`](https://github.com/bim-ba/ycli/commit/c9382284fd742007e1c4e6dbf515bd6e87d5fbfe))

### Breaking Changes

- MCP tool questions_move now returns a validation error when called with only 'position' (no
  page/page_id/question/create_page) instead of silently retargeting to page 1. The CLI is
  unaffected (defaults to page 1 visibly).


## v0.15.0 (2026-07-13)

### Build System

- Re-lock uv.lock for 0.14.0
  ([`aed4b9b`](https://github.com/bim-ba/ycli/commit/aed4b9bbcda26c33816e7cca9004c334756012ce))

### Features

- Shared Ack detail source + retire *ActionResult wrappers
  ([#55](https://github.com/bim-ba/ycli/pull/55),
  [`3f5a6f3`](https://github.com/bim-ba/ycli/commit/3f5a6f3c3bb690214abc24209c24fbf29d408bb5))

### Refactoring

- Add single-source Ack detail builders + fix 7 drifted write-op details
  ([#55](https://github.com/bim-ba/ycli/pull/55),
  [`3f5a6f3`](https://github.com/bim-ba/ycli/commit/3f5a6f3c3bb690214abc24209c24fbf29d408bb5))

- Retire *ActionResult wrappers in favor of shared Ack
  ([#55](https://github.com/bim-ba/ycli/pull/55),
  [`3f5a6f3`](https://github.com/bim-ba/ycli/commit/3f5a6f3c3bb690214abc24209c24fbf29d408bb5))

### Testing

- Strengthen entities link-create MCP assertion to prove richer detail form
  ([#55](https://github.com/bim-ba/ycli/pull/55),
  [`3f5a6f3`](https://github.com/bim-ba/ycli/commit/3f5a6f3c3bb690214abc24209c24fbf29d408bb5))


## v0.14.0 (2026-07-13)

### Build System

- Re-lock uv.lock for 0.13.1
  ([`21bb37a`](https://github.com/bim-ba/ycli/commit/21bb37aceab63814e0dedfa5ad7d0c3fd764b943))

### Features

- Type all Tracker MCP write-tool bodies + fail-closed enforcement
  ([#49](https://github.com/bim-ba/ycli/pull/49),
  [`08c80fd`](https://github.com/bim-ba/ycli/commit/08c80fd73fffdf87aa7657e79a15d80225d21319))


## v0.13.1 (2026-07-13)

### Bug Fixes

- Floor negative --limit to default cap; bump fastmcp lock to 3.4.4
  ([#44](https://github.com/bim-ba/ycli/pull/44),
  [`c129022`](https://github.com/bim-ba/ycli/commit/c1290229f467f0ef7f93568b619d4b89a635ca06))

### Build System

- Re-lock uv.lock for 0.13.0
  ([`2c5c1f2`](https://github.com/bim-ba/ycli/commit/2c5c1f2a62d8f0c8fc16bee9ead196811a772a01))

- **deps**: Bump the actions group with 3 updates ([#34](https://github.com/bim-ba/ycli/pull/34),
  [`9a8b9de`](https://github.com/bim-ba/ycli/commit/9a8b9dedeb9c6d192adc658d9b5b8166b22ea3bd))

### Chores

- AI-environment ergonomics — scope perms, throttle graphify hook, harden git_guard
  ([#47](https://github.com/bim-ba/ycli/pull/47),
  [`61c8512`](https://github.com/bim-ba/ycli/commit/61c851220c6d2480252fd61ce3518c83ed8d8bf1))

- **drift-log**: Codify typed MCP write-tool body; close open drift entry
  ([#42](https://github.com/bim-ba/ycli/pull/42),
  [`bd0447c`](https://github.com/bim-ba/ycli/commit/bd0447cbd9e41c75af0d6a695d25cd34ad8b2be7))

### Documentation

- Advertise 222 MCP tools, bump plugin version, document social-preview regen
  ([#45](https://github.com/bim-ba/ycli/pull/45),
  [`cf0be28`](https://github.com/bim-ba/ycli/commit/cf0be28103397f9f452d11f58f0e0bec04f8a6c9))

- Base-cleanup design spec + implementation plan ([#43](https://github.com/bim-ba/ycli/pull/43),
  [`3b11ac6`](https://github.com/bim-ba/ycli/commit/3b11ac6feb2ca1702de0ed132140ff72a87f6503))

- Restructure README, delete internal notes, deep-link coverage tables
  ([#41](https://github.com/bim-ba/ycli/pull/41),
  [`fbec717`](https://github.com/bim-ba/ycli/commit/fbec717763469a00ccf088be19b5846e924a6f2a))

### Refactoring

- Rename cfg MCP-tool param to config ([#46](https://github.com/bim-ba/ycli/pull/46),
  [`5eeaf5a`](https://github.com/bim-ba/ycli/commit/5eeaf5ab760c317aebeae827a78341cfc6fe6248))

### Testing

- Harden ARCH conformance harness (op-parity, helper-follow, print-guard, strict-markers)
  ([#48](https://github.com/bim-ba/ycli/pull/48),
  [`8494c88`](https://github.com/bim-ba/ycli/commit/8494c880fe5d4c6016588f94728b626c267baa25))


## v0.13.0 (2026-07-13)

### Bug Fixes

- **mcp**: Cyrillic grid-column slugs + enforce write-tag on write tools
  ([#40](https://github.com/bim-ba/ycli/pull/40),
  [`7f8e58e`](https://github.com/bim-ba/ycli/commit/7f8e58eee27b070ec916a0495c29671702be1726))

### Build System

- Re-lock uv.lock for 0.12.0
  ([`10fd277`](https://github.com/bim-ba/ycli/commit/10fd27785384dc548a56ced228fe826a198e0378))

### Chores

- Dedup CI lint, drop dead ruff ignore, fix VHS cache-key drift, graphify hygiene
  ([#38](https://github.com/bim-ba/ycli/pull/38),
  [`51ef62a`](https://github.com/bim-ba/ycli/commit/51ef62ae9e35baf31bbe94fae02400fa02ffab6c))

- **drift-log**: MCP write-tool body should be a typed model, not dict
  ([#40](https://github.com/bim-ba/ycli/pull/40),
  [`7f8e58e`](https://github.com/bim-ba/ycli/commit/7f8e58eee27b070ec916a0495c29671702be1726))

### Documentation

- Align every surface with read/write MCP + live-test findings
  ([#40](https://github.com/bim-ba/ycli/pull/40),
  [`7f8e58e`](https://github.com/bim-ba/ycli/commit/7f8e58eee27b070ec916a0495c29671702be1726))

- Correct graphify refresh guidance (graphify update explodes the graph here)
  ([#39](https://github.com/bim-ba/ycli/pull/39),
  [`b197921`](https://github.com/bim-ba/ycli/commit/b1979216cdfc5aba0e47cb8f7d37df7b423314ea))

- Propagate references/ move into docs, fix README layout, refresh demo.gif
  ([#36](https://github.com/bim-ba/ycli/pull/36),
  [`687591b`](https://github.com/bim-ba/ycli/commit/687591b4b51a0ae75cf5ee5136e7f79e5ea84c12))

- Unify org header as one canonical X-Org-Id (kill false casing gotcha)
  ([#35](https://github.com/bim-ba/ycli/pull/35),
  [`6935370`](https://github.com/bim-ba/ycli/commit/69353705e6ed01d9f37dd9eb4d8387f37aa2c3e6))

### Features

- **mcp**: Mirror the SDK with write tools + fix live-found bugs across domains
  ([#40](https://github.com/bim-ba/ycli/pull/40),
  [`7f8e58e`](https://github.com/bim-ba/ycli/commit/7f8e58eee27b070ec916a0495c29671702be1726))

- **mcp**: Read/write MCP server + full-surface live test + tech-debt fixes
  ([#40](https://github.com/bim-ba/ycli/pull/40),
  [`7f8e58e`](https://github.com/bim-ba/ycli/commit/7f8e58eee27b070ec916a0495c29671702be1726))

- **mcp**: Replace ARCH-3 read-only with annotation honesty (core)
  ([#40](https://github.com/bim-ba/ycli/pull/40),
  [`7f8e58e`](https://github.com/bim-ba/ycli/commit/7f8e58eee27b070ec916a0495c29671702be1726))

### Refactoring

- Remove dead SinglePageStrategy pagination class ([#37](https://github.com/bim-ba/ycli/pull/37),
  [`ed670eb`](https://github.com/bim-ba/ycli/commit/ed670ebb0303ee6ac83af3cb7d70de031c417543))


## v0.12.0 (2026-07-11)

### Build System

- Re-lock uv.lock for 0.11.0 ([#28](https://github.com/bim-ba/ycli/pull/28),
  [`c3bf839`](https://github.com/bim-ba/ycli/commit/c3bf83970716abf28a5bec7a85cdbd0e08c1e61f))

### Chores

- Rebuild graphify code-graph with GLM-5.2 deep extraction
  ([#30](https://github.com/bim-ba/ycli/pull/30),
  [`c0de08a`](https://github.com/bim-ba/ycli/commit/c0de08a283361a6f0e3036a601b34e4fe03a56b9))

### Continuous Integration

- Automate post-release uv.lock re-lock, SHA-pin actions, pin VHS toolchain
  ([#31](https://github.com/bim-ba/ycli/pull/31),
  [`ae496ce`](https://github.com/bim-ba/ycli/commit/ae496ce7e38972adeabeae705845810384b9c446))

- Make the demo drift-check report-only ([#31](https://github.com/bim-ba/ycli/pull/31),
  [`ae496ce`](https://github.com/bim-ba/ycli/commit/ae496ce7e38972adeabeae705845810384b9c446))

- Verify-only demo workflow + fix pre-commit hooks ([#27](https://github.com/bim-ba/ycli/pull/27),
  [`fe856db`](https://github.com/bim-ba/ycli/commit/fe856dbb8f197e49f5b561349ad9a98dbdecc4bf))

### Documentation

- Fix plugin-skill doc references (bundle quick-refs + live URLs), drop phantom tool, refresh tool
  counts ([#32](https://github.com/bim-ba/ycli/pull/32),
  [`7fbc625`](https://github.com/bim-ba/ycli/commit/7fbc625f234572d5c848ad75599f7f7ebe13157d))

### Features

- Progress spinners, guided auth login, and pretty/help polish
  ([#33](https://github.com/bim-ba/ycli/pull/33),
  [`6e3606e`](https://github.com/bim-ba/ycli/commit/6e3606e3da00fde0545e31e13d00916e3fec476e))

### Refactoring

- Add CursorStrategy.collect_wrapped and collapse wiki cursor blocks
  ([#29](https://github.com/bim-ba/ycli/pull/29),
  [`4be2e10`](https://github.com/bim-ba/ycli/commit/4be2e102d9890841a75cf124f237c9a68d124d42))

- Build entity fields body from typed EntityFieldsInput
  ([#29](https://github.com/bim-ba/ycli/pull/29),
  [`4be2e10`](https://github.com/bim-ba/ycli/commit/4be2e102d9890841a75cf124f237c9a68d124d42))

- Dedup domain clients, wiki cursor pagination, limit-cap, and entity fields
  ([#29](https://github.com/bim-ba/ycli/pull/29),
  [`4be2e10`](https://github.com/bim-ba/ycli/commit/4be2e102d9890841a75cf124f237c9a68d124d42))

- Dedup pagination-cap logic behind resolve_cap + shared Typer aliases
  ([#29](https://github.com/bim-ba/ycli/pull/29),
  [`4be2e10`](https://github.com/bim-ba/ycli/commit/4be2e102d9890841a75cf124f237c9a68d124d42))

- Extract shared DomainClient constructor for the three domain clients
  ([#29](https://github.com/bim-ba/ycli/pull/29),
  [`4be2e10`](https://github.com/bim-ba/ycli/commit/4be2e102d9890841a75cf124f237c9a68d124d42))


## v0.11.0 (2026-07-10)

### Chores

- Docs fetcher + stop committing yandex.ru corpus + re-lock 0.10.0
  ([#22](https://github.com/bim-ba/ycli/pull/22),
  [`468653e`](https://github.com/bim-ba/ycli/commit/468653e44f233cd0a5314aae63e8eda386503639))

- Move vendored Yandex docs to top-level references/ (360 local + cloud submodule)
  ([#23](https://github.com/bim-ba/ycli/pull/23),
  [`48f2102`](https://github.com/bim-ba/ycli/commit/48f210266a78c40389826df4498c19b4aa81cb73))

- Skip malformed sitemap locs (external links/PDFs) in fetch_docs
  ([#24](https://github.com/bim-ba/ycli/pull/24),
  [`7420bab`](https://github.com/bim-ba/ycli/commit/7420babecac510a5fafefbb8548cb18d550db43c))

### Documentation

- Correct stale per-service org-header-casing claim in CLAUDE.md
  ([#25](https://github.com/bim-ba/ycli/pull/25),
  [`67b6950`](https://github.com/bim-ba/ycli/commit/67b6950bd5a0d3cd240b38bb1f93bb82c030c8fd))

- Fix AI-env doc drift + restore /new-endpoint and /arch-review commands
  ([#25](https://github.com/bim-ba/ycli/pull/25),
  [`67b6950`](https://github.com/bim-ba/ycli/commit/67b6950bd5a0d3cd240b38bb1f93bb82c030c8fd))

- Fix AI-env doc drift and restore /new-endpoint + /arch-review commands
  ([#25](https://github.com/bim-ba/ycli/pull/25),
  [`67b6950`](https://github.com/bim-ba/ycli/commit/67b6950bd5a0d3cd240b38bb1f93bb82c030c8fd))

### Features

- Humane CLI errors, --version, and polished pretty output
  ([#26](https://github.com/bim-ba/ycli/pull/26),
  [`a1fccb3`](https://github.com/bim-ba/ycli/commit/a1fccb379834dac9312ab812754e8be656a78fc1))


## v0.10.0 (2026-07-10)

### Build System

- Sync uv.lock project version to 0.9.0
  ([`7f62799`](https://github.com/bim-ba/ycli/commit/7f62799c5f518515d92f37c4079b03568ed62dd7))

- **deps**: Bump the actions group with 2 updates (git-auto-commit 7.2.0, PSR 10.6.0)
  ([`593f59a`](https://github.com/bim-ba/ycli/commit/593f59a9c314bb20580608042fc12cce8c77a7d7))

### Documentation

- Record enforced branch protection + GitHub App release flow
  ([#19](https://github.com/bim-ba/ycli/pull/19),
  [`7740588`](https://github.com/bim-ba/ycli/commit/7740588f30b303e58acffd16d838637b8960d02b))

### Features

- Full public API coverage, ycli auth login, and live-E2E fixes
  ([#21](https://github.com/bim-ba/ycli/pull/21),
  [`41e5df0`](https://github.com/bim-ba/ycli/commit/41e5df0baefde0faf85f342e363998d8fc3cc530))


## v0.9.0 (2026-06-29)

### Bug Fixes

- **status**: Discriminate the auth me union to survive the MCP round-trip
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Build System

- Make the demo render pretty, realistic output ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Render demo output from committed fixtures, not hand-typed text
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Sync uv.lock project version to 0.8.1 ([#15](https://github.com/bim-ba/ycli/pull/15),
  [`b442d41`](https://github.com/bim-ba/ycli/commit/b442d4157a72605d221eadd8cc296efb53b86481))

### Code Style

- Collapse the test_settings monkeypatch line (ruff format)
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Continuous Integration

- Drop the CI-bypass marker from the demo-GIF auto-commit
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Mint a GitHub App token for PSR so it can push past branch protection
  ([#17](https://github.com/bim-ba/ycli/pull/17),
  [`e0674b5`](https://github.com/bim-ba/ycli/commit/e0674b5136a3b53071cfdb10d3ceae8b6dec4e14))

### Documentation

- Add module docstrings to the four empty __init__.py files
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Add round-4 architecture refactor design spec ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Add round-4 implementation plan (6 tasks) ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Regenerate demo GIF ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **readme**: Match badge style to DeepWiki (flat, logos, semantic colors)
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Features

- Remove the raw issues 'full' accessor and RawMapping
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Round-4 architecture refactor (remove RawMapping/full, status & mcp packages, pagination generics,
  reproducible demo) ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Status package with native me + read-only status_get MCP tool
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Refactoring

- Drop underscore prefixes from internal yandex modules
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Flatten API ref wrappers to scalars via BeforeValidator
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Move the MCP server + CLI into a ycli.mcp package ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Simplify the pretty renderer to lay out flat models
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Type pagination strategies with PEP 695 generics ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **cli**: Drop the lazy __getattr__ shim; reference ycli.cli.app explicitly
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **cli**: Group cli/context/output into the ycli.cli package
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- **cli**: Split domain _args.py into _types.py + _utils.py
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

### Testing

- Align changelog/wiki-comments model test names with the flat-field shape
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Cover render.py unknown-command path + tighten renderer list test
  ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))

- Harden status_get wiki assertion + doc/typing nits ([#16](https://github.com/bim-ba/ycli/pull/16),
  [`f1d95c6`](https://github.com/bim-ba/ycli/commit/f1d95c6c961b503d16f33f9b59a4a2f6c0f8a444))


## v0.8.1 (2026-06-29)

### Bug Fixes

- Detect mcp sub-app via registered_groups in post-build smoke test
  ([#14](https://github.com/bim-ba/ycli/pull/14),
  [`5175d2f`](https://github.com/bim-ba/ycli/commit/5175d2f02e71e8ad03f02f58b3c83d82153cd5a1))


## v0.8.0 (2026-06-29)

### Bug Fixes

- **arch-4**: Route issues full through Serializer; forbid json.dumps outside output.py
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **tracker**: Model transition target status (to) faithfully; realistic _execute test fixtures
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Build System

- Add ty type checker (advisory CI gate while ty is beta)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Sync uv.lock project version to 0.7.0 ([#11](https://github.com/bim-ba/ycli/pull/11),
  [`e7788b5`](https://github.com/bim-ba/ycli/commit/e7788b5e4cf3488f6f8b72b91a260a5baa8393f3))

### Chores

- Commit graphify code-graph routine and built graph snapshot
  ([#13](https://github.com/bim-ba/ycli/pull/13),
  [`0972035`](https://github.com/bim-ba/ycli/commit/0972035194e580f91d6ff233a5ddd0561396a100))

- **graph**: Gitignore graphify output; /codegraph-regen command (local index)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Code Style

- Adopt ruff formatter (mechanical reformat, no behavior change)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Enable ruff lint (E,W,F,I,N,UP,B,A,C4,SIM,PTH,RUF) with autofix
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Ratchet ruff ANN+TC (annotations + type-checking imports)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **ruff**: Suppress B008 for fastmcp Depends via config, drop 25 inline noqa
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Documentation

- Add Task D5 (align issues count CLI<->MCP surface) to round-3 plan
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Design spec for round-3 (tooling, composition/DI, surface, conventions, infra)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Fix stale idioms in README/CLAUDE/skills; update demo tape+shim; regen gif
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Implementation plan for round-3 (A tooling, B DI, C transport, D dedup, E surface, F infra)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Regenerate demo GIF [skip ci] ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **conventions**: Correct resources.md enforcement table (APIModel/naming are code-review only)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **drift**: Seed drift log with three round-2/round-3 genuine entries
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **mcp**: Write tool-metadata standard; scaffold comment; assert description+output schema
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **readme**: Minimalist flat-square badges + DeepWiki + PyPI
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Features

- Round-3 architecture + tooling refactor (ARCH-1..11, ruff+ty, mcp sub-app)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **arch**: Add ARCH-11 doc-drift guard and close drift-log entry
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **cli**: Mcp Typer sub-app (mcp start/methods); delete mcp_launcher; regen snapshots
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **commands**: /snapshot-regen and /release-checklist
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **tracker**: Align issues_count MCP tool with the CLI's query/filter capability
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **tracker**: Model transitions execute as TransitionList; render via Serializer
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

### Refactoring

- Hoist settings to top-level ycli.settings; update ARCH-8 path
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Move APIModel base into ycli.yandex.models (thin top-level)
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- Rename auth.py->status.py (keep 'auth status'); fold probes into ServiceProbe
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **conventions**: Me models -> APIModel; drop dead forms/_models; rename surveys models;
  resources.md ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **di**: ClientFactory + cached MCP factory; collapse _deps; slim AppContext
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **di**: Inject AppConfig via Depends(app_config)/AppContext.config; no on-the-fly settings
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **output**: Decompose PrettyStrategy into RichCell + split list-table builders
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **output**: Remove Tracker-only deeplink (ARCH-5 leak); defer general deeplink design
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **pagination**: Hoist single-page list wrapper into collect_single_page helper
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))

- **transport**: _raise_typed as Transport staticmethod; extract _authorization seam
  ([#12](https://github.com/bim-ba/ycli/pull/12),
  [`1a12f9f`](https://github.com/bim-ba/ycli/commit/1a12f9f331d77b082c20d19d8a3bcdf2dc524588))


## v0.7.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.6.0
  ([`c9ec02e`](https://github.com/bim-ba/ycli/commit/c9ec02e2f42ac3b8a55f2a5bf7c5ad4990d03636))

### Code Style

- **transport**: Restore PEP8 blank line; assert base= applies hook+adapter
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Documentation

- Design spec for round-2 architecture refactor (DI, serialization, pagination, ARCH rules)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Implementation plan for round-2 architecture refactor (13 tasks, 6 phases)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Rename ApiModel -> APIModel in round-2 spec ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Revise MCP DI to per-domain @functools.cache factory (fastmcp-canonical)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- Revise round-2 spec — raw-arg clients + Serializer service
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **arch**: Align ARCH-10 Check with enforcement (max_items not grep-enforced — HTTP 500 collision)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **arch**: ARCH-4 serialization confinement; add ARCH-7..10 (DI, single config, typed errors,
  no-shadow) ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Features

- Round-2 architecture refactor (raw-arg DI, Serializer, pagination strategies, ARCH-7..10)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **config**: Add YCLI_MAX_ITEMS pagination cap (default 500)
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **forms**: Answers list_all via NextUrlStrategy, bounded by --limit/--all
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **pagination**: PaginationStrategy ABC + SinglePage/Cursor/NextUrl strategies
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki**: Auto-paginate pages descendants (CursorStrategy) → flat PageRefList; --limit/--all
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki,forms**: Unwrap comments/attachments/surveys envelopes to flat RootModel collections
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Refactoring

- **cli**: Dedupe KeyArg into _args.py; standardize _group anchors; modernize scaffold template
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **di**: Raw-arg composition clients + AppContext; rewrite CLI call sites via Serializer; drop
  cliformat/_clideps/from_env(CLI) ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **mcp**: Per-domain @cache client factories (fastmcp canonical); delete from_env/FromEnvSession
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **models**: Consolidate four _Lenient bases into a single APIModel
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **output**: Add Serializer service + SerializationStrategy.from_format; fold helpers into
  PrettyStrategy ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **transport**: Raw oauth_token arg + bare-session base injection; inline org header
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

### Testing

- **forms**: Limit-spans-pages drain test; assert single-fetch on page-1 cap
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **models**: Exercise APIModel lenient parsing at runtime, not just config
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **output**: Assert from_format covers all four formats; dedupe io import
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **tracker**: Stub TrackerClient via raw args, not a pre-authed session
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki**: De-duplicate list tests via page_size assertion; PEP8 blank lines
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))

- **wiki**: Drop dead import; --all test drains two pages; assert page_size=100
  ([#10](https://github.com/bim-ba/ycli/pull/10),
  [`38e28ff`](https://github.com/bim-ba/ycli/commit/38e28ff19dd6c799988c715d07c175bc1caca5d2))


## v0.6.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.5.0
  ([`e2f63de`](https://github.com/bim-ba/ycli/commit/e2f63de7348b9343a0c3c8e71bdd96470f72a2ce))

### Features

- Internals cleanup — env settings, transport, output strategies, multi-service auth, wiki me,
  config fixes
  ([`5d45127`](https://github.com/bim-ba/ycli/commit/5d451274f3798a85cb9061ab36af35dc9b3630a1))


## v0.5.0 (2026-06-28)

### Build System

- Sync uv.lock project version to 0.4.0
  ([`ddb8dfe`](https://github.com/bim-ba/ycli/commit/ddb8dfe40b144dc7aa54f06eb632ecf652af50ed))

### Features

- Track C — UX quick-wins (typed errors, MCP metadata, completion, tracker me, auth status, key
  links)
  ([`a19cad7`](https://github.com/bim-ba/ycli/commit/a19cad7484dc22dc8883928d8e2f3a20a3f45747))


## v0.4.0 (2026-06-27)

### Features

- Track B — AI-infra hardening (CI-skip guard, gitleaks, bundled plugin MCP, release/conventions
  docs)
  ([`5ae61ad`](https://github.com/bim-ba/ycli/commit/5ae61ad938631c76daf6202e1318bbbd6f1d5623))


## v0.3.0 (2026-06-27)

### Features

- Architecture guardrails enforcing the six ARCH invariants
  ([`6bbc381`](https://github.com/bim-ba/ycli/commit/6bbc38148a9a0b930171210351166a7cac51b128))


## v0.2.1 (2026-06-27)

### Bug Fixes

- Ship PEP 561 py.typed marker so type checkers see ycli's types
  ([`22986e4`](https://github.com/bim-ba/ycli/commit/22986e4c0992e580112e99a16f0bc1d8492eea29))

### Continuous Integration

- Re-trigger release pipeline for the pending py.typed fix
  ([`69458c1`](https://github.com/bim-ba/ycli/commit/69458c1a3b91661aa798f16eb4d86f31d9469084))


## v0.2.0 (2026-06-27)

### Continuous Integration

- Automate releases with python-semantic-release
  ([`982256e`](https://github.com/bim-ba/ycli/commit/982256e98baf3df3023ef0bfca7ffa39ae1ff617))

### Features

- Global --format/-o for CLI output (auto/json/yaml/pretty)
  ([`ccab9a3`](https://github.com/bim-ba/ycli/commit/ccab9a3ebffcde5752a2a580bce23439abf13f02))


## [0.1.0] — 2026-06-27

### Added
- Initial release: Yandex 360 toolkit for **Tracker**, **Wiki**, and **Forms**.
- Four surfaces from one codebase: Typer **CLI** (`ycli` / `yandex-cli`), FastMCP **server**
  (`ycli mcp`, read-only, `[mcp]` extra), importable **Python SDK** (`ycli.yandex.*`), and a
  **Claude Code plugin** (`plugins/yandex-360/`).
- Published on PyPI as **`yandex-cli`** (`uv add yandex-cli`, or `yandex-cli[mcp]` for the server).
- Test suite at 100% coverage with `responses`-stubbed HTTP.
