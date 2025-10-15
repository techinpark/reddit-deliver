"""
Base translator interface for all translation services.

Defines the contract that all translator implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BaseTranslator(ABC):
    """
    Abstract base class for translation services.

    All translator implementations (DeepL, Gemini, etc.) must inherit from this class.
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def check_supported_language(self, lang_code: str) -> bool:
        """
        Check if language is supported by the translator.

        Args:
            lang_code: Language code (e.g., 'ko', 'ja')

        Returns:
            True if supported, False otherwise
        """
        pass

    def get_usage(self) -> dict:
        """
        Get API usage statistics (optional, may not be supported by all translators).

        Returns:
            Dictionary with usage info or empty dict if not supported
        """
        return {}
