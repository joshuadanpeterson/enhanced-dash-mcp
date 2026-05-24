# Help Guide

This project provides an MCP server that augments the official Dash MCP. The
official Dash MCP performs exact docset listing, documentation search, full-text
search enablement, and page loading. Enhanced Dash MCP analyzes repos, plans
official Dash searches, ranks official results, and explains local cache
coverage.

- Run the server with `./venv/bin/python3 enhanced_dash_server.py` after setup,
  or any Python 3.11+ interpreter. The script uses
  `stdio_server` internally to expose STDIO streams. Press `Ctrl+C` to
  stop the server gracefully without seeing a stack trace. Since version
  1.2.11 the server logs startup, shutdown, and unexpected error events, and cancels its tasks properly so startup no longer hangs
  when interrupted. Cancellation for `Ctrl+C` and task timeouts now
  share a single code path via `_cancel_task`.
- Initialization options are now generated with
  `server.create_initialization_options()` before running the server to avoid
  `AttributeError: 'dict' object has no attribute 'capabilities'` in certain MCP
  clients.
- If you encounter `ModuleNotFoundError: No module named 'mcp.streams'`,
  update to version 1.1.4 or later which replaces `StdioClient` with
  `stdio_server`.
- Ensure Python 3.11+ and required dependencies from `requirements.txt` are installed.
- Lint and type-check using `flake8 .` and `mypy .`; configuration files are
  provided in `.flake8` and `mypy.ini`.
- Tool `limit` values use an integer `limit`; float-like values are cast to an
  integer and bounded to the relevant tool range.
- Removed v1 overlap tools: `search_dash_docs`, `list_docsets`, and
  `get_doc_content`. Use official Dash MCP tools for exact search and page
  loading.
- Enhanced Dash MCP returns a `dash-augmentation/v1` handoff envelope with
  recommended official docset identifiers, suggested `search_documentation`
  calls, local-only cache candidates, and warnings.
- Logs are written to `~/.cache/dash-mcp/server.log` by default. Adjust
  `DASH_MCP_LOG_LEVEL` and `DASH_MCP_LOG_FILE` environment variables to
  control logging.
- The persistent metadata index is written to
  `~/.cache/dash-mcp/docset-index-v2.json` by default. Set
  `DASH_MCP_INDEX_PATH` in tests or specialized environments.
- Set `DASH_DOCSETS_PATH` only if your Dash docsets aren't under
  `~/Library/Application Support/Dash/DocSets/`.
- Symlinks to that directory are resolved automatically.
- When creating a symlink, target the parent `Dash` directory rather than the
  `DocSets` folder itself. Linking directly to `DocSets` results in a search
  path like `.../DocSets/DocSets` and the server won't find your docsets.
- The server now adjusts automatically if `DASH_DOCSETS_PATH` points to the
  `Dash` directory instead of `DocSets`.
- Docsets inside subfolders are discovered automatically so Dash 4 layouts work
  without extra configuration.
- The log file now includes startup and shutdown messages and records any unexpected errors.

- Review [CHANGELOG.md](../CHANGELOG.md) for a summary of recent releases. The changelog lists versions in reverse chronological order so the latest updates appear first and the entire history is retained for reference.

For more detailed usage, see [server_usage.md](server_usage.md).
- The changelog is automatically updated by GitHub Actions. The workflow now fetches full history so older entries stay intact and appends only the latest release notes.
- If the changelog ever appears truncated, run `git fetch --unshallow` before rerunning the workflow to restore the missing history.
- Version 2.0.0 changed the product boundary to an official-Dash handoff and
  augmentation layer.
- Shell scripts now live under `scripts/` and configuration templates under `configs/`.
- The Claude configuration template (`configs/claude-mcp-config.json`) uses `venv/bin/python3` so you don't need to activate the virtual environment when starting the server through Claude.
- The setup scripts define `DASH_MCP_DIR` as the installation path and all generated files reference this variable.
- During setup you can enter a custom installation path when prompted. Press
  **Enter** to accept the default location.
- By default the script installs to `~/enhanced-dash-mcp`.
- See [AGENTS.md](../AGENTS.md) and [AI_Docs/AGENTS.md](../AI_Docs/AGENTS.md) for guidelines on working with this repository using AI tools.
