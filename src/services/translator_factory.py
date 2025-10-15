"""
Translator factory for creating appropriate translator instances.

Provides a unified interface for creating translators based on configuration.
"""

from typing import Optional
from lib.logger import get_logger
from services.base_translator import BaseTranslator

logger = get_logger("translator_factory")


class TranslatorFactory:
    """
    Factory for creating translator instances based on service type.

    Supports DeepL and Gemini translation services.
    """

    @staticmethod
    def create_translator(
        service_type: str,
        **kwargs
    ) -> BaseTranslator:
        """
        Create a translator instance based on service type.

        Args:
            service_type: Type of translator ('deepl' or 'gemini')
            **kwargs: Additional arguments passed to translator constructor

        Returns:
            BaseTranslator instance

        Raises:
            ValueError: If service_type is not supported
            Exception: If translator initialization fails
        """
        service_type = service_type.lower().strip()

        if service_type == 'deepl':
            from services.translator import Translator
            logger.info("Creating DeepL translator")
            return Translator()

        elif service_type == 'gemini':
            from services.gemini_translator import GeminiTranslator
            model_name = kwargs.get('model_name', 'gemini-2.5-flash-lite')
            logger.info(f"Creating Gemini translator with model: {model_name}")
            return GeminiTranslator(model_name=model_name)

        else:
            raise ValueError(
                f"Unsupported translator service: '{service_type}'. "
                f"Supported services: 'deepl', 'gemini'"
            )

    @staticmethod
    def get_available_services() -> list:
        """
        Get list of available translator services.

        Returns:
            List of service names
        """
        return ['deepl', 'gemini']

    @staticmethod
    def validate_service(service_type: str) -> bool:
        """
        Check if a translator service is valid.

        Args:
            service_type: Service type to validate

        Returns:
            True if valid, False otherwise
        """
        return service_type.lower() in TranslatorFactory.get_available_services()
