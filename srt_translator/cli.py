"""
SRT Translator CLI - Command-line interface for translating SRT subtitle files.
Supports multiple translation services, concurrent processing, and batch operations.
"""
import argparse
import os
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional, Any, Dict
from tqdm import tqdm
from srt_translator.srt_parser import SrtParser
from srt_translator.translators import get_translator, get_supported_languages, validate_language_code, BaseTranslator
from srt_translator import __version__


def get_file_hash(filepath: str) -> str:
    """Generate a simple hash of the file path and size for state tracking."""
    stats = os.stat(filepath)
    hash_input = f"{filepath}_{stats.st_size}_{stats.st_mtime}"
    return hashlib.md5(hash_input.encode()).hexdigest()


class TranslationState:
    """Handles persistence of translation progress."""
    def __init__(self, input_file: str, output_lang: str, translator: str):
        self.state_dir = os.path.join(os.path.expanduser("~"), ".srt_translator_cli_cache")
        os.makedirs(self.state_dir, exist_ok=True)
        
        file_hash = get_file_hash(input_file)
        self.state_file = os.path.join(self.state_dir, f"{file_hash}_{output_lang}_{translator}.json")
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save(self, results: Dict[int, str]) -> None:
        """Save current progress to disk."""
        self.data['translated_blocks'] = results
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False)

    def get_translated_blocks(self) -> Dict[int, str]:
        """Return already translated blocks from state."""
        # JSON keys are always strings, convert back to int
        blocks = self.data.get('translated_blocks', {})
        return {int(k): v for k, v in blocks.items()}

    def clear(self) -> None:
        """Remove state file after successful completion."""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)


def translate_block(block_data: Tuple[int, str, BaseTranslator, str, str]) -> Tuple[int, str]:
    """
    Translate a single subtitle block.

    Args:
        block_data: Tuple of (index, text, translator, output_lang, source_lang)

    Returns:
        Tuple of (index, translated_text)
    """
    idx, original_text, translator, output_lang, source_lang = block_data

    try:
        # Clean text and extract tags
        cleaned_text, tags = SrtParser.clean_text(original_text)
        sentences = SrtParser.split_into_sentences(cleaned_text)

        translated_sentences: List[str] = []
        for sentence in sentences:
            detected_lang = SrtParser.detect_language(sentence)

            # Determine source language for this sentence
            current_source_lang = source_lang
            if source_lang == 'auto' and detected_lang != 'unknown':
                current_source_lang = detected_lang
            elif source_lang != 'auto' and detected_lang != 'unknown' and detected_lang != source_lang:
                current_source_lang = detected_lang

            # Translate sentence
            translated_sentence = translator.translate(sentence, output_lang, current_source_lang)
            translated_sentences.append(translated_sentence)

        # Reassemble translated sentences
        translated_cleaned_text = " ".join(translated_sentences)

        # Reinsert tags into the fully translated text
        final_translated_text = SrtParser.reinsert_tags(translated_cleaned_text, tags)
        return (idx, final_translated_text)
    except Exception:
        # On error, return original text
        return (idx, original_text)


def translate_single_srt(input_file: str, output_lang: str, source_lang: str, translator_service: str, *,
                         output_dir: Optional[str] = None, workers: int = 1, _batch_size: int = 10,
                         use_cache: bool = True) -> str:
    """
    Translate a single SRT file with resume support.
    """
    try:
        # Validate target language code
        if not validate_language_code(output_lang):
            raise ValueError(f"'{output_lang}' may not be a valid language code. Use --list-languages to see supported codes.")

        # Parse SRT
        srt_parser = SrtParser(input_file)
        original_subtitle_blocks = srt_parser.get_subtitles_text()
        total_blocks = len(original_subtitle_blocks)

        if total_blocks == 0:
            return f'Warning: No subtitles found in {input_file}'

        # Initialize translator
        translator = get_translator(translator_service)
        
        # State management for resume capability
        state = TranslationState(input_file, output_lang, translator_service)
        results_map = state.get_translated_blocks() if use_cache else {}
        
        if len(results_map) > 0:
            print(f"  Resuming from {len(results_map)}/{total_blocks} translated blocks...")

        # Prepare work items (only for those not already translated)
        work_items: List[Tuple[int, str, BaseTranslator, str, str]] = [
            (i, text, translator, output_lang, source_lang)
            for i, text in enumerate(original_subtitle_blocks)
            if i not in results_map
        ]

        if work_items:
            # Translate with concurrency if workers > 1
            if workers > 1 and len(work_items) > 5:
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    futures = {executor.submit(translate_block, item): item[0] for item in work_items}
                    # Save state periodically (every 10 blocks or so)
                    count = 0
                    for future in tqdm(as_completed(futures), total=len(work_items),
                                       desc=f"  {os.path.basename(input_file)}", leave=False):
                        idx, translated_text = future.result()
                        results_map[idx] = translated_text
                        count += 1
                        if count % 10 == 0:
                            state.save(results_map)
            else:
                # Sequential translation with progress
                for item in tqdm(work_items, desc=f"  {os.path.basename(input_file)}", leave=False):
                    idx, translated_text = translate_block(item)
                    results_map[idx] = translated_text
                    state.save(results_map)
            
            # Final save
            state.save(results_map)

        # Update and save SRT
        translated_subtitle_blocks = [results_map.get(i, original_subtitle_blocks[i]) for i in range(total_blocks)]
        srt_parser.update_subtitles_text(translated_subtitle_blocks)

        # Determine output file path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.basename(input_file)
            base, ext = os.path.splitext(base_name)
            output_file = os.path.join(output_dir, f'{base}_{output_lang}{ext}')
        else:
            base, ext = os.path.splitext(input_file)
            output_file = f'{base}_{output_lang}{ext}'

        srt_parser.write_srt(output_file)
        
        # Success! Clear the cache
        state.clear()
        
        return f'✓ Translated {input_file} → {output_file} ({total_blocks} subtitles)'

    except FileNotFoundError:
        return f'✗ Error: Input file not found at {input_file}'
    except ValueError as ve:
        return f'✗ Configuration Error for {input_file}: {ve}'
    except Exception as e:
        return f'✗ Error for {input_file}: {e}'


