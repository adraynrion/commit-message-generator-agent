.PHONY: clean-imports sort-imports format format-docs add-type-annotations type-check test test-cov all

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

# Run tests
test:
	@echo "🧪 Running test suite..."
	@pytest tests/

# Run tests with coverage report
test-cov:
	@echo "📊 Running test suite with coverage..."
	@pytest --cov=commit_message_generator --cov-report=term-missing tests/
