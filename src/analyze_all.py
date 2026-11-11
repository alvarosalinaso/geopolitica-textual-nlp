"""
Orquestador completo: ejecuta todos los scripts de análisis en orden.
"""

import logging
import sys

logger = logging.getLogger(__name__)


def main() -> int:
    logger.info("Pipeline completo: Geopolítica Textual NLP")

    errors = []

    # 1. Export visualizations (includes corpus processing, NER, sentiment, geo, RAG)
    logger.info("[1/3] Ejecutando export_visualizations...")
    try:
        from export_visualizations import main as export_main

        export_main()
    except Exception:
        logger.exception("export_visualizations falló")
        errors.append("export_visualizations")

    # 2. Statistical tests
    logger.info("[2/3] Ejecutando statistical_tests...")
    try:
        from statistical_tests import run_statistical_tests

        run_statistical_tests()
    except Exception:
        logger.exception("statistical_tests falló")
        errors.append("statistical_tests")

    # 3. Generate report
    logger.info("[3/3] Ejecutando generate_report...")
    try:
        from generate_report import generate_report

        generate_report()
    except Exception:
        logger.exception("generate_report falló")
        errors.append("generate_report")

    if errors:
        logger.error("Pipeline completado con errores: %s", ", ".join(errors))
    else:
        logger.info("Pipeline completado exitosamente")

    return 1 if errors else 0


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    sys.exit(main())
