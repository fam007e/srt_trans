# API Reference

SRT Translator can be used as a Python library.

## Installation

```bash
# Recommended: Use a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -e .
```

## Quick Start

```python
from srt_translator import translate_single_srt

result = translate_single_srt(
    input_file='movie.srt',
    output_lang='es',
    source_lang='auto',
    translator_service='google'
)
print(result)
```

## Core Components

### `SrtParser`

Handles reading, parsing, and writing SRT files.

```python
from srt_translator import SrtParser

parser = SrtParser('movie.srt')
subtitles = parser.get_subtitles_text()
# ... do something with subtitles ...
parser.update_subtitles_text(translated_subtitles)
parser.write_srt('movie_translated.srt')
```

### `get_translator`

Factory function to get a translator instance.

```python
from srt_translator import get_translator

translator = get_translator('google')
translated_text = translator.translate("Hello world", dest_lang='es', src_lang='en')
```

### `translate_block`

Internal function used for parallel translation of subtitle blocks.

```python
from srt_translator import translate_block, get_translator

translator = get_translator('google')
# item format: (index, text, translator, output_lang, source_lang)
item = (0, "Hello world", translator, 'es', 'en')
idx, translated_text = translate_block(item)
```

## Supported Translators

The following translator classes implement the `BaseTranslator` interface:

* `GoogleTranslate`
* `DeepLTranslate`
* `MyMemoryTranslate`

All of them have a `translate(text, dest_lang, src_lang=None)` method.
