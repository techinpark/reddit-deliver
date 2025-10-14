"""
Structured logging configuration for reddit-deliver.

Provides consistent logging across all modules with support for
both human-readable console output and structured logging.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "reddit-deliver",
    level: int = logging.INFO,
    verbose: bool = False
) -> logging.Logger:
    """
    Configure and return a logger with structured output.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        verbose: Enable verbose/debug output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level based on verbose flag
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else level)

    # Format: [LEVEL] Module: Message
    formatter = logging.Formatter(
        fmt='[%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the standard configuration.

    Args:
        name: Logger name (default: reddit-deliver)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"reddit-deliver.{name}")
    return logging.getLogger("reddit-deliver")
