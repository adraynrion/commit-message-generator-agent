# Git Commit Message Generator Agent Setup Instructions

## Overview
This directory contains the configuration for a specialized AI Agent that analyzes git repository changes and generates conventional commit messages. The agent is designed to work with the CLI of your current repository to analyze staged changes and suggest appropriate commit messages.

## Files Structure
- `agent_config.json` - Main configuration file for the Git Commit Message Generator Agent
- `system_prompt.md` - Complete system prompt with commit message generation guidelines
- `mcp_setup.md` - Instructions for setting up the git MCP tool
- `setup_instructions.md` - This file
- `README.md` - Overview and usage guide

## Setup Steps

### 1. Install Prerequisites
Run the installation script to set up the virtual environment and dependencies:
```bash
# Run the installation script
./install.sh
```

Or manually set up the virtual environment:
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

# Verify git installation
git --version
```

### 2. Test MCP Git Server
Verify the MCP git server is accessible (ensure virtual environment is activated):
```bash
# Activate virtual environment first
source .venv/bin/activate

# Test MCP git server
uvx mcp-server-git
```

### 3. Deploy Agent
Use your preferred AI agent deployment platform and reference the `agent_config.json` configuration file. The MCP configuration is already included:

```json
{
  "mcp": {
    "servers": {
      "git": {
        "command": "uvx",
        "args": ["mcp-server-git"]
      }
    }
  }
}
```

### 4. Test Repository Access
Ensure the agent can access git repositories and perform basic operations:
- `git_status` - Check repository status and extract ticket numbers
- `git_diff_staged` - Analyze staged changes
- `git_add` - Stage files
- `git_commit` - Create commits

## Usage Workflow

### 1. Repository Analysis
The agent will:
- Check current repository status
- Identify staged and unstaged changes
- Analyze file types and change patterns

### 2. Commit Message Generation
Based on the analysis, the agent will:
- Determine appropriate commit type (feat, fix, docs, etc.)
- Identify scope (component or area affected)
- Generate descriptive commit messages
- Follow conventional commit standards

### 3. Interactive Assistance
The agent can:
- Suggest staging specific files for focused commits
- Provide multiple commit message options
- Explain the reasoning behind suggestions
- Confirm before executing commits

## Agent Capabilities

Once set up, your agent will have access to:
- Git repository analysis using `git_diff_staged` (primary command)
- Ticket number extraction from branch names
- Commit message generation with format: `<Type>/<Severity>: <ticket> - <description>`
- Interactive commit workflow with user confirmation
- Support for all commit types: FEATURE, IMPROVE, BUGFIX, REFACTO, CORE, TEST, DOC
- Severity assessment: MAJOR, MEDIUM, MINOR
- 70-character line wrapping (except code snippets)
- English-only commit messages

## Commit Format Requirements

The agent generates commits following this exact format:
```
<Commit Type>/<Severity>: <2-letters>-<xxxx> - <description>

Detailed explanation wrapped at 70 characters (code snippets may
exceed this limit).
```

### Ticket Number Handling
- **User provides**: Uses ticket number directly (e.g., "AB-1234")
- **User forgets**: Extracts from branch name pattern `AB-1234_feature-name`
- **Extraction fails**: Asks user to provide ticket number
- **Critical rule**: Never proceeds without valid ticket number

### Commit Types and Severity
- **FEATURE/IMPROVE/BUGFIX/REFACTO**: Severity mandatory (MAJOR/MEDIUM/MINOR)
- **CORE/TEST**: Severity optional
- **DOC**: No severity required

## Customization Options

You can extend this setup by:
- Modifying commit message templates in `system_prompt.md`
- Adding project-specific commit conventions
- Integrating with issue tracking systems
- Adding custom scopes for your project structure

## Best Practices

### For Optimal Results
- Stage related changes together for focused commits
- Ensure branch names follow pattern `<2-letters>-<xxxx>_description` for automatic ticket extraction
- Use the agent only when you want to commit (it never commits automatically)
- Provide ticket numbers explicitly if branch name doesn't contain them
- Review generated messages before confirming

### Repository Requirements
- Ensure you're in a git repository
- Have appropriate git permissions
- Stage files before requesting commit message generation
- Follow branch naming conventions for ticket extraction
- Use English for all commit-related communication

## Critical Usage Rules

1. **Never commits automatically**: Agent only commits when explicitly requested
2. **Always uses git_diff_staged**: Primary command for analyzing changes
3. **Ticket number mandatory**: Must extract or request ticket number
4. **Strict format adherence**: Follows exact `<Type>/<Severity>: <ticket> - <description>` format
5. **English only**: All commit messages generated in English
6. **70-character wrapping**: Maintains proper line length (except code snippets)

## Troubleshooting

### Common Issues
- **Agent can't access git**: Verify MCP tool installation and git availability
- **No staged changes**: Use `git add` to stage files before requesting commit messages
- **Generic messages**: Ensure changes are meaningful and well-structured
- **Permission errors**: Check git repository permissions and user configuration

### Verification Steps
1. Ensure virtual environment is activated: `source .venv/bin/activate`
2. Test uvx installation: `uvx --version`
3. Test MCP git server: `uvx mcp-server-git`
4. Verify git commands manually: `git status`, `git diff --staged`
5. Check agent configuration includes proper MCP setup
6. Test with a simple file change first

### Virtual Environment Notes
- Always activate the virtual environment before using the agent: `source .venv/bin/activate`
- The virtual environment isolates Python dependencies from your system
- Deactivate when done: `deactivate`
- Virtual environment location: `.venv/` directory in the project root

### MCP Configuration Details
The agent uses this MCP configuration:
- **Command**: `uvx` (Python package runner)
- **Args**: `["mcp-server-git"]` (MCP git server package)
- **Primary operations**: `git_status`, `git_diff_staged`, `git_commit`
- **No manual installation**: uvx handles package management automatically
