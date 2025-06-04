# Git Commit Message Generator Agent

This repository contains the configuration and setup files for a specialized AI Agent that analyzes git repository changes and generates high-quality, conventional commit messages. The agent is designed to work directly with the CLI of your current repository to analyze staged changes and suggest appropriate commit messages.

## Quick Start

### Option 1: Automated Installation (Recommended)
```bash
# Run the installation script (creates virtual environment)
chmod +x install.sh
./install.sh

# Activate the environment when needed
source .venv/bin/activate
```

### Option 2: Manual Installation
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies from requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Test MCP server
uvx mcp-server-git --help

# Deploy your agent using agent_config.json
```

### Virtual Environment Management
- **Activate**: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
- **Deactivate**: `deactivate`

## Features

- ✅ Conventional commit message generation with custom format
- ✅ Git repository analysis via uvx MCP tool
- ✅ Staged changes analysis using `git_diff_staged`
- ✅ Automatic ticket number extraction from branch names
- ✅ Interactive workflow for staging and committing
- ✅ Support for all commit types (FEATURE, IMPROVE, BUGFIX, etc.)
- ✅ Severity assessment (MAJOR, MEDIUM, MINOR)
- ✅ English-only commit messages with 70-character wrapping

## How It Works

The agent follows this strict workflow:
1. **Waits for explicit commit request** (never commits automatically)
2. **Analyzes staged changes** using `git_diff_staged` command
3. **Extracts ticket number** from branch name or asks user for it
4. **Determines commit type and severity** based on change analysis
5. **Generates formatted commit message** following exact specifications
6. **Asks for confirmation** before any commit operation

## Ticket Number Handling

The agent handles ticket numbers intelligently:
- **If you provide** the ticket number in format `AB-1234`, it uses it directly
- **If you forget**, it extracts from branch name pattern `AB-1234_feature-name`
- **If extraction fails**, it will ask you to provide the ticket number
- **Format in commit**: Always formatted as `AB-1234 -` in the commit message

## Commit Message Format

The agent follows a specific commit message format:
```
<Commit Type>/<Severity>: <2-letters>-<xxxx> - <description>

Detailed explanation wrapped at 70 characters (code snippets may
exceed this limit).
```

## Commit Types Supported

| Type | Description | Severity Required | Example |
|------|-------------|-------------------|---------|
| `FEATURE` | New features added to the project | **Mandatory** | `FEATURE/MEDIUM: AB-1234 - add OAuth2 login` |
| `IMPROVE` | Improvements or optimizations | **Mandatory** | `IMPROVE/MINOR: CD-5678 - optimize database queries` |
| `BUGFIX` | Bug fixes or production solutions | **Mandatory** | `BUGFIX/MAJOR: EF-9012 - fix null pointer exception` |
| `REFACTO` | Code refactoring without behavior change | **Mandatory** | `REFACTO/MINOR: GH-3456 - extract validation logic` |
| `CORE` | Core development system changes | **Optional** | `CORE/MAJOR: IJ-7890 - upgrade Node.js to v18` |
| `TEST` | Test modifications or additions | **Optional** | `TEST: KL-2468 - add unit tests for auth` |
| `DOC` | Documentation updates | **Not required** | `DOC: MN-1357 - update setup instructions` |

## Severity Levels

| Severity | Description |
|----------|-------------|
| `MAJOR` | Major change with significant project-wide impact or potential regressions |
| `MEDIUM` | Medium-sized change affecting specific area without major system impact |
| `MINOR` | Minor update like small bug fixes, performance improvements, or cosmetic adjustments |

## Usage Examples

### Basic Usage
```bash
# Stage your changes
git add .

# Ask the agent to generate commit messages
"Please analyze my staged changes and suggest commit messages"
```

### Interactive Workflow
```bash
# The agent will:
# 1. Check git status
# 2. Analyze staged changes
# 3. Generate commit message
# 4. Ask for confirmation before committing
"Please analyze my staged changes and generate a commit message"
```

## Files

| File | Description |
|------|-------------|
| `agent_config.json` | Complete agent configuration with MCP setup |
| `mcp_config.json` | Standalone MCP configuration for git tool |
| `system_prompt.md` | Complete system prompt for commit message generation |
| `mcp_setup.md` | Git MCP tool setup instructions using uvx |
| `setup_instructions.md` | Complete setup guide |
| `install.sh` | Automated installation script with virtual environment |
| `requirements.txt` | Python dependencies for the project |
| `.gitignore` | Git ignore file excluding virtual environment |

## Example Interaction
```
User: "Please commit my changes"
Agent: "Let me analyze the staged changes using git_diff_staged..."
Agent: "I found changes to authentication module. Based on branch 'AB-1234_oauth-feature':"
Agent: "FEATURE/MEDIUM: AB-1234 - add OAuth2 authentication support

Implement OAuth2 flow with Google and GitHub providers including
user session management and redirect handling for authentication
callbacks."
Agent: "Shall I proceed with this commit?"
```

## Git Operations Available

Your agent will be able to perform:
- Repository status checks
- File staging and committing
- Branch creation and management
- Remote operations (push, pull, fetch)
- Viewing diffs and commit history
- Tag management
- And more...

## Agent Behavior

The agent is specifically designed to:
- **Never commit automatically**: Only commits when explicitly requested
- **Use git_diff_staged first**: Always analyzes staged changes before generating messages
- **Handle ticket numbers**: Extracts from branch names or asks user for them
- **Follow strict format**: Adheres to `<Type>/<Severity>: <ticket> - <description>` format
- **Wrap text properly**: Maintains 70-character line limit (except code snippets)
- **Confirm actions**: Never commits without explicit user approval
- **Use English only**: All commit messages are in English
- **Analyze before suggesting**: Always examines actual changes before generating messages
- **Follow conventions**: Strictly adheres to conventional commit standards
- **Provide options**: Offers multiple commit message suggestions when appropriate
- **Explain reasoning**: Describes why specific commit types and scopes were chosen

## Next Steps

1. Follow the setup instructions to install the git MCP tool
2. Deploy your agent using your preferred platform
3. Navigate to any git repository in your CLI
4. Start using your Git Commit Message Generator Agent!

## Support

For issues with:
- **MCP Git Tool**: Check the [official MCP servers repository](https://github.com/modelcontextprotocol/servers)
- **Agent Configuration**: Review the setup instructions and configuration files
- **Commit Standards**: Refer to the commit format specifications in `system_prompt.md`

---

*Generate better commit messages with AI! 🤖📝*
