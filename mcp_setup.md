# Git MCP Tool Setup

## Prerequisites
- Python 3.8 or higher
- Git installed on your system

## Installation Steps

### 1. Create and Activate Virtual Environment
Create a Python virtual environment to isolate dependencies:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Activate virtual environment (Windows)
.venv\Scripts\activate
```

### 2. Install uvx
Install uvx in the virtual environment:
```bash
# Ensure virtual environment is activated
pip install --upgrade pip

# Option 1: Install from requirements.txt
pip install -r requirements.txt

# Option 2: Install uvx directly
pip install uvx
```

### 3. Verify Git Installation
Ensure git is installed and accessible:
```bash
git --version
```

### 4. Test MCP Git Server
Test that the MCP git server can be accessed (ensure virtual environment is activated):
```bash
uvx mcp-server-git
```

### 5. Configuration
The git MCP tool provides the following capabilities:
- Repository status checking (`git_status`)
- File staging and committing (`git_add`, `git_commit`)
- Branch management (`git_branch`, `git_checkout`)
- Remote operations (`git_push`, `git_pull`, `git_fetch`)
- Diff viewing (`git_diff`, `git_diff_staged`)
- Log history (`git_log`)
- Tag management (`git_tag`)

### 6. Integration with AI Agent
Add the following to your agent's MCP configuration:

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

### 7. Available Git Operations
Once configured, your agent will have access to these git operations:
- `git_status` - Check repository status and extract ticket numbers from branch names
- `git_diff_staged` - **Primary command** for analyzing staged changes
- `git_diff` - View unstaged differences
- `git_add` - Stage files for commit
- `git_commit` - Create commits with generated messages
- `git_push` - Push changes to remote
- `git_pull` - Pull changes from remote
- `git_branch` - Branch management
- `git_checkout` - Switch branches/checkout files
- `git_log` - View commit history
- `git_tag` - Tag management
- `git_reset` - Reset changes
- `git_merge` - Merge branches

### 8. Agent-Specific Usage
For the Git Commit Message Generator Agent, the primary workflow uses:
1. **`git_status`** - Extract ticket number from branch name
2. **`git_diff_staged`** - Analyze staged changes (most important command)
3. **`git_commit`** - Execute commit with generated message

### 9. Security Considerations
- The git MCP tool operates on the local repository
- Ensure proper access controls are in place
- Be cautious with destructive operations (reset, force push)
- The agent will never commit without explicit user permission
- Consider using branch protection rules for important branches

### 10. Troubleshooting
- Ensure the virtual environment is activated: `source .venv/bin/activate`
- Ensure uvx is properly installed in the virtual environment: `uvx --version`
- Check that git is properly installed and accessible in PATH: `git --version`
- Verify the MCP server starts correctly: `uvx mcp-server-git`
- Check repository permissions and git configuration
- Ensure you're in a valid git repository when using the agent

## Virtual Environment Management

### Activating the Environment
Before using the agent, always activate the virtual environment:
```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Deactivating the Environment
When done, deactivate the virtual environment:
```bash
deactivate
```

### Verifying Installation
Check that uvx is available in the virtual environment:
```bash
# Ensure virtual environment is activated
which uvx  # Should point to .venv/bin/uvx
uvx --version
```

## Usage Examples
Once set up, you can ask your agent to perform git operations like:
- "Analyze my staged changes and generate a commit message"
- "Check the current git status and extract the ticket number"
- "Generate a commit message for ticket AB-1234"
- "Commit these changes with the generated message"
