.DEFAULT_GOAL := all

############################################
# Code quality checks and formatting
############################################
.PHONY: clean-imports sort-imports format format-docs add-type-annotations type-check all

# Run all code quality checks and formatting
all: clean-imports sort-imports format format-docs add-type-annotations type-check
	@echo "✨ All code quality checks and formatting complete!"

# Remove unused imports
clean-imports:
	@echo "🚀 Removing unused imports..."
	@pycln . --config pyproject.toml -a

# Sort imports
sort-imports:
	@echo "🔍 Sorting imports..."
	@isort .

# Format code with Black
format:
	@echo "💅 Formatting code with Black..."
	@black .

# Format docstrings
format-docs:
	@echo "📝 Formatting docstrings..."
	@docformatter --in-place --recursive .

# Add type annotations to specific directories and root Python files
add-type-annotations:
	@echo "🔍 Adding type annotations..."
	@# Process root directory Python files (non-recursive)
	@echo "  • Processing root directory..."
	@find . -maxdepth 1 -type f -name '*.py' -print0 | xargs -0 autotyping --safe >/dev/null 2>&1
	@# Process Python files in specified directories (recursively)
	@for dir in commit_message_generator hooks tests; do \
		if [ -d "$$dir" ]; then \
			echo "  • Processing directory: $$dir"; \
			find "$$dir" -type f -name '*.py' -print0 | xargs -0 autotyping --safe >/dev/null 2>&1; \
		else \
			echo "  ⚠️  Directory '$$dir' not found, skipping..."; \
		fi; \
	done
	@echo "✅ Type annotations added successfully"

# Run static type checking with mypy
type-check:
	@echo "🔍 Running static type checking with mypy..."
	@mypy .
	@echo "✅ Type checking complete"

############################################
# Tests
############################################
.PHONY: test test-cov

# Run tests
test:
	@echo "🧪 Running test suite..."
	@pytest tests/

# Run tests with coverage report
test-cov:
	@echo "📊 Running test suite with coverage..."
	@pytest --cov=commit_message_generator --cov-report=term-missing tests/

############################################
# Build
############################################
.PHONY: build clean-build clean-dist clean-cache clean-all clean

# Build the application
build:
	@echo "🏗️ Building the application..."
	@pyinstaller commit_message_generator.spec --clean
	@echo "✅ Build complete"

# Clean build artifacts
clean-build:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/

# Clean distribution artifacts
clean-dist:
	@echo "🗑️  Cleaning distribution artifacts..."
	@rm -rf dist/

# Clean cache and temporary files
clean-cache:
	@echo "🧽 Cleaning cache and temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -delete
	@find . -type f -name "*.so" -delete

# Clean everything
clean-all: clean-build clean-dist clean-cache
	@echo "✨ All clean!"

# Alias for clean-all
clean: clean-all

############################################
# Virtual environment
############################################
.PHONY: venv

# Create a virtual environment
venv:
	@echo "🐍 Creating virtual environment..."
	@python -m venv .venv
	@echo "✅ Virtual environment created"

# Clean virtual environment
clean-venv:
	@echo "🗑️  Cleaning virtual environment..."
	@rm -rf .venv
	@echo "✅ Virtual environment cleaned"

# Reset virtual environment
reset-venv: clean-venv venv
	@echo "🔄 Resetting virtual environment..."
	@pip install --upgrade pip
	@pip install -e .
	@echo "✅ Virtual environment reset"

############################################
# Version Management
############################################
.PHONY: bump-version

# Version to bump to (e.g., make bump-version VERSION=1.2.3)
VERSION ?=

# File containing the version
VERSION_FILE = commit_message_generator/__init__.py

# Bump version and create Git tag
# Usage: make bump-version VERSION=x.y.z
bump-version:
ifndef VERSION
	$(error VERSION is not set. Usage: make bump-version VERSION=x.y.z)
endif
	@echo "🆙 Bumping version to $(VERSION)..."
	@# Update version in __init__.py
	@sed -i "s/^__version__ = .*/__version__ = \"$(VERSION)\"/" $(VERSION_FILE)
	@# Stage the version change
	@git add $(VERSION_FILE)
	@# Create commit
	@git commit -m "Bump version to $(VERSION)"
	@# Create annotated tag
	@git tag -a "v$(VERSION)" -m "Version $(VERSION)"
	@echo "✅ Version bumped to $(VERSION) and tagged as v$(VERSION)"
	@echo "📌 Don't forget to push the tag: git push origin v$(VERSION)"
