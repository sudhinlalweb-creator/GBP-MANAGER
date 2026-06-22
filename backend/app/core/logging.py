"""Logging configuration for API and worker processes."""

import logging


def configure_logging() -> None:
    """Configure a consistent root logger format."""
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "%(filename)s:%(lineno)d | %(message)s"
        ),
    )
