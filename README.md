[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/joshuadanpeterson-enhanced-dash-mcp-badge.png)](https://mseep.ai/app/joshuadanpeterson-enhanced-dash-mcp)

# Enhanced Dash MCP Server

![Version](https://img.shields.io/badge/version-1.3.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/joshuadanpeterson/enhanced-dash-mcp)

## 🎯 What is this?

This is a **Model Context Protocol (MCP)** server that bridges [Dash](https://kapeli.com/dash) - the popular offline API documentation browser for macOS - with Claude Desktop and other agentic development environments. MCP is an open protocol that enables AI assistants like Claude and Warp to securely access local resources and tools on your computer through structured APIs.

**In simple terms:** This server lets Claude and other agentic coding tools instantly search and read your local Dash documentation (200+ API docs, cheat sheets, and guides) to provide accurate, version-specific answers based on the actual documentation you have installed - all offline, private, and blazing fast.

## 📚 About Dash

[Dash](https://kapeli.com/dash) is an API Documentation Browser and Code Snippet Manager for macOS that gives you instant offline access to 200+ API documentation sets. It's the go-to tool for developers who want fast, searchable, offline documentation without relying on internet connectivity or dealing with slow web searches.

## 🔗 Why This Integration Matters

- **Offline-First**: Access all your documentation without internet connectivity
- **Version-Specific**: Get answers based on the exact versions of libraries you have installed
- **Privacy-Focused**: Your code context and queries never leave your machine
- **Lightning Fast**: Sub-second searches through gigabytes of documentation
- **Context-Aware**: Claude understands your project stack and suggests relevant docs automatically

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 🚀 Features

### **Core Capabilities**

- **🔍 Intelligent Search** - Fuzzy matching with typo tolerance and smart ranking
- **📚 Content Extraction** - Clean text extraction from HTML, Markdown, and text docs
- **⚡ Multi-Tier Caching** - Memory + disk caching for lightning-fast repeated searches
- **🎯 Project Awareness** - Automatically detects your tech stack and prioritizes relevant docs
- **🛠️ Implementation Guidance** - Best practices and patterns for specific features
- **📈 Migration Support** - Version upgrade documentation and breaking changes
- **🔄 Latest API Reference** - Current API docs with practical examples

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
- **Python 3.8+** (Python 3.11+ recommended)
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
- `beautifulsoup4>=4.12.0` - HTML content extraction
- `fuzzywuzzy>=0.18.0` - Fuzzy string matching
- `python-levenshtein>=0.27.0` - Fast string similarity
- `aiofiles>=24.0.0` - Async file operations
- `aiohttp>=3.11.0` - Async HTTP client
- `rapidfuzz>=3.0.0` - Enhanced fuzzy matching
- `typing-extensions>=4.12.0` - Extended type hints

## ⚡ Quick Start

### 🔄 **Important: Cache Clearing for Existing Users**

**If you're upgrading from a previous version**, the server now discovers 8x more docsets (364 instead of 45) by searching the entire Dash directory tree. To see all the new docsets, clear the cache:

```bash
# Clear the docset cache to discover newly available docsets
rm -rf ~/.cache/dash-mcp/

# Then restart your server
dash-mcp-restart
# or
cd ~/enhanced-dash-mcp && ./start-dash-mcp.sh --test
```

**What changed:**
- **Before**: Searched only `~/Library/Application Support/Dash/DocSets/` (45 docsets)
- **After**: Searches entire `~/Library/Application Support/Dash/` directory (364 docsets)
- **Benefit**: Now includes User Contributed, Python DocSets, Versioned DocSets, and more!

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
dash-api-lookup <api> <tech> # Quick API reference
dash-best-practices <feature> # Implementation guidance
dash-help                   # Show all commands
```

### **Powerlevel10k Integration**

Add MCP server status to your prompt:

```bash
# Add to ~/.p10k.zsh (see p10k-dash-mcp.zsh for details)
# Shows 📚 when running, 📕 when stopped
```

## 🔧 Configuration

### **Cache Settings**

```python
# Default cache TTL: 1 hour
# Cache location: ~/.cache/dash-mcp/
# Memory + disk caching for optimal performance
```

### **Fuzzy Search Tuning**

```python
# Default threshold: 60% match
# Adjustable in server configuration
# Typo tolerance with intelligent ranking
```

### **Content Extraction Limits**

```python
# Default: 5000 characters per document
# Configurable for performance vs. detail trade-off
```

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
- **Lazy Loading**: On-demand content extraction
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
    python3 enhanced_dash_server.py --test
```

### **🔍 Debugging Automation Issues**

#### **Log Analysis**
```bash
# View detailed environment detection logs
export DASH_MCP_LOG_LEVEL=DEBUG
python3 enhanced_dash_server.py --test

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

- **DashMCPServer** - Main server orchestrating all components
- **CacheManager** - Multi-tier caching (memory + disk)
- **ContentExtractor** - Clean text extraction from various formats
- **FuzzySearchEngine** - Intelligent search with ranking algorithms
- **ProjectAwareDocumentationServer** - Context-aware documentation selection

### **Data Flow**

1. **Query received** from Claude via MCP
2. **Project context** analyzed (language, framework, dependencies)
3. **Relevant docsets** identified and prioritized
4. **Fuzzy search** performed with intelligent ranking
5. **Content extracted** and cached for future requests
6. **Results returned** with project-specific scoring

### **Caching Strategy**

- **Memory Cache** - Instant access for recently searched items
- **Disk Cache** - Persistent storage surviving server restarts
- **Smart Expiration** - 1-hour TTL with automatic cleanup
- **Cache Keys** - Generated from search parameters for optimal hit rates

## 📊 Performance

### **Benchmarks**

- **First search**: ~500ms (includes docset scanning)
- **Cached searches**: ~50ms (memory cache hits)
- **Content extraction**: +200-300ms (when requested)
- **Fuzzy matching**: Minimal overhead with significant quality improvement

### **Optimization Tips**

- Keep server running in tmux for best performance
- Initial searches per docset are slower (cache building)
- Content extraction adds latency but provides much richer context
- Memory cache provides fastest repeated access

## 🔍 Available Tools

### **Core Search Tools**

| Tool               | Description                                    | Use Case                         |
| ------------------ | ---------------------------------------------- | -------------------------------- |
| `search_dash_docs` | Basic documentation search with fuzzy matching | General API/concept lookup       |
| `list_docsets`     | Show all available documentation sets          | Discover available documentation |
| `get_doc_content`  | Get full content for specific documentation    | Deep dive into specific topics   |

### **Project-Aware Tools**

| Tool                          | Description                                | Use Case                           |
| ----------------------------- | ------------------------------------------ | ---------------------------------- |
| `analyze_project_context`     | Detect project tech stack and dependencies | Understand current project         |
| `get_project_relevant_docs`   | Context-aware documentation search         | Find docs relevant to your project |
| `get_implementation_guidance` | Best practices for specific features       | Implementation planning            |

### **Specialized Tools**

| Tool                       | Description                    | Use Case                         |
| -------------------------- | ------------------------------ | -------------------------------- |
| `get_migration_docs`       | Version upgrade documentation  | Planning upgrades and migrations |
| `get_latest_api_reference` | Current API docs with examples | Quick reference while coding     |

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
which python3
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
python3 -m venv dev-env
source dev-env/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
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

1. **Docset Support** - Add new file format extractors in `ContentExtractor`
2. **Search Algorithms** - Enhance ranking in `FuzzySearchEngine`
3. **Project Detection** - Extend framework detection in `ProjectAwareDocumentationServer`
4. **Caching Strategies** - Optimize cache management in `CacheManager`

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
