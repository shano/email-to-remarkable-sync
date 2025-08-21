# Makefile for email-to-remarkable-sync (Poetry edition)

.PHONY: help install test test-coverage lint format type-check clean build publish setup all-checks pre-commit

# Default target
help:
	@echo "Available commands:"
	@echo "  help          Show this help message"
	@echo "  install       Install dependencies with Poetry"
	@echo "  install-dev   Install with dev dependencies (alias for install)"
	@echo "  test          Run tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run linting (flake8)"
	@echo "  format        Format code (black + isort)"
	@echo "  format-check  Check code formatting without making changes"
	@echo "  type-check    Run type checking (mypy)"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package with Poetry"
	@echo "  setup         Setup development environment"
	@echo "  shell         Activate Poetry shell"
	@echo "  update        Update dependencies"
	@echo "  show          Show package information"
	@echo "  all-checks    Run all quality checks (lint, format-check, type-check, test)"
	@echo "  pre-commit    Run pre-commit hooks"

# Setup development environment
setup:
	@echo "Setting up development environment with Poetry..."
	poetry install
	@echo "Installing pre-commit hooks..."
	-poetry run pre-commit install
	@echo "Development environment setup complete!"

# Install dependencies
install:
	poetry install

# Alias for install (backwards compatibility)
install-dev: install

# Run tests
test:
	poetry run pytest tests/ -v

# Run tests with coverage
test-coverage:
	poetry run pytest tests/ -v --cov=email_to_remarkable --cov-report=term-missing --cov-report=html

# Run linting
lint:
	poetry run flake8 email_to_remarkable.py tests/

# Format code
format:
	poetry run black email_to_remarkable.py tests/
	poetry run isort email_to_remarkable.py tests/

# Check formatting without making changes
format-check:
	poetry run black --check email_to_remarkable.py tests/
	poetry run isort --check-only email_to_remarkable.py tests/

# Run type checking
type-check:
	poetry run mypy email_to_remarkable.py

# Activate Poetry shell
shell:
	poetry shell

# Show package information
show:
	poetry show

# Update dependencies
update:
	poetry update

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Build package
build: clean
	poetry build

# Note: This package is intended to be installed directly from GitHub
# No publishing commands needed - users should install with:
# pip install git+https://github.com/shano/email-to-remarkable-sync.git

# Run all quality checks
all-checks: lint format-check type-check test-coverage
	@echo "All quality checks passed!"

# Run pre-commit hooks
pre-commit:
	poetry run pre-commit run --all-files

# Development workflow - run before committing
dev-check: format all-checks
	@echo "Development checks completed successfully!"

# Quick start - setup and test
quick-start: setup test
	@echo "Quick start completed! You're ready to develop."