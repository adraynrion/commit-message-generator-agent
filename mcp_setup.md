# Git MCP Tool Setup

## Prerequisites
- Node.js (version 16 or higher)
- npm or yarn package manager
- Git installed on your system

## Installation Steps

### 1. Clone the MCP Servers Repository
```bash
git clone https://github.com/modelcontextprotocol/servers.git
cd servers/src/git
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Build the Git MCP Tool
```bash
npm run build
```

### 4. Configuration
The git MCP tool provides the following capabilities:
- Repository status checking
- File staging and committing
- Branch management
- Remote operations (push, pull, fetch)
- Diff viewing
- Log history
- Tag management

### 5. Integration with AI Agent
Add the following to your agent's MCP configuration:

```json
{
  "mcpServers": {
    "git": {
      "command": "node",
      "args": ["path/to/servers/src/git/dist/index.js"],
      "env": {}
    }
  }
}
```

### 6. Available Git Operations
Once configured, your agent will have access to these git operations:
- `git_status` - Check repository status
- `git_add` - Stage files for commit
- `git_commit` - Create commits
- `git_push` - Push changes to remote
- `git_pull` - Pull changes from remote
- `git_branch` - Branch management
- `git_checkout` - Switch branches/checkout files
- `git_diff` - View differences
- `git_log` - View commit history
- `git_tag` - Tag management
- `git_reset` - Reset changes
- `git_merge` - Merge branches

### 7. Security Considerations
- The git MCP tool operates on the local repository
- Ensure proper access controls are in place
- Be cautious with destructive operations (reset, force push)
- Consider using branch protection rules for important branches

### 8. Troubleshooting
- Ensure git is properly installed and accessible in PATH
- Check that the MCP server is running and accessible
- Verify repository permissions
- Check for any git configuration issues

## Usage Examples
Once set up, you can ask your agent to perform git operations like:
- "Check the current git status"
- "Commit these changes with message 'Fix bug in authentication'"
- "Create a new branch called 'feature/new-ui'"
- "Push changes to the main branch"