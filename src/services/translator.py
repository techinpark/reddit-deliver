"""
Translation service using DeepL API.

Handles translation of post titles and content with caching support.
"""

import os
import deepl
from typing import Optional, Tuple
from lib.logger import get_logger
from services.base_translator import BaseTranslator

logger = get_logger("deepl_translator")


class Translator(BaseTranslator):
    """
    Translation service using DeepL API.

    Provides translation with language detection and caching support.
    """

    def __init__(self):
        """Initialize DeepL translator with API key from environment."""
        api_key = os.environ.get('DEEPL_API_KEY')

        if not api_key:
            raise ValueError(
                "DeepL API key not found. "
                "Please set DEEPL_API_KEY environment variable."
            )

        self.translator = deepl.Translator(api_key)
        logger.info("DeepL translator initialized")

    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'ko', 'ja', 'es')
            source_lang: Source language code (optional, auto-detected if not provided)

        Returns:
            Tuple of (translated_text, detected_source_lang)

        Raises:
            Exception: If translation fails
        """
        if not text or not text.strip():
            return "", "unknown"

        try:
            # Truncate very long text to avoid quota issues
            # DeepL free tier: 500k chars/month
            max_length = 10000
            if len(text) > max_length:
                logger.warning(f"Text truncated from {len(text)} to {max_length} chars")
                text = text[:max_length] + "..."

            # Translate
            result = self.translator.translate_text(
                text,
                target_lang=target_lang.upper(),
                source_lang=source_lang.upper() if source_lang else None
            )

            translated_text = result.text
            detected_lang = result.detected_source_lang.lower()

            logger.debug(f"Translated {len(text)} chars ({detected_lang} → {target_lang})")

            return translated_text, detected_lang

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

    def translate_post(
        self,
        title: str,
        content: Optional[str],
        target_lang: str
    ) -> Tuple[str, Optional[str], str]:
        """
        Translate post title and content.

        Args:
            title: Post title
            content: Post content (may be None or empty)
            target_lang: Target language code

        Returns:
            Tuple of (translated_title, translated_content, detected_source_lang)
        """
        # Translate title
        translated_title, source_lang = self.translate(title, target_lang)

        # Translate content if present
        translated_content = None
        if content and content.strip():
            translated_content, _ = self.translate(content, target_lang, source_lang)

        logger.info(
            f"Post translated: {source_lang} → {target_lang} "
            f"(title: {len(title)} chars, content: {len(content or '')} chars)"
        )

        return translated_title, translated_content, source_lang

    def get_usage(self) -> dict:
        """
        Get API usage statistics.

        Returns:
            Dictionary with usage info (character count, limit)
        """
        try:
            usage = self.translator.get_usage()
            return {
                'character_count': usage.character.count,
                'character_limit': usage.character.limit,
                'percentage_used': (usage.character.count / usage.character.limit * 100) if usage.character.limit else 0
            }
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {}

    def check_supported_language(self, lang_code: str) -> bool:
        """
        Check if language is supported by DeepL.

        Args:
            lang_code: Language code (e.g., 'ko', 'ja')

        Returns:
            True if supported, False otherwise
        """
        try:
            target_languages = self.translator.get_target_languages()
            supported_codes = [lang.code.lower() for lang in target_languages]
            return lang_code.lower() in supported_codes
        except Exception as e:
            logger.error(f"Failed to check language support: {e}")
            return False
