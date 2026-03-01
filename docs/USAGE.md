# Usage Guide

SRT Translator is a powerful CLI tool for translating SubRip (SRT) subtitle files.

> **Note:** If you installed via `pip` or using the binary, the command is `srt-translator-cli`.

## Installation

### From Source (Local Development)

To build and install the project locally, it's recommended to use a virtual environment:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/fam007e/srt_trans.git
    cd srt_trans
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Setup dependencies and development environment**:
    ```bash
    make setup
    ```
    This will upgrade `pip`, install all dependencies (including dev and test), and download necessary NLTK data.

4.  **Build a standalone binary**:
    ```bash
    make build
    ```
    The binary will be created in `dist/srt-translator-cli`.

5.  **Install in editable mode** (to run the command globally in your venv):
    ```bash
    pip install -e .
    ```

## Basic Usage

The simplest way to use SRT Translator is to specify an input file and a target language:

```bash
srt-translator-cli movie.srt -t es
```

This will create `movie_es.srt` in the same directory.

## Language Codes

SRT Translator supports 70+ languages. You can see the full list by running:

```bash
srt-translator-cli --list-languages
```

Common codes:
* `en`: English
* `es`: Spanish
* `fr`: French
* `de`: German
* `zh-CN`: Chinese (Simplified)
* `ja`: Japanese
* `bn`: Bengali

## Advanced Options

### Source Language Detection

By default, SRT Translator automatically detects the source language per sentence (great for mixed-language subtitles). If you want to force a specific source language:

```bash
srt-translator-cli movie.srt -t fr -s en
```

### Translation Services

SRT Translator supports multiple translation services:

* `google` (default): Fast and robust.
* `mymemory`: Free alternative, no API key required.
* `deepl`: Higher quality (requires `DEEPL_API_KEY`).

#### Configuration (Environment Variables)

For services like DeepL, you need an API key. You can:
* Set an environment variable: `export DEEPL_API_KEY="your-key-here"`
* Create a `.env` file in the project directory:
  ```env
  DEEPL_API_KEY=your-key-here
  ```

### Resilience & Error Recovery

SRT Translator is designed to handle API interruptions gracefully:

* **Automatic Retries:** If an API call fails due to network issues or rate limits, it will automatically retry with an exponential backoff.
* **Resume Capability:** Progress is automatically saved to a cache directory (`~/.srt_translator_cli_cache`). If a translation is interrupted, running the same command again will pick up exactly where it left off.

To disable this caching behavior, use the `--no-cache` flag:
```bash
srt-translator-cli movie.srt -t es --no-cache
```

### Parallel Processing (Speed Up)

For large movies or batch processing, you can use multiple workers:

```bash
srt-translator-cli movie.srt -t es --workers 4
```

### Batch Processing

You can translate multiple files or entire directories:

```bash
# Multiple files
srt-translator-cli ep1.srt ep2.srt ep3.srt -t es

# Directory
srt-translator-cli ./subtitles_dir/ -t es
```

### Output Directory

Save all translated files to a specific folder:

```bash
srt-translator-cli movie.srt -t es --output_dir ./translated/
```

## HTML Tags

SRT Translator intelligently preserves HTML tags like `<i>`, `<b>`, `<font>`, etc. The tags are extracted before translation and carefully reinserted into the translated text to maintain styling.

## Troubleshooting

### API Limits

If you are using the free services (`google` or `mymemory`), you might occasionally hit rate limits for very large files. If this happens, try:
* Reducing the number of `--workers`.
* Waiting a few minutes before trying again.

### Encoding Issues

SRT Translator automatically detects file encoding. If you have an unusual encoding, it's recommended to convert the file to UTF-8 first for best results.
