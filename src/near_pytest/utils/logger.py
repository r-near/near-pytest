# src/near_pytest/utils/logger.py
"""Simple logging utility for near-pytest using rich."""

import os
import logging
from rich.console import Console
from rich.logging import RichHandler

# Create console for rich output
console = Console()

# Create logger
logger = logging.getLogger("near-pytest")


# Configure handler
def configure_logging(level=None):
    """Configure the logger with the specified level."""
    # Determine log level from environment variable if not specified
    if level is None:
        env_level = os.environ.get("NEAR_PYTEST_LOG_LEVEL", "ERROR").upper()
        level = getattr(logging, env_level, logging.ERROR)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Configure logger
    logger.setLevel(level)

    # Create and add rich handler
    handler = RichHandler(
        console=console, rich_tracebacks=True, show_time=False, markup=True
    )
    logger.addHandler(handler)


# Initialize with default level
configure_logging()


# Simple shortcut functions
def debug(msg, *args, **kwargs):
    """Log a debug message."""
    logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """Log an info message."""
    logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    """Log a warning message."""
    logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    """Log an error message."""
    logger.error(msg, *args, **kwargs)


def success(msg, *args, **kwargs):
    """Log a success message with green color."""
    logger.debug(f"[green]{msg}[/green]", *args, **kwargs)
