# PyInstaller Build Guide

This document provides instructions for building a standalone executable of the Commit Message Generator using PyInstaller.

## Prerequisites

- Python 3.11.9
- pip
- Git (for cloning the repository)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/commit-message-generator.git
cd commit-message-generator
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Building the Executable

### Basic Build

To build the executable with default settings:

```bash
make build
```

This will create a standalone executable in the `dist/commit-message-generator` directory.

### Cleaning Up

- Clean build artifacts:
```bash
make clean-build
```

- Clean distribution files:
```bash
make clean-dist
```

- Clean everything (build, dist, cache):
```bash
make clean
```

## Advanced Configuration

### PyInstaller Hooks

The following custom hooks are included to handle specific packaging requirements:

- `hook-pydantic.py`: Handles Pydantic imports and dependencies
- `hook-logfire.py`: Handles Logfire and OpenTelemetry dependencies
- `rthook-pydantic.py`: Runtime hook for Pydantic initialization
- `fix_pydantic_imports.py`: Fixes import issues with Pydantic in frozen applications

### Customizing the Build

You can modify the `commit_message_generator.spec` file to customize the build process. Common customizations include:

- Adding data files with `datas`
- Including additional hidden imports with `hiddenimports`
- Configuring the output directory and file name
- Setting up code signing (for macOS/Windows)

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
  - Ensure all required packages are installed in your virtual environment
  - Check the build output for any missing module warnings

2. **Import Errors**
  - If you see import errors for Pydantic or Logfire, try cleaning and rebuilding:
```bash
make clean
make build
```

3. **Large Executable**
  - The executable might be large due to including all dependencies
  - Consider using `--exclude-module` in the spec file for unused modules

### Debugging

To get more verbose output during the build:

```bash
pyinstaller --clean --log-level=DEBUG commit_message_generator.spec
```

## Distribution

The built executable is self-contained and can be distributed by packaging the contents of the `dist/commit-message-generator` directory.

### Creating a Distribution Package

1. Build the application:
```bash
make build
```

2. Create a zip archive of the distribution:
```bash
cd dist
zip -r commit-message-generator-$(python -c "from commit_message_generator import __version__; print(__version__)")-$(uname -s)-$(uname -m).zip commit-message-generator/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
