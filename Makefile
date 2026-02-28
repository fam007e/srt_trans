# Makefile for SRT Translator

VENV_DIR = .venv

# Detect OS and set VENV_BIN
ifeq ($(OS),Windows_NT)
    VENV_BIN = Scripts
else
    # Check if we are in a bash-like shell on Windows
    ifneq ($(findstring NT,$(shell uname -s)),)
        VENV_BIN = Scripts
    else
        VENV_BIN = bin
    endif
endif

VENV_PIP = $(VENV_DIR)/$(VENV_BIN)/pip
VENV_PYTHON = $(VENV_DIR)/$(VENV_BIN)/python
VENV_PYINSTALLER = $(VENV_DIR)/$(VENV_BIN)/pyinstaller

.PHONY: setup test lint type-check check build clean help

setup:
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -e ".[dev,test]"
	$(VENV_PYTHON) -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

test:
	$(VENV_PYTHON) -m pytest tests/ -v --cov=srt_translator --cov-report=term-missing -m "not network"

lint:
	$(VENV_PYTHON) -m ruff check srt_translator/

type-check:
	$(VENV_PYTHON) -m mypy srt_translator/ --ignore-missing-imports

check: lint type-check test
	@echo "All checks passed!"

build:
	PYTHONPATH=. $(VENV_PYINSTALLER) --onefile --name srt_translator srt_translator/cli.py
	@echo "Binary created in dist/srt_translator"

clean:
	rm -rf .pytest_cache .coverage coverage.xml htmlcov .mypy_cache .ruff_cache
	rm -rf build/ dist/ *.spec
	find . -type d -name "__pycache__" -exec rm -rf {} +

help:
	@echo "Available targets:"
	@echo "  setup         - Install all dependencies for development"
	@echo "  test          - Run tests with coverage"
	@echo "  lint          - Run ruff linter"
	@echo "  type-check    - Run mypy type checker"
	@echo "  check         - Run all checks (lint, type-check, test)"
	@echo "  build         - Build a standalone binary using PyInstaller"
	@echo "  clean         - Remove temporary files and build artifacts"
