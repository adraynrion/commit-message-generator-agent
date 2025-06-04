#!/bin/bash

# Git Commit Message Generator Agent - Installation Script

echo "🚀 Setting up Git Commit Message Generator Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed."
    exit 1
fi

echo "✅ Python, pip, and git are installed"

# Install uvx
echo "📦 Installing uvx..."
pip install uvx

if [ $? -eq 0 ]; then
    echo "✅ uvx installed successfully"
else
    echo "❌ Failed to install uvx"
    exit 1
fi

# Test MCP git server
echo "🧪 Testing MCP git server..."
timeout 5s uvx mcp-server-git --help > /dev/null 2>&1

if [ $? -eq 0 ] || [ $? -eq 124 ]; then
    echo "✅ MCP git server is accessible"
else
    echo "❌ Failed to access MCP git server"
    exit 1
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Deploy your agent using agent_config.json"
echo "2. Navigate to a git repository"
echo "3. Start using your Git Commit Message Generator Agent!"
echo ""
echo "Example usage:"
echo '  "Please analyze my staged changes and generate a commit message"'
echo ""