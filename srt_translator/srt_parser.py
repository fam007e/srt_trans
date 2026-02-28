"""
SRT Parser - Handles reading, parsing, and writing SRT subtitle files.
Also provides utility methods for text cleaning and language detection.
"""
import re
from typing import List, Tuple
import pysrt
from nltk.tokenize import sent_tokenize
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Alias Subtitle to pysrt.SubRipItem for test compatibility
Subtitle = pysrt.SubRipItem

# Ensure reproducibility for langdetect
DetectorFactory.seed = 0

class SrtParser:
    """
    Parser for SRT files using pysrt.
    """
    def __init__(self, input_file: str) -> None:
        """Initialize parser with an input SRT file."""
        # Use open() with utf-8-sig to handle BOM correctly and avoid codecs.open() warning
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            self.subs = pysrt.from_string(f.read())

    def get_subtitles_text(self) -> List[str]:
        """Return a list of text content from all subtitles."""
        return [sub.text for sub in self.subs]

    def get_subtitles_text_blocks(self) -> List[pysrt.SubRipItem]:
        """Return the list of SubRipItem objects."""
        return self.subs

    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Detect file encoding using chardet."""
        import chardet  # pylint: disable=import-outside-toplevel
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding'] or 'utf-8'

    def update_subtitles_text(self, translated_texts: List[str]) -> None:
        """Update subtitle objects with new translated text."""
        for i, sub in enumerate(self.subs):
            if i < len(translated_texts):
                sub.text = translated_texts[i]

    def write_srt(self, output_file: str) -> None:
        """Save the subtitles to a file in UTF-8 encoding."""
        # Use open() with utf-8 to avoid codecs.open() warning
        with open(output_file, 'w', encoding='utf-8') as f:
            self.subs.write_into(f)

    @staticmethod
    def clean_text(text: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Extract HTML tags and return cleaned text with placeholders.

        Args:
            text: Original subtitle text with HTML tags.

        Returns:
            Tuple of (cleaned_text, tags_list).
        """
        tags: List[Tuple[str, str]] = []
        # Find all HTML tags and replace them with placeholders
        def replace_tag(match: re.Match) -> str:
            tag = match.group(0)
            placeholder = f'__TAG_{len(tags)}__'
            tags.append((placeholder, tag))
            return placeholder

        cleaned_text = re.sub(r'<[^>]*>', replace_tag, text)
        # Remove multiple spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text.strip(), tags

    @staticmethod
    def reinsert_tags(text: str, tags: List[Tuple[str, str]]) -> str:
        """Reinsert HTML tags into translated text using placeholders."""
        # Reinsert HTML tags from placeholders
        for placeholder, tag in tags:
            text = text.replace(placeholder, tag)
        return text

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences using NLTK."""
        return sent_tokenize(text)

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language code of the given text."""
        try:
            return detect(text)
        except LangDetectException:
            return 'unknown'
