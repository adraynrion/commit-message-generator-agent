#!/bin/bash

# Git Commit Message Generator Agent - Installation Script

echo "🚀 Setting up Git Commit Message Generator Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed."
    exit 1
fi

echo "✅ Python and git are installed"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activated"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip in virtual environment
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully in virtual environment"
else
    echo "❌ Failed to install dependencies"
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
echo "📝 Important: Virtual environment created at .venv/"
echo "   To activate it manually: source .venv/bin/activate"
echo "   To deactivate: deactivate"
echo ""
echo "Next steps:"
echo "1. Deploy your agent using agent_config.json"
echo "2. Navigate to a git repository"
echo "3. Start using your Git Commit Message Generator Agent!"
echo ""
echo "Example usage:"
echo '  "Please analyze my staged changes and generate a commit message"'
echo ""
