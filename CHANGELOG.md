#  (2026-05-24)


* feat!: 🧭 convert Dash MCP to augmentation layer ([a2fe39a](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/a2fe39ae4d6716d2a3494e467000fe5df2aa942d))


### Bug Fixes

* 🧹 resolve flake8 and mypy issues ([e01b3cd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e01b3cd5f509bb072833f2bde7cbed59e205d33a))
* 🩹 consolidate task cancellation ([3f1e15e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/3f1e15e5f50c74b485016b9cd84cb7608a44bb52))
* **changelog:** 📝 restore full history ([1762a0e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/1762a0e5d9e9dd5032955daf829b6aa82d6c4903))
* **changelog:** 📝 restore full history ([956b290](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/956b2903f9ea73e37366a6428b67cd1a7d2daa1b))
* **changelog:** 🛠️ append new release notes ([e989861](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9898613b9519002906bdf1236ec3a3302da1321))
* **deps:** 🔧 Fix MCP compatibility and enhance dependency management ([2fdd40c](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2fdd40c9d2ee2b3b1d9ce6b597cb480deffcf4c8))
* **docsets:** 🐛 Fix Dash docset discovery and database schema handling ([7fbb1ea](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7fbb1ea561991d74e2c707adfed90153a2152524))
* **scripts:** 🛠️ Resolve script stalling issues in Codex environments ([0a97842](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/0a9784220eae11d4176896228bc99c8feb8da8f1))
* **search:** 🐛 cast limit param to int ([e70b568](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e70b568f98e4420f8569ed58768c6a12441b2c87))
* **search:** 🛡️ validate limit inputs\n\nAdd tests for invalid limit values and document the behavior. ([530de36](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/530de36cb74dff32b05ca8bf4c8247f55c33f8a5))
* **server:** 🐛 run using StdioClient ([93aaff0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/93aaff05ff784c468d0adcf4aced73c09625aa28))
* **server:** 🚮 re-raise KeyboardInterrupt ([91c26b2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/91c26b2c67dfb278dfe5a912409b2ba0aa8773ef))
* **server:** 🛑 handle KeyboardInterrupt cleanly ([5ba6459](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/5ba6459dadee3e36e58f66f547c03b5cf13aa22d))
* **setup:** 🐛 Fix validation test to handle non-Dash environments ([398f6e8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/398f6e84638eb9d20ebf6b5f691b3796918c6e70))
* **setup:** 🐛 Make setup script non-interactive for automated environments ([74f269a](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/74f269a181f5a4c8581fea89b03f45f5cf0f68a2))
* **startup:** 🐛 create initialization options ([e9cb087](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/e9cb08758c4a50fa6be24403aebce8cebb2c84dc))
* **symlink:** 🛠️ improve docset symlink handling ([da23af6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/da23af6a509eb331f11d5a11e9611ca279c8c7b0))
* **tests:** ✅ make stdio_server check robust ([48dd505](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48dd505d794f58ebb0dd5246c931c0190302562a))


### Features

