"""
Translation Services - Provides an abstraction layer for various translation APIs.
Supported: Google Translate, DeepL, and MyMemory.
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from deep_translator import GoogleTranslator, DeeplTranslator, MyMemoryTranslator
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

# Load environment variables from .env file
load_dotenv()

# Setup logging for retries
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common language codes supported by most translation services
COMMON_LANGUAGE_CODES: Dict[str, str] = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
    'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
    'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)',
    'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
    'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian',
    'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician',
    'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati',
    'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew',
    'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic',
    'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian',
    'ja': 'Japanese', 'jv': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh',
    'km': 'Khmer', 'rw': 'Kinyarwanda', 'ko': 'Korean', 'ku': 'Kurdish',
    'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian',
    'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'mk': 'Macedonian', 'mg': 'Malagasy',
    'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori',
    'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali',
    'no': 'Norwegian', 'ny': 'Nyanja (Chichewa)', 'or': 'Odia (Oriya)', 'ps': 'Pashto',
    'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi',
    'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic',
    'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi',
    'si': 'Sinhala (Sinhalese)', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali',
    'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish',
    'tl': 'Tagalog (Filipino)', 'tg': 'Tajik', 'ta': 'Tamil', 'tt': 'Tatar',
    'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'tk': 'Turkmen',
    'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur', 'uz': 'Uzbek',
    'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish',
    'yo': 'Yoruba', 'zu': 'Zulu'
}


def get_supported_languages() -> str:
    """Return a formatted string of supported language codes."""
    lines: List[str] = ["Supported language codes:"]
    lines.append("-" * 50)
    for code, name in sorted(COMMON_LANGUAGE_CODES.items(), key=lambda x: x[1]):
        lines.append(f"  {code:8} - {name}")
    lines.append("-" * 50)
    lines.append("Note: Actual availability depends on the translation service used.")
    lines.append("Use 'auto' for source language to auto-detect.")
    return "\n".join(lines)


def validate_language_code(code: str, allow_auto: bool = False) -> bool:
    """
    Validate if a language code is likely supported.
    Returns True if valid, False otherwise.
    """
    if allow_auto and code == 'auto':
        return True
    # Accept common codes and also trust user for less common ones
    return code.lower() in COMMON_LANGUAGE_CODES or len(code) in (2, 5)


class BaseTranslator(ABC):
    """Abstract base class for all translators."""
    @abstractmethod
    def translate(self, text: str, dest_lang: str, src_lang: Optional[str] = None) -> str:
        """Translate text from src_lang to dest_lang."""


class GoogleTranslate(BaseTranslator):
    """Translator using Google Translate via deep-translator."""
    def __init__(self) -> None:
        """Initialize Google translator."""
        self.translator = GoogleTranslator()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def translate(self, text: str, dest_lang: str, src_lang: Optional[str] = None) -> str:
        """Translate text using Google with retries."""
        if not text or not text.strip():
            return text
        self.translator.source = src_lang if src_lang and src_lang != 'auto' else 'auto'
        self.translator.target = dest_lang
        try:
            result = self.translator.translate(text)
            return result if result else text
        except Exception as e:
            # Re-raise to trigger tenacity retry
            raise RuntimeError(f"Google Translate error: {e}") from e


class DeepLTranslate(BaseTranslator):
    """Translator using DeepL via deep-translator."""
    def __init__(self) -> None:
        """Initialize DeepL translator using DEEPL_API_KEY env var."""
        api_key = os.getenv("DEEPL_API_KEY")
        if not api_key:
            raise ValueError("DeepL API key not found. Please set the DEEPL_API_KEY environment variable or a .env file.")
        self.api_key = api_key

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def translate(self, text: str, dest_lang: str, src_lang: Optional[str] = None) -> str:
        """Translate text using DeepL with retries."""
        if not text or not text.strip():
            return text
        try:
            # DeepL uses uppercase language codes and requires source to be set correctly
            translator = DeeplTranslator(
                api_key=self.api_key,
                source=src_lang.upper() if src_lang and src_lang != 'auto' else 'auto',
                target=dest_lang.upper()
            )
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            # If it's a 429 or other temporary error, tenacity will retry
            raise RuntimeError(f"DeepL error: {e}") from e

# Mapping from short codes to full MyMemory codes
MYMEMORY_LANG_CODES: Dict[str, str] = {
    'af': 'af-ZA', 'sq': 'sq-AL', 'am': 'am-ET', 'ar': 'ar-SA',
    'hy': 'hy-AM', 'az': 'az-AZ', 'eu': 'eu-ES', 'be': 'be-BY',
    'bn': 'bn-IN', 'bs': 'bs-BA', 'bg': 'bg-BG', 'ca': 'ca-ES',
    'ceb': 'ceb-PH', 'zh-CN': 'zh-CN', 'zh-TW': 'zh-TW', 'zh': 'zh-CN',
    'hr': 'hr-HR', 'cs': 'cs-CZ', 'da': 'da-DK', 'nl': 'nl-NL',
    'en': 'en-GB', 'eo': 'eo-EU', 'et': 'et-EE', 'fi': 'fi-FI',
    'fr': 'fr-FR', 'gl': 'gl-ES', 'ka': 'ka-GE', 'de': 'de-DE',
    'el': 'el-GR', 'gu': 'gu-IN', 'ht': 'ht-HT', 'ha': 'ha-NE',
    'haw': 'haw-US', 'he': 'he-IL', 'hi': 'hi-IN', 'hu': 'hu-HU',
    'is': 'is-IS', 'ig': 'ig-NG', 'id': 'id-ID', 'ga': 'ga-IE',
    'it': 'it-IT', 'ja': 'ja-JP', 'jv': 'jv-ID', 'kn': 'kn-IN',
    'kk': 'kk-KZ', 'km': 'km-KH', 'rw': 'rw-RW', 'ko': 'ko-KR',
    'ku': 'kmr-TR', 'ky': 'ky-KG', 'lo': 'lo-LA', 'la': 'la-XN',
    'lv': 'lv-LV', 'lt': 'lt-LT', 'lb': 'lb-LU', 'mk': 'mk-MK',
    'mg': 'mg-MG', 'ms': 'ms-MY', 'ml': 'ml-IN', 'mt': 'mt-MT',
    'mi': 'mi-NZ', 'mr': 'mr-IN', 'mn': 'mn-MN', 'my': 'my-MM',
    'ne': 'ne-NP', 'no': 'nb-NO', 'ny': 'ny-MW', 'or': 'or-IN',
    'ps': 'ps-PK', 'fa': 'fa-IR', 'pl': 'pl-PL', 'pt': 'pt-PT',
    'pa': 'pa-IN', 'ro': 'ro-RO', 'ru': 'ru-RU', 'sm': 'sm-WS',
    'gd': 'gd-GB', 'sr': 'sr-Latn-RS', 'sn': 'sn-ZW', 'sd': 'sd-PK',
    'si': 'si-LK', 'sk': 'sk-SK', 'sl': 'sl-SI', 'so': 'so-SO',
    'es': 'es-ES', 'su': 'su-ID', 'sw': 'sw-KE', 'sv': 'sv-SE',
    'tl': 'tl-PH', 'tg': 'tg-TJ', 'ta': 'ta-IN', 'tt': 'tt-RU',
    'te': 'te-IN', 'th': 'th-TH', 'tr': 'tr-TR', 'tk': 'tk-TM',
    'uk': 'uk-UA', 'ur': 'ur-PK', 'ug': 'ug-CN', 'uz': 'uz-UZ',
    'vi': 'vi-VN', 'cy': 'cy-GB', 'xh': 'xh-ZA', 'yi': 'yi-YD',
    'yo': 'yo-NG', 'zu': 'zu-ZA'
}


class MyMemoryTranslate(BaseTranslator):
    """
    MyMemory translator - free, no API key required.
    """
    def __init__(self) -> None:
        """Initialize MyMemory translator."""
        pass  # pylint: disable=unnecessary-pass

    def _get_full_code(self, code: Optional[str]) -> str:
        """Convert short code to full MyMemory format."""
        if not code or code == 'auto':
            return 'en-GB'
        code_lower = code.lower()
        # If already a full code (contains hyphen), use as-is
        if '-' in code:
            return code
        # Map short code to full code
        return MYMEMORY_LANG_CODES.get(code_lower, f'{code_lower}-{code_lower.upper()}')

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def translate(self, text: str, dest_lang: str, src_lang: Optional[str] = None) -> str:
        """Translate text using MyMemory with retries."""
        if not text or not text.strip():
            return text
        try:
            source = self._get_full_code(src_lang)
            target = self._get_full_code(dest_lang)
            translator = MyMemoryTranslator(source=source, target=target)
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            # Re-raise to trigger tenacity retry
            raise RuntimeError(f"MyMemory error: {e}") from e


def get_translator(service_name: str) -> BaseTranslator:
    """
    Factory function to get a translator instance by name.
    """
    translators: Dict[str, Type[BaseTranslator]] = {
        'google': GoogleTranslate,
        'deepl': DeepLTranslate,
        'mymemory': MyMemoryTranslate,
    }
    if service_name not in translators:
        raise ValueError(f"Unknown translator: {service_name}. Available: {', '.join(translators.keys())}")
    return translators[service_name]()
