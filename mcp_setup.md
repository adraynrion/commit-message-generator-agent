# Git MCP Tool Setup

## Prerequisites
- Python 3.8 or higher
- uvx (Python package runner)
- Git installed on your system

## Installation Steps

### 1. Install uvx
If you don't have uvx installed, install it using pip:
```bash
pip install uvx
```

### 2. Verify Git Installation
Ensure git is installed and accessible:
```bash
git --version
```

### 3. Test MCP Git Server
Test that the MCP git server can be accessed:
```bash
uvx mcp-server-git
```

### 4. Configuration
The git MCP tool provides the following capabilities:
- Repository status checking (`git_status`)
- File staging and committing (`git_add`, `git_commit`)
- Branch management (`git_branch`, `git_checkout`)
- Remote operations (`git_push`, `git_pull`, `git_fetch`)
- Diff viewing (`git_diff`, `git_diff_staged`)
- Log history (`git_log`)
- Tag management (`git_tag`)

### 5. Integration with AI Agent
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

### 6. Available Git Operations
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

### 7. Agent-Specific Usage
For the Git Commit Message Generator Agent, the primary workflow uses:
1. **`git_status`** - Extract ticket number from branch name
2. **`git_diff_staged`** - Analyze staged changes (most important command)
3. **`git_commit`** - Execute commit with generated message

### 8. Security Considerations
- The git MCP tool operates on the local repository
- Ensure proper access controls are in place
- Be cautious with destructive operations (reset, force push)- The agent will never commit without explicit user permission- Consider using branch protection rules for important branches

### 9. Troubleshooting
- Ensure uvx is properly installed: `uvx --version`
- Check that git is properly installed and accessible in PATH: `git --version`
- Verify the MCP server starts correctly: `uvx mcp-server-git`
- Check repository permissions and git configuration
- Ensure you're in a valid git repository when using the agent

## Usage Examples
Once set up, you can ask your agent to perform git operations like:
- "Analyze my staged changes and generate a commit message"
- "Check the current git status and extract the ticket number"
- "Generate a commit message for ticket AB-1234"
- "Commit these changes with the generated message"