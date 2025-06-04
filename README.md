# Git Commit Message Generator Agent

This repository contains the configuration and setup files for a specialized AI Agent that analyzes git repository changes and generates high-quality, conventional commit messages. The agent is designed to work directly with the CLI of your current repository to analyze staged changes and suggest appropriate commit messages.

## Quick Start

1. **Set up the git MCP tool**: Follow instructions in `mcp_setup.md`
2. **Deploy your agent**: Use the configuration in `agent_config.json`
3. **Start generating commit messages**: The agent will analyze your repository and suggest commit messages

## Features

- ✅ Conventional commit message generation
- ✅ Git repository analysis via MCP tool
- ✅ Staged changes analysis
- ✅ Multiple commit message suggestions
- ✅ Interactive workflow for staging and committing
- ✅ Support for all conventional commit types

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
"Please analyze my staged changes and generate a commit message"


# 4. Ask for confirmation before committing
```
## Files

| File | Description |
# 1. Use git_diff_staged to analyze changes
# 2. Extract ticket number from branch or ask for it
# 3. Determine appropriate commit type and severity
# 4. Generate formatted commit message
# 5. Ask for confirmation before committing
```

### Example Interaction
```
User: "Please commit my changes"
Agent: "Let me analyze the staged changes using git_diff_staged..."
Agent: "I found changes to authentication module. Based on branch 'AB-1234_oauth-feature':"
Agent: "FEATURE/MEDIUM: AB-1234 - add OAuth2 authentication support

Implement OAuth2 flow with Google and GitHub providers including
user session management and redirect handling for authentication
callbacks."
Agent: "Shall I proceed with this commit?"uctions |
| `setup_instructions.md` | Complete setup guide |

## Git Operations Available

Your agent will be able to perform:
- Repository status checks
- File staging and committing
- Branch creation and management
- Remote operations (push, pull, fetch)
- Viewing diffs and commit history
- Tag management
- And more...

## Next Steps

1. Fill in your custom system prompt in `system_prompt.md`
2. Follow the setup instructions to install the git MCP tool
3. Deploy your agent using your preferred platform
4. Start using your custom AI agent with git capabilities!

## Support

For issues with:
- **MCP Git Tool**: Check the [official MCP servers repository](https://github.com/modelcontextprotocol/servers)
- **Agent Configuration**: Review the setup instructions and configuration files

---
- Repository status analysis (`git_status`) for ticket number extraction
- Staged changes examination (`git_diff_staged`) - primary analysis command
- Unstaged changes review (`git_diff`) when needed
- File staging operations (`git_add`) if requested
- Commit operations with properly formatted messages
## Agent Behavior

The agent is specifically designed to:
- **Never commit automatically**: Only commits when explicitly requested
- **Use git_diff_staged first**: Always analyzes staged changes before generating messages
- **Handle ticket numbers**: Extracts from branch names or asks user for them
- **Follow strict format**: Adheres to `<Type>/<Severity>: <ticket> - <description>` format
- **Wrap text properly**: Maintains 70-character line limit (except code snippets)
- **Confirm actions**: Never commits without explicit user approval
- **Use English only**: All commit messages are in Englishory analysis for context1. Follow the setup instructions to install the git MCP tool
2. Deploy your agent using your preferred platform
3. Navigate to any git repository in your CLI
4. Start using your Git Commit Message Generator Agent!
1. Follow the setup instructions to install the git MCP tool
2. Deploy your agent using your preferred platform
3. Navigate to any git repository in your CLI
4. Start using your Git Commit Message Generator Agent!
- **Analyze before suggesting**: Always examines actual changes before generating messages
- **Follow conventions**: Strictly adheres to conventional commit standards
- **Provide options**: Offers multiple commit message suggestions when appropriate
- **Explain reasoning**: Describes why specific commit types and scopes were chosen
- **Confirm actions**: Never commits without explicit user approval
- **Handle complexity**: Can suggest splitting large changes into multiple focused commits- **Commit Standards**: Refer to [Conventional Commits](https://www.conventionalcommits.org/)*Generate better commit messages with AI! 🤖📝*- **Commit Standards**: Refer to the commit format specifications in `system_prompt.md`

---

*Generate better commit messages with AI! 🤖📝*