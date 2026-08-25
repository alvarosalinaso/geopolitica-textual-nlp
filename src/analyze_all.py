"""
Orquestador completo: ejecuta todos los scripts de análisis en orden.
"""

import sys


def main():
    print("=" * 60)
    print("  Pipeline completo: Geopolítica Textual NLP")
    print("=" * 60)

    errors = []

    # 1. Export visualizations (includes corpus processing, NER, sentiment, geo, RAG)
    print("\n[1/3] Ejecutando export_visualizations...")
    try:
        from export_visualizations import main as export_main

        export_main()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] export_visualizations: {e}")
        errors.append("export_visualizations")

    # 2. Statistical tests
    print("\n[2/3] Ejecutando statistical_tests...")
    try:
        from statistical_tests import run_statistical_tests

        run_statistical_tests()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] statistical_tests: {e}")
        errors.append("statistical_tests")

    # 3. Generate report
    print("\n[3/3] Ejecutando generate_report...")
    try:
        from generate_report import generate_report

        generate_report()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] generate_report: {e}")
        errors.append("generate_report")

    print("\n" + "=" * 60)
    if errors:
        print(f"  Pipeline completado con errores: {', '.join(errors)}")
    else:
        print("  Pipeline completado exitosamente")
    print("=" * 60)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
