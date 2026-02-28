# Makefile for SRT Translator

.PHONY: setup test lint type-check check clean help

setup:
	pip install -e .
	pip install -r test_requirements.txt
	pip install ruff mypy tenacity python-dotenv
	pip install types-requests types-setuptools types-tqdm
	python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

test:
	pytest tests/ -v --cov=srt_translator --cov-report=term-missing -m "not network"

lint:
	ruff check srt_translator/

type-check:
	mypy srt_translator/ --ignore-missing-imports

check: lint type-check test
	@echo "All checks passed!"

clean:
	rm -rf .pytest_cache .coverage coverage.xml htmlcov .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

help:
	@echo "Available targets:"
	@echo "  setup         - Install all dependencies for development"
	@echo "  test          - Run tests with coverage"
	@echo "  lint          - Run ruff linter"
	@echo "  type-check    - Run mypy type checker"
	@echo "  check         - Run all checks (lint, type-check, test)"
	@echo "  clean         - Remove temporary files"