# Alias for test compatibility
def translate_srt_file(input_file: str, target_language: str, source_language: str = 'auto', output_file: Optional[str] = None) -> str:
    """Legacy function for backward compatibility."""
    output_dir = os.path.dirname(output_file) if output_file else None
    return translate_single_srt(input_file, target_language, source_language, 'google', output_dir=output_dir)


def collect_srt_files(input_paths: List[str]) -> List[str]:
    """Collect all SRT files from paths and directories."""
    srt_files: List[str] = []
    for path in input_paths:
        if os.path.isfile(path) and path.lower().endswith('.srt'):
            srt_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.srt'):
                        srt_files.append(os.path.join(root, file))
    return srt_files


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='srt-translator-cli',
        description='Translate SRT subtitle files to any language.',
        epilog='Examples:\n'
               '  %(prog)s movie.srt -t es                      # Translate to Spanish\n'
               '  %(prog)s ./subs/ -t fr --translator mymemory  # Directory to French\n'
               '  %(prog)s movie.srt -t de --workers 4          # Parallel translation\n'
               '  %(prog)s --list-languages                     # Show supported languages',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--list-languages', action='store_true',
                        help='Display supported language codes and exit.')
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {__version__}',
                        help='Display the version and exit.')
    parser.add_argument('input_paths', type=str, nargs='*',
                        help='Path(s) to input SRT files or directories containing SRT files.')
    parser.add_argument('-t', '--target', dest='output_lang', type=str,
                        help='Target language code for translation (e.g., en, es, fr, bn, zh-CN).')
    parser.add_argument('-s', '--source_lang', type=str, default='auto',
                        help='Source language code (e.g., en, es, fr). Defaults to auto-detect.')
    parser.add_argument('--translator', type=str, default='google',
                        choices=['google', 'deepl', 'mymemory'],
                        help='Translation service: google (default), deepl (requires API key), mymemory (free).')
    parser.add_argument('--output_dir', type=str,
                        help='Directory to save translated files. If not provided, files are saved next to originals.')
    parser.add_argument('--workers', '-w', type=int, default=1,
                        help='Number of parallel workers for translation (default: 1, max: 8).')
    parser.add_argument('--no-cache', action='store_false', dest='use_cache',
                        help="Disable progress caching (don't resume from previous run).")

    args = parser.parse_args()

    # Handle --list-languages first
    if args.list_languages:
        print(get_supported_languages())
        return

    # Validate required arguments when not listing languages
    if not args.input_paths:
        parser.error("input_paths is required. Provide path(s) to SRT files or directories.")
    if not args.output_lang:
        parser.error("--target/-t is required. Specify the target language code (e.g., -t es).")

    # Validate and clamp workers
    workers = max(1, min(args.workers, 8))
    if args.workers > 8:
        print(f"Warning: workers capped at 8 (requested {args.workers})")

    # Validate language codes
    if not validate_language_code(args.output_lang):
        print(f"Warning: '{args.output_lang}' may not be a recognized language code.")
        print("Use --list-languages to see common language codes.")

    if args.source_lang != 'auto' and not validate_language_code(args.source_lang):
        print(f"Warning: '{args.source_lang}' may not be a recognized language code.")

    # Collect SRT files
    srt_files_to_translate = collect_srt_files(args.input_paths)

    if not srt_files_to_translate:
        print("No SRT files found to translate.")
        return

    # Print summary
    worker_info = f" with {workers} workers" if workers > 1 else ""
    print(f'Translating {len(srt_files_to_translate)} SRT file(s) to {args.output_lang} '
          f'using {args.translator}{worker_info}...\n')

    # Translate files
    results: List[str] = []
    for srt_file in srt_files_to_translate:
        result = translate_single_srt(
            srt_file, args.output_lang, args.source_lang,
            args.translator, output_dir=args.output_dir, workers=workers,
            use_cache=args.use_cache
        )
        results.append(result)
        print(result)

    # Summary
    success_count = sum(1 for r in results if r.startswith('✓'))
    error_count = len(results) - success_count
    print(f"\n--- Summary: {success_count} succeeded, {error_count} failed ---")


if __name__ == '__main__':
    main()
