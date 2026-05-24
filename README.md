# Enhanced Dash MCP Server

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/joshuadanpeterson/enhanced-dash-mcp)

## 🎯 What is this?

This is a **Model Context Protocol (MCP)** server that augments the official [Dash](https://kapeli.com/dash) MCP server. The official Dash MCP owns exact Dash-backed operations: installed docsets, precise documentation search, full-text search, and page loading. Enhanced Dash MCP owns the higher-level intelligence around those operations: project context, docset recommendation, local cache discovery, routing, ranking, and workflow guidance.

**In simple terms:** this server tells Claude and other agentic coding tools which Dash docsets and `search_documentation` queries to use for the repo and task in front of them. The official Dash MCP still fetches the search results and documentation pages.

## 📚 About Dash

[Dash](https://kapeli.com/dash) is an API Documentation Browser and Code Snippet Manager for macOS that gives you instant offline access to 200+ API documentation sets. It's the go-to tool for developers who want fast, searchable, offline documentation without relying on internet connectivity or dealing with slow web searches.

## 🔗 Why This Integration Matters

- **Official Dash Handoff**: returns docset identifiers and ready-to-run `search_documentation` calls when you provide a `list_installed_docsets` snapshot
- **Local Cache Awareness**: indexes valid local Dash cache docsets and explains which ones the official Dash MCP cannot see
- **Privacy-Focused**: project inspection and local cache discovery stay on your machine
- **Persistent Metadata Index**: stores docset metadata in `~/.cache/dash-mcp/docset-index-v2.json` so cold discovery is not repeated unnecessarily
- **Context-Aware**: detects a repo's stack and suggests relevant Dash docsets automatically

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 🚀 Features

### **Core Capabilities**

- **Project Context Analysis** - detects languages, frameworks, dependencies, manifests, and common source files
- **Docset Recommendation** - recommends exact Dash docsets for a repo or supplied context
- **Search Planning** - produces official Dash MCP `search_documentation` query plans
- **Result Ranking** - re-ranks official Dash search results without loading page content
- **Coverage Summaries** - compares official Dash-visible docsets with valid local cache docsets
- **Missing Docset Explanations** - explains whether a requested docset is official, local-only, or absent

### **Developer Workflow Integration**

- **Warp Terminal** - Native command palette and workflow integration
- **tmux** - Background server execution across terminal sessions
- **Neovim** - Documentation access while coding via Claude
- **Oh-My-Zsh** - Enhanced aliases and productivity shortcuts
- **Git Integration** - Repository-aware documentation suggestions

### **Supported Technologies**

JavaScript/TypeScript, React, Next.js, Vue.js, Angular, Node.js, Python, Django, Flask, FastAPI, pandas, NumPy, and many more through Dash docsets.

## 📋 Prerequisites

- **macOS** with Dash app installed
- **Python 3.11+**
- **Dash docsets** downloaded (JavaScript, Python, React, etc.)
- **Claude** with MCP support
- **tmux** (recommended for background execution)

### ⚠️ Important Dependency Requirements

This server requires **Pydantic v2.0+** for MCP compatibility. If you have existing projects with Pydantic v1.x, you may need to:

1. Use a virtual environment (recommended)
2. Check for compatibility with other tools (like `pieces-os-client`)
3. Consider using separate Python environments for different projects

```bash
# Check your current Pydantic version
pip show pydantic

# If you have v1.x, you'll need to upgrade
pip install "pydantic>=2.0.0"
```

### 📦 Dependencies

The setup script automatically installs all required dependencies, including:

- `mcp>=1.9.0` - Model Context Protocol framework
- `pydantic>=2.0.0` - Data validation (required for MCP compatibility)
- `typing-extensions>=4.12.0` - Extended type hints

## ⚡ Quick Start

### 🔄 **Important: v2 Boundary Change**

**If you're upgrading from a previous version**, Enhanced Dash MCP no longer exposes direct search/page loading tools. Use the official Dash MCP for:

- `list_installed_docsets`
- `search_documentation`
- `enable_docset_fts`
- `load_documentation_page`

Use Enhanced Dash MCP for repo-aware recommendations, search planning, ranking, coverage summaries, and missing-docset explanations.

To rebuild the v2 metadata index:

```bash
# Clear the metadata index
rm -f ~/.cache/dash-mcp/docset-index-v2.json

# Then restart your server
dash-mcp-restart
# or
cd ~/enhanced-dash-mcp && ./start-dash-mcp.sh --test
```

**What changed:** Enhanced Dash MCP now reports local cache docsets only as metadata and fallback diagnostics. It does not fetch documentation pages.

See [docs/help.md](docs/help.md) for a brief overview of how to run the server.

### 1. **Clone & Setup**

```bash
# Clone or download the project files
mkdir ~/enhanced-dash-mcp && cd ~/enhanced-dash-mcp

# Make setup script executable
chmod +x scripts/setup-dash-mcp.sh

# Run automated setup
./scripts/setup-dash-mcp.sh
```
The script prompts for an installation directory. Press **Enter** to accept the
default path or provide a custom location. The default is `~/enhanced-dash-mcp`.

### 2. **Configure Claude**

Add this to Claude's MCP settings:

```json
{
  "mcpServers": {
    "enhanced-dash-mcp": {
      "command": "$DASH_MCP_DIR/venv/bin/python3",
      "args": [
        "$DASH_MCP_DIR/enhanced_dash_server.py"
      ],
      "env": {}
    }
  }
}
```

### 3. **Start & Test**

```bash
# Add shell enhancements
echo "source ~/enhanced-dash-mcp/dash-mcp-aliases.sh" >> ~/.zshrc
source ~/.zshrc

# Start the server
dash-mcp-start

# Test with Claude
# "Search for React useState hook documentation"
```

## 🎮 Usage

### **Basic Documentation Search**

```bash
# Ask Claude:
"Search for Python pandas DataFrame methods"
"Find React hooks best practices"
"Get FastAPI routing documentation with examples"
```

### **Project-Aware Intelligence**

```bash
# Navigate to your project directory, then ask Claude:
"Analyze my current project and find relevant documentation"
"Get implementation guidance for user authentication in my React app"
"What are the best practices for my current Django project?"
```

### **Migration & Upgrade Help**

```bash
# Ask Claude:
"Get migration docs for upgrading from React 17 to 18"
"Find Django 4.2 upgrade guide and breaking changes"
"Show me Next.js 13 to 14 migration documentation"
```

### **API Reference with Examples**

```bash
# Ask Claude:
"Get latest pandas DataFrame.merge API reference with examples"
"Show me React useEffect hook documentation and patterns"
"Find Express.js middleware documentation with use cases"
```

## 🛠️ Advanced Setup

### **Warp Terminal Integration**

For enhanced Warp Terminal support:

```bash
# Run Warp-specific setup
chmod +x scripts/setup-warp-dash-mcp.sh
./scripts/setup-warp-dash-mcp.sh

# Use Command Palette (⌘K):
dash-mcp-start
dash-analyze-project
dash-api-ref useState react
```

### **Shell Aliases & Functions**

After setup, you'll have these convenient commands:

```bash
dash-mcp-start              # Start server in tmux
dash-mcp-status             # Check if running
dash-mcp-logs               # View server output
enhanced-dash-mcp-for-project       # Analyze current project
dash-api-lookup <api> <tech> # Plan official Dash MCP searches
dash-best-practices <feature> # Recommend docsets and search routes
dash-help                   # Show all commands
```

### **Powerlevel10k Integration**

Add MCP server status to your prompt:

```bash
# Add to ~/.p10k.zsh (see p10k-dash-mcp.zsh for details)
# Shows 📚 when running, 📕 when stopped
```

## 🔧 Configuration

### **Metadata Index Settings**

```python
# Default index: ~/.cache/dash-mcp/docset-index-v2.json
# Test override: DASH_MCP_INDEX_PATH=/tmp/docset-index.json
# Rebuild: pass force_refresh=true to recommendation/coverage tools
```

### **Official Dash Snapshot**

Pass the official Dash MCP `list_installed_docsets` response to Enhanced Dash
tools when you want exact official docset identifiers in the handoff envelope.

## 🤖 Automation & Non-Interactive Operation

The Enhanced Dash MCP server features comprehensive automation detection and non-interactive operation capabilities, making it suitable for CI/CD pipelines, deployment scripts, and containerized environments.

### **🔍 Interactive Mode Detection Logic**

The server uses an 8-phase detection sequence to determine whether it's running in interactive or automated mode:

#### **Phase 1: CI Environment Detection**
Checks for continuous integration indicators:
```bash
# Primary CI Variables
CI, CONTINUOUS_INTEGRATION, GITHUB_ACTIONS, GITLAB_CI, JENKINS_URL
TRAVIS, CIRCLECI, BUILDKITE, DRONE, BITBUCKET_BUILD_NUMBER
AZURE_HTTP_USER_AGENT, CODEBUILD_BUILD_ID, TEAMCITY_VERSION
# And 15+ more CI environment variables
```

#### **Phase 2: Automation Environment Detection**
Identifies automated/batch processing:
```bash
# Automation Indicators
AUTOMATION, AUTOMATED, NON_INTERACTIVE, BATCH_MODE, HEADLESS
CRON, SYSTEMD_EXEC_PID, KUBERNETES_SERVICE_HOST, DOCKER_CONTAINER
AWS_EXECUTION_ENV, LAMBDA_RUNTIME_DIR, GOOGLE_CLOUD_PROJECT
# Cloud platforms: Heroku, Vercel, Netlify, Railway, etc.
```

#### **Phase 3-8: Terminal & Process Environment**
- **Terminal Type**: Validates `TERM` environment (rejects `dumb`, `unknown`)
- **Shell Capabilities**: Checks for interactive shell support
- **TTY Stream Detection**: Verifies STDIN/STDOUT/STDERR are connected to terminals
- **Process Environment**: Detects daemon processes, nohup, orphaned processes
- **SSH Connections**: Validates TTY allocation in remote connections
- **Session Management**: Recognizes tmux/screen sessions

### **📊 Automation Behavior Matrix**

| Environment Type | Detection Method | Behavior | Logging Level |
|------------------|------------------|----------|---------------|
| **GitHub Actions** | `GITHUB_ACTIONS=true` | Silent, no prompts | INFO |
| **GitLab CI** | `GITLAB_CI=true` | Silent, no prompts | INFO |
| **Docker Build** | `CONTAINER=true` or non-TTY | Silent, no prompts | INFO |
| **Cron Jobs** | `CRON=true` or non-TTY | Silent operation | INFO |
| **SSH Scripts** | `SSH_CONNECTION` without `SSH_TTY` | Non-interactive | INFO |
| **Kubernetes** | `KUBERNETES_SERVICE_HOST` | Pod-aware operation | INFO |
| **AWS Lambda** | `LAMBDA_RUNTIME_DIR` | Serverless mode | DEBUG |
| **Local Terminal** | TTY + interactive shell | Full interaction | DEBUG |

### **⚙️ Automation-Specific Features**

#### **Timeout Protection**
```bash
# All operations have built-in timeouts
Pip installations: 5-10 minute limits
User prompts: 10-second timeout with auto-defaults
Server startup: Quick validation mode for testing
Network operations: Configurable timeouts
```

#### **Signal Handling**
```bash
# Graceful shutdown in automation
SIGINT/SIGTERM: Clean resource cleanup
Keyboard interrupts: Logged and handled gracefully
Partial operations: Automatic rollback/cleanup
Exit codes: Standard automation-friendly codes
```

#### **Non-Interactive Setup**
```bash
# Setup script automation modes
./scripts/setup-dash-mcp.sh    # Auto-detects environment
CI=true ./scripts/setup-dash-mcp.sh    # Force CI mode
BATCH_MODE=true ./scripts/setup-dash-mcp.sh    # Force batch mode
```

### **🔒 Security & Safety**

#### **Environment Validation**
- **Path Sanitization**: Validates and sanitizes all file paths
- **Input Validation**: Comprehensive query and parameter validation
- **Resource Limits**: Memory and CPU usage constraints
- **Rate Limiting**: Built-in request rate limiting (100 calls/minute)

#### **Error Recovery**
```bash
# Robust error handling
Partial installations: Automatic cleanup
Network failures: Retry mechanisms with backoff
Corrupted cache: Automatic cache rebuilding
Docset issues: Graceful degradation
```

### **📈 Performance in Automation**

#### **Benchmarks**
```bash
# Automation environment performance
CI installation time: ~70-80 seconds
Server validation: ~2-3 seconds
Docset discovery: ~500ms (first run), ~50ms (cached)
Timeout response: ~5 seconds maximum
Clean environment setup: ~70-75 seconds
```

#### **Optimization for Automation**
- **Parallel Operations**: Concurrent docset scanning and validation
- **Smart Caching**: Persistent cache survives container restarts
- **Official Handoff**: enhanced tools plan work, then official Dash MCP loads pages
- **Memory Management**: Automatic cleanup of large operations

### **🛠️ Automation Testing**

The server includes comprehensive automation testing:

```bash
# Quick CI compatibility test
./test-ci-automation.sh

# Comprehensive automation validation
./test-final-validation.sh

# Individual component testing
./scripts/test-pip-install.sh
CI=true ./scripts/setup-dash-mcp.sh
env -i PATH=/usr/bin:/bin HOME=$HOME CI=true ./scripts/setup-dash-mcp.sh
```

#### **Test Coverage**
- ✅ **CI Environment Tests**: GitHub Actions, GitLab CI, Jenkins
- ✅ **Container Tests**: Docker builds, Kubernetes pods
- ✅ **Timeout Mechanism Tests**: All operations respect timeouts
- ✅ **Signal Handling Tests**: Graceful interruption and cleanup
- ✅ **Environment Detection Tests**: All 26+ environment variables
- ✅ **Non-Interactive Tests**: Stdin redirection, batch mode

### **📋 Deployment Examples**

#### **GitHub Actions Workflow**
```yaml
- name: Setup Enhanced Dash MCP
  run: |
    git clone <repository-url>
    cd enhanced-dash-mcp
    CI=true ./scripts/setup-dash-mcp.sh
    # No prompts, automatic defaults
```

#### **Docker Container**
```dockerfile
RUN git clone <repository-url> && \\
    cd enhanced-dash-mcp && \\
    CONTAINER=true ./scripts/setup-dash-mcp.sh
# Detects container environment automatically
```

#### **Kubernetes Job**
```yaml
command: ["/bin/bash", "-c"]
args:
  - |
    cd /app/enhanced-dash-mcp
    KUBERNETES_SERVICE_HOST=true ./scripts/setup-dash-mcp.sh
    ./venv/bin/python3 enhanced_dash_server.py --test
```

### **🔍 Debugging Automation Issues**

#### **Log Analysis**
```bash
# View detailed environment detection logs
export DASH_MCP_LOG_LEVEL=DEBUG
./venv/bin/python3 enhanced_dash_server.py --test

# Check automation detection reasoning
grep "Detection reason" ~/.cache/dash-mcp/server.log

# Verify environment variables
grep "Environment summary" ~/.cache/dash-mcp/server.log
```

#### **Common Automation Scenarios**
```bash
# Force interactive mode (testing)
export FORCE_INTERACTIVE=true

# Override environment detection
export DASH_MCP_MODE=interactive  # or 'automation'

# Detailed process information
export DASH_MCP_DEBUG_PROCESS=true
```

## 🏗️ Architecture

### **Core Components**

- **DashMCPServer** - Internal local-cache metadata indexer
- **DashAugmentationServer** - Project-aware recommendation and handoff planner
- **OfficialDocsetIndex** - Optional official Dash snapshot matcher
- **ProjectDocsContext** - Repo context model for languages, frameworks, dependencies, and manifests

### **Data Flow**

1. **Task or repo path received** from Claude via MCP
2. **Project context** analyzed from manifests and source files
3. **Relevant docsets** identified and matched against the optional official snapshot
4. **Official Dash search plans** generated with identifiers when available
5. **Local-only cache gaps** explained only when official Dash cannot see the docset
6. **Handoff envelope returned** for the caller to run official Dash MCP operations

### **Caching Strategy**

- **Persistent Metadata Index** - Stores local docset metadata, not page content
- **Mtime Invalidation** - Rebuilds when the Dash root, `Info.plist`, or `docSet.dsidx` changes
- **Force Refresh** - Recommendation and coverage tools accept `force_refresh=true`

## 📊 Performance

### **Benchmarks**

- **First metadata index**: depends on Dash cache size and docset count
- **Cached metadata reads**: fast JSON load from `docset-index-v2.json`
- **Official search/page loading**: handled by the official Dash MCP, not this server

### **Optimization Tips**

- Keep server running in tmux for best performance
- Pass an official Dash docset snapshot when you need exact identifiers
- Use `force_refresh=false` for routine recommendations
- Use `force_refresh=true` only after installing or moving docsets

## 🔍 Available Tools

| Tool                           | Description                                      | Use Case                         |
| ------------------------------ | ------------------------------------------------ | -------------------------------- |
| `analyze_project_docs_context` | Detect repo stack, manifests, and dependencies   | Understand current project       |
| `recommend_dash_docsets`       | Recommend official/local Dash docsets            | Choose docs for a task           |
| `plan_dash_searches`           | Build official `search_documentation` calls      | Prepare Dash MCP handoff         |
| `rank_dash_results`            | Rank official Dash search results                | Prioritize fetched candidates    |
| `summarize_docset_coverage`    | Compare official-visible and local-cache docsets | Explain app/cache gap            |
| `suggest_offline_docs_for_repo`| Suggest repo-specific offline docs               | Bootstrap project docs workflow  |
| `explain_missing_docsets`      | Explain official/local/missing docset status     | Diagnose missing docs            |

## 🚨 Troubleshooting

### **Common Issues**

**❌ "No docsets found"**

```bash
# Ensure Dash is installed with docsets
ls ~/Library/Application\ Support/Dash/DocSets/
# Should show *.docset directories
# Optionally set DASH_DOCSETS_PATH if your docsets live elsewhere
# (symlinks to the default location are supported)
# When creating a symlink, point it at `~/Library/Application Support/Dash`.
# A symlink directly to the `DocSets` folder will produce a search path
# ending in `DocSets/DocSets` and no docsets will be discovered.
# The server now resolves such symlinks automatically and also corrects
# `DASH_DOCSETS_PATH` values that point at the parent `Dash` directory.
```

**❌ "Permission errors"**

```bash
# Check Python environment
python --version
source ~/enhanced-dash-mcp/venv/bin/activate
```

**❌ "Import errors"**

```bash
# Reinstall dependencies
cd ~/enhanced-dash-mcp
source venv/bin/activate
pip install -r requirements.txt
```

**❌ "Server won't start"**

```bash
# Check if port is in use
tmux kill-session -t dash-mcp
dash-mcp-start
```

**❌ "Slow searches"**

```bash
# First searches build cache - subsequent searches are much faster
# Check cache directory
ls ~/.cache/dash-mcp/
```

### **Debug Mode**

```bash
# View detailed server logs
dash-mcp-logs

# Attach to server session for real-time debugging
dash-mcp-attach
```

## 🤝 Contributing

### **Development Setup**

```bash
# Clone repository
git clone <repository-url>
cd enhanced-dash-mcp

# Create development environment
python -m venv dev-env
source dev-env/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

### **Running Tests**

```bash
# Unit tests
pytest tests/

# Linting and type checks
black .
flake8 .  # uses settings from .flake8
mypy .    # uses settings from mypy.ini
```

### **Adding New Features**

1. **Docset Matching** - Add aliases in `aliases_for_name`
2. **Ranking** - Enhance `rank_results` with more result fields
3. **Project Detection** - Extend manifest parsing in `DashAugmentationServer`
4. **Indexing** - Extend local metadata in `DashMCPServer`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dash** by Kapeli for providing excellent local documentation
- **Anthropic** for Claude and the MCP framework
- **Warp Terminal** for innovative terminal experience
- **Fort Collins Tech Community** for inspiration and feedback

## 📞 Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the `/docs` directory for detailed guides

## 🗺️ Roadmap

### **v1.1 - Enhanced Intelligence**

- [ ] ML-powered documentation relevance scoring
- [ ] Automatic dependency documentation downloads
- [ ] Cross-reference linking between related docs

### **v1.2 - Extended Platform Support**

- [ ] VS Code extension for direct editor integration

### **v1.3 - Advanced Features**

- [ ] Documentation usage analytics and recommendations
- [ ] Team collaboration features for shared documentation
- [ ] Integration with popular documentation hosting platforms

---

**Built with ❤️ in Fort Collins, CO for developers who value efficient, intelligent documentation access.**

_Transform your development workflow with context-aware documentation that understands your project and coding patterns._

## 📚 Further Reading

- [Changelog and CI](docs/changelog_and_ci.md)
- [Server Usage](docs/server_usage.md)
- [AI Agent Guide](AGENTS.md)
