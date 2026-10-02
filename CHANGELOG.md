# Changelog

All notable changes to this project are documented here, newest first, following
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). From v0.2.0 on, every
entry below is generated automatically by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) from the
[Conventional Commits](https://www.conventionalcommits.org/) on `main` — do not edit
released sections by hand.

<!-- version list -->

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
