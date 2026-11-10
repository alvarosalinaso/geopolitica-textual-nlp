"""Configuración central de logging para los entrypoints del pipeline.

Los módulos solo crean ``logging.getLogger(__name__)``; únicamente los bloques
``if __name__ == "__main__"`` llaman a :func:`setup_logging`.
"""

from __future__ import annotations

import logging
import os

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int | str | None = None) -> None:
    """Configura el root logger una sola vez.

    El nivel se toma de ``level`` o de la variable de entorno ``LOG_LEVEL``
    (por defecto ``INFO``).
    """
    resolved = level if level is not None else os.environ.get("LOG_LEVEL", "INFO")
    if isinstance(resolved, str):
        resolved = resolved.upper()
    logging.basicConfig(level=resolved, format=LOG_FORMAT, datefmt=DATE_FORMAT)