* 🎉 automate changelog ([b661b06](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b661b063d2d3b162d17ddfd5766c527e1778b688))
* 📝 bump to 1.1.3 and update docs ([7ffc5ac](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7ffc5ac5b3750f0a0f9c6ee38c580e98f960f06f))
* 🛠️ use stdio_server for server I/O\n\n* replace removed StdioClient import\n* adjust main execution flow\n* bump version to 1.1.2 and update docs\n* update tests and changelog ([2efa38e](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/2efa38e8b3378476431e494f12022ce02ba877ee))
* Allow nested docset directories ([43d44dd](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/43d44dd93ccf653bcfb7f887af1173886a0a72de))
* **ci:** 🎉 add release workflow and changelog links ([957aa45](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/957aa45a6ed03952249ad7e11475858df26cdbc0))
* **docsets:** 🗂️ support nested docset folders ([55417e0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/55417e0a97811003c9be17044610e48b38598c54))
* **docsets:** 🧭 auto-adjust docset path ([f37a2b8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f37a2b8419316d966519a2817229c7e531815425))
* **docsets:** 🚀 Expand docset discovery to entire Dash directory tree ([7f7c4df](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/7f7c4dff3c85e73a5adedd6229deba108a8e3b36))
* **enhanced-dash-mcp:** 🚀 Complete MCP server implementation with Warp integration ([4755ac8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4755ac817b84fb566e9871d4965faf96e5e6b7b0))
* Initial commit ([f4bfea4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f4bfea4dcff04ec063a2abd5ab1c82df803c6b8f))
* **logging:** ✨ log docset path and document symlink support ([fb5ac07](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/fb5ac07ad01868a69bfd7454ca6517bc857c038d))
* **logging:** 🎉 add startup logging ([f072579](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/f072579b89d6d0466d0c130315a6b0ae08415164))
* **logging:** 🎉 add structured logging ([248d36f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/248d36f75f150557d7a025feb969d080bb422d0f))
* **logging:** 📝 improve server event logging ([8849a8f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/8849a8f966aa0ce5113d939bff45b17d9b99d2d2))
* **logging:** 🚀 Comprehensive verbose logging and documentation ([97f8a7f](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/97f8a7f04b1fac99cc36e17bbacf5a14adc43f88))
* **server:** ✨ handle cancellation without hang ([48f5ec6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/48f5ec62ece95fd8625bbeee28e688e696ce6d4e))
* **server:** 🛑 unify cancellation handling ([b1d9693](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/b1d96934a14c25059dac61fc72febd5bf33423c9))
* **server:** 🛠️ ensure Server.run receives streams ([a993850](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/a993850b6a707ce3500337850a95aae4e0a7a5c1))
* **structure:** 📁 reorganize project files ([4bc2243](https://github.com/joshuadanpeterson/enhanced-dash-mcp/commit/4bc2243269c5ab335e3b5585580b687cd4620e55))


### BREAKING CHANGES

* enhanced-dash-mcp no longer exposes search_dash_docs, list_docsets, or get_doc_content; use the official Dash MCP for exact search and page loading.
# Changelog
## [2.0.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v2.0.0) - 2026-05-23

### Breaking Changes

- Repositioned Enhanced Dash MCP as an augmentation layer around the official Dash MCP.
- Removed public overlap tools: `search_dash_docs`, `list_docsets`, and `get_doc_content`.
- Replaced exact Dash search/loading behavior with project-aware recommendation, search planning, result ranking, coverage summaries, and missing-docset explanations.

### Features

- Added a standard `dash-augmentation/v1` handoff envelope for official Dash MCP docset identifiers, search plans, local-only cache candidates, and warnings.
- Added persistent local docset metadata indexing at `~/.cache/dash-mcp/docset-index-v2.json`, overridable with `DASH_MCP_INDEX_PATH`.
- Added project inspection for common JavaScript, Python, Rust, Go, PHP, Ruby, and Java manifests.
- Added coverage-gap reporting between official Dash-visible docsets and valid local cache docsets.

## [1.3.1](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.3.1) - 2025-06-16

### Fixes

- Improved Dash docset discovery and database schema handling.
- Preserved nested docset discovery and symlink correction behavior.

## [1.3.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.3.0) - 2025-06-16

### Features

- Expanded docset discovery across the Dash directory tree.

## [1.2.12](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.12) - 2025-06-11

### Fixes

- Restored full changelog history after release automation truncation.

## [1.2.11](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.11) - 2025-06-10

### Fixes

- Added startup and shutdown logging.
- Centralized cancellation handling to avoid startup hangs.

## [1.2.10](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.10) - 2025-06-10

### Fixes

- Created initialization options before invoking `Server.run`.

## [1.2.9](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.9) - 2025-06-08

### Fixes

- Improved stdio server integration tests.

## [1.2.8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.8) - 2025-06-08

### Fixes

- Handled `KeyboardInterrupt` cleanly.

## [1.2.7](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.7) - 2025-06-08

### Fixes

- Unified task cancellation behavior.

## [1.2.6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.6) - 2025-06-08

### Fixes

- Ensured `Server.run` receives stdio streams.

## [1.2.5](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.5) - 2025-06-08

### Fixes

- Documented `stdio_server` usage.

## [1.2.4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.4) - 2025-06-08

### Fixes

- Replaced removed MCP stdio imports.

## [1.2.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.3) - 2025-06-08

### Fixes

- Adjusted main execution flow for current MCP APIs.

## [1.2.2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.2) - 2025-06-08

### Fixes

- Updated tests for server startup behavior.

## [1.2.1](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.1) - 2025-06-08

### Fixes

- Improved setup validation for non-Dash environments.

## [1.2.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.0) - 2025-06-08

### Features

- Added richer setup automation and project documentation.

## [1.1.11](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.11) - 2025-06-08

### Fixes

- Improved script behavior in automated environments.

## [1.1.10](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.10) - 2025-06-08

### Fixes

- Hardened setup scripts for non-interactive execution.

## [1.1.9](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.9) - 2025-06-08

### Fixes

- Updated Claude configuration template paths.

## [1.1.8](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.8) - 2025-06-08

### Fixes

- Improved help documentation.

## [1.1.7](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.7) - 2025-06-08

### Fixes

- Added changelog ordering checks.

## [1.1.6](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.6) - 2025-06-08

### Fixes

- Added changelog link checks.

## [1.1.5](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.5) - 2025-06-08

### Fixes

- Added version consistency checks.

## [1.1.4](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.4) - 2025-06-08

### Fixes

- Switched to `stdio_server` for server I/O.

## [1.1.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.3) - 2025-06-08

### Features

- Updated docs for MCP startup.

## [1.1.2](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.2) - 2025-06-08

### Features

- Replaced removed stdio client imports.

## [1.1.1](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.1) - 2025-06-08

### Fixes

- Adjusted setup documentation.

## [1.1.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.1.0) - 2025-06-08

### Features

- Added structured startup logging.

## [1.0.0](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.0.0) - 2025-06-07

### Features

- Initial MCP server for local Dash documentation workflows.
