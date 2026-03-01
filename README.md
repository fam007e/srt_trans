# SRT Translator

[![Build Status](https://github.com/fam007e/srt_trans/actions/workflows/ci.yml/badge.svg)](https://github.com/fam007e/srt_trans/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A robust and feature-rich Python command-line tool for translating SubRip (SRT) subtitle files. Supports Google Translate, DeepL, and MyMemory with intelligent mixed-language handling, HTML tag preservation, and resilient error recovery.

## ✨ Features

*   **Modular Architecture:** Easy to extend with new translation services.
*   **Multiple Services:** Google Translate (default), DeepL, and MyMemory.
*   **Resilient Recovery:** Automatic retries with exponential backoff and resume capability for interrupted translations.
*   **Parallel Processing:** Use `--workers` to speed up translation of large files.
*   **Mixed-Language Handling:** Sentence-level language detection for mixed subtitles.
*   **HTML Tag Preservation:** Keeps `<i>`, `<b>`, etc., styling intact.
*   **Batch Processing:** Translate multiple files or entire directories at once.
*   **Configuration:** Support for `.env` files for secure API key management.

## 🚀 Quick Start

### Installation

1.  **From PyPI (Recommended)**:
    ```bash
    pip install srt-translator-cli
    ```

2.  **From Source**:
    ```bash
    git clone https://github.com/fam007e/srt_trans.git
    cd srt_trans
    pip install .
    ```

### Developer Setup

For developers wanting to run tests and build the package, we provide a `Makefile`:

```bash
# 1. Create venv
python -m venv .venv

# 2. Setup all dev/test dependencies
make setup

# 3. Run all checks (lint, type-check, tests)
make check

# 4. Build binary
make build

# 5. (Optional) Install in editable mode
pip install -e .
```

### Basic Usage

```bash
srt-translator-cli movie.srt -t es
```

## 📚 Documentation

For more detailed information, please see our dedicated documentation:

*   [**Usage Guide**](docs/USAGE.md) - Deep dive into CLI options and examples.
*   [**API Reference**](docs/API.md) - How to use SRT Translator as a library.
*   [**Contributing**](CONTRIBUTING.md) - How to help improve this project.

## 🛠 Supported Languages

SRT Translator supports over 70 languages. Run the following command to see the full list:

```bash
srt-translator-cli --list-languages
```

## ⚖ License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

*   [deep-translator](https://github.com/nidhaloff/deep-translator)
*   [pysrt](https://github.com/byroot/pysrt)
*   [langdetect](https://github.com/Mimino666/langdetect)
*   [nltk](https://github.com/nltk/nltk)
