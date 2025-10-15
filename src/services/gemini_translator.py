"""
Translation service using Google Gemini API.

Handles translation of post titles and content using Gemini.
"""

import os
from google import genai
from typing import Optional, Tuple
from lib.logger import get_logger
from services.base_translator import BaseTranslator

logger = get_logger("gemini_translator")


class GeminiTranslator(BaseTranslator):
    """
    Translation service using Google Gemini API.

    Provides translation with language detection using Gemini's language models.
    """

    # Language code mapping for common languages
    LANG_NAMES = {
        'ko': 'Korean',
        'ja': 'Japanese',
        'zh': 'Chinese',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'en': 'English',
    }

    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        """
        Initialize Gemini translator with API key from environment.

        Args:
            model_name: Gemini model to use (default: gemini-2.5-flash-lite)
        """
        api_key = os.environ.get('GEMINI_API_KEY')

        if not api_key:
            raise ValueError(
                "Gemini API key not found. "
                "Please set GEMINI_API_KEY environment variable."
            )

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        logger.info(f"Gemini translator initialized with model: {model_name}")

    def _get_language_name(self, lang_code: str) -> str:
        """
        Get full language name from code.

        Args:
            lang_code: ISO 639-1 language code

        Returns:
            Full language name or the code itself if not found
        """
        return self.LANG_NAMES.get(lang_code.lower(), lang_code)

    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Translate text to target language using Gemini.

        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'ko', 'ja', 'es')
            source_lang: Source language code (optional, will be detected if not provided)

        Returns:
            Tuple of (translated_text, detected_source_lang)

        Raises:
            Exception: If translation fails
        """
        if not text or not text.strip():
            return "", "unknown"

        try:
            # Truncate very long text
            max_length = 10000
            if len(text) > max_length:
                logger.warning(f"Text truncated from {len(text)} to {max_length} chars")
                text = text[:max_length] + "..."

            target_lang_name = self._get_language_name(target_lang)

            # Detect source language if not provided
            detected_lang = source_lang
            if not source_lang:
                detect_prompt = (
                    f"Identify the language of the following text. "
                    f"Respond with ONLY the ISO 639-1 language code (e.g., 'en', 'ko', 'ja'). "
                    f"Text: {text[:500]}"
                )
                detect_response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=detect_prompt
                )
                detected_lang = detect_response.text.strip().lower()
                logger.debug(f"Detected language: {detected_lang}")

            # Translate
            translate_prompt = (
                f"Translate the following text to {target_lang_name}. "
                f"Provide ONLY the translation without any explanations or additional text.\n\n"
                f"Text to translate:\n{text}"
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=translate_prompt
            )
            translated_text = response.text.strip()

            logger.debug(
                f"Translated {len(text)} chars ({detected_lang} → {target_lang}) "
                f"using {self.model_name}"
            )

            return translated_text, detected_lang

        except Exception as e:
            logger.error(f"Gemini translation failed: {e}")
            raise

    def translate_post(
        self,
        title: str,
        content: Optional[str],
        target_lang: str
    ) -> Tuple[str, Optional[str], str]:
        """
        Translate post title and content using Gemini.

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
            f"Post translated with Gemini: {source_lang} → {target_lang} "
            f"(title: {len(title)} chars, content: {len(content or '')} chars)"
        )

        return translated_title, translated_content, source_lang

    def check_supported_language(self, lang_code: str) -> bool:
        """
        Check if language is supported by Gemini.

        Gemini supports a wide range of languages. This is a basic check
        against known language codes.

        Args:
            lang_code: Language code (e.g., 'ko', 'ja')

        Returns:
            True if supported (Gemini supports most languages)
        """
        # Gemini supports most major languages
        # Return True for known codes, could be expanded
        return lang_code.lower() in self.LANG_NAMES or len(lang_code) == 2

    def get_usage(self) -> dict:
        """
        Get API usage statistics.

        Note: Gemini API doesn't provide usage stats through the SDK,
        so we return an empty dict.

        Returns:
            Empty dictionary (usage tracking not available)
        """
        logger.debug("Usage statistics not available for Gemini API")
        return {}
