"""Language detection module using langdetect library.

This replaces the deprecated cld2-cffi library which is not Python 3 compatible.
"""

import logging
import re

from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent results
DetectorFactory.seed = 0

# Pattern to remove illegal characters that may cause issues
illegal_chars = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')


def detect_language(text):
    """Detect the language of the given text.

    Args:
        text: The text to analyze for language detection.

    Returns:
        A two-letter ISO 639-1 language code (e.g., 'en', 'es', 'ja'),
        or None if detection fails or is unreliable.
    """
    # Clean the text of illegal characters
    text = illegal_chars.sub('', text)

    if not text or not text.strip():
        return None

    try:
        # langdetect returns ISO 639-1 codes like 'en', 'es', 'zh-cn', etc.
        lang = detect(text)
        # Normalize codes like 'zh-cn' to just 'zh'
        if '-' in lang:
            lang = lang.split('-')[0]
        return lang
    except LangDetectException:
        logging.debug('Language detection failed for text: %r', text[:100] if len(text) > 100 else text)
        return None
    except Exception:
        logging.exception('Error processing text for language detection: %r', text[:100] if len(text) > 100 else text)
        return None
