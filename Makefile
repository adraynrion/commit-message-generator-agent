.PHONY: clean-imports sort-imports format format-docs type-check all

# Run all code quality checks and formatting
all: clean-imports sort-imports format format-docs type-check
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
type-check:
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
