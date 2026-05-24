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
