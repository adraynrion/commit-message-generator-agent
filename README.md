# Git Commit Message Generator Agent

[![Python Version](https://img.shields.io/badge/python-3.11.9-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checker: mypy](https://img.shields.io/badge/type%20checker-mypy-blueviolet)](http://mypy-lang.org/)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-ff69b4)](https://flake8.pycqa.org/)
[![Testing: pytest](https://img.shields.io/badge/testing-pytest-0d8fcc)](https://docs.pytest.org/)
[![Coverage](https://github.com/adraynrion/commit-message-generator-agent/actions/workflows/test.yml/badge.svg?branch=main&event=push)](https://github.com/adraynrion/commit-message-generator-agent/actions/workflows/test.yml)

An AI-powered CLI tool that helps generate clear, concise, and conventional commit messages based on your git changes.

## ✨ Features

- 🤖 **AI-Powered** - Uses advanced language models to understand code changes
- 🔍 **Smart Analysis** - Analyzes git diffs to understand changes in context
- 🎨 **Beautiful Output** - Rich terminal formatting with syntax highlighting
- 🧪 **Type Hints** - Full type annotations for better development experience

## 📦 Installation

### Using pip

```bash
pip install git+https://github.com/adraynrion/commit-message-generator-agent.git
```

### Development Installation

1. Clone the repository:
```bash
git clone https://github.com/adraynrion/commit-message-generator-agent.git
cd commit-message-generator-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install in development mode with all dependencies:
```bash
pip install -e '.[dev]'
```

## 🚀 Quick Start

1. **Initialize Configuration** (optional):
```bash
mkdir -p ~/.config/commit-msg-gen
cp commit_message_generator/default_config.yaml ~/.config/commit-msg-gen/config.yaml
# Edit the config file as needed
```

2. **Set up your OpenAI API key** (required):
```bash
echo 'OPENAI_API_KEY=your-api-key-here' > .env
```
Or add it to your environment variables.

3. **Generate a commit message** for your staged changes:
```bash
# Stage your changes
git add .

# Generate and review the commit message
commit-msg-gen generate -t AB-12aze34
```

## 🛠️ Configuration

Create a `config.yaml` file in one of these locations:

1. `./config.yaml` (current directory)
2. `~/.config/commit-msg-gen/config.yaml` (user config)
3. `/etc/commit-msg-gen/config.yaml` (system config)

Example configuration (see [default_config.yaml](commit_message_generator/default_config.yaml) for all options):

```yaml
# AI model configuration
ai:
  model_name: "gpt-4o-mini"  # or "gpt-3.5-turbo" for faster/cheaper results
  temperature: 0.3  # 0.0 to 2.0, higher is more creative/random
  max_tokens: 1000  # Maximum length of the generated message
  top_p: 1.0        # Nucleus sampling parameter (0.0 to 1.0)
  max_attempts: 3   # Maximum number of attempts to generate a valid commit message

# Commit message settings
commit:
  max_line_length: 80  # Wrap commit message at this length

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "commit_gen.log"  # Leave empty to log to console only

# Optional: Langfuse configuration for tracing and observability
langfuse:
  enabled: false  # Set to true to enable Langfuse tracing
  public_key: ""
  secret_key: ""
  host: "https://cloud.langfuse.com"
```

## 📝 Usage

```bash
# Generate a commit message for staged changes with a ticket number
commit-msg-gen generate --ticket AB-12aze34

# Enable verbose output
commit-msg-gen generate --ticket AB-12aze34 --verbose

# Show help
commit-msg-gen --help
commit-msg-gen generate --help
```

## 🔌 Build & Packaging

### Prerequisites

1. Install Ubuntu dependencies:
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    liblzma-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    tk-dev \
    libgdbm-dev \
    libc6-dev \
    libgdbm-compat-dev
```

2. Use pyenv and install Python 3.11:
```bash
pyenv install 3.11.9
pyenv global 3.11.9
```

3. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install the package in development mode with all dependencies:
```bash
pip install -e '.[dev]'
```

### Building with PyInstaller

For detailed instructions on building a standalone executable with PyInstaller, see our [PyInstaller Guide](README-PYINSTALLER.md).

#### Quick Start

1. Clean the repository:
```bash
make clean
```

2. Build the application:
```bash
make build
```

The standalone executable will be available in the `dist/commit-message-generator` directory.

## 🔌 API

You can also use the generator programmatically:

```python
import asyncio
from commit_message_generator import CommitMessageGenerator

async def main():
    # Initialize the generator
    generator = CommitMessageGenerator()

    # Generate a commit message
    commit_message = await generator.generate_commit_message(
        diff="""diff --git a/file.txt b/file.txt
        index 1234567..89abcde 100644
        --- a/file.txt
        +++ b/file.txt
        @@ -1 +1,2 @@
          Hello, world!
        +This is a new line.""",
        ticket="ABC-123"  # Optional: Include a ticket number
    )
    print(commit_message)

# Run the async function
asyncio.run(main())
```

## 🧪 Testing

Run the test suite:

```bash
make test
```

Run with coverage:

```bash
make test-cov
```

## 🛠️ Code Quality

We use several tools to maintain code quality. All commands can be run via the Makefile:

1. **Remove unused imports**:
```bash
make clean-imports
```

2. **Sort imports**:
```bash
make sort-imports
```

3. **Format code with Black**:
```bash
make format
```

4. **Format docstrings**:
```bash
make format-docs
```

5. **Add type annotations** (review changes carefully):
```bash
make add-type-annotations
```

6. **Run all code quality checks and formatting**:
```bash
make all
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Click](https://click.palletsprojects.com/)
- [Rich](https://github.com/Textualize/rich)
