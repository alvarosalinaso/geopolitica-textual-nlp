"""Tests estadisticos para analisis geopolitico."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    import numpy as np
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from src.data_loader import load_json, write_json
    from src.metrics import cramers_v as compute_cramers_v
    from src.metrics import uniform_expected
except ImportError:  # ejecución directa: python src/statistical_tests.py
    from data_loader import load_json, write_json
    from metrics import cramers_v as compute_cramers_v
    from metrics import uniform_expected

logger = logging.getLogger(__name__)


def _to_json_serializable(obj: Any) -> Any:
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, (np.bool_, np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, dict):
        return {k: _to_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_serializable(v) for v in obj]
    return obj


def run_statistical_tests(
    data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")
) -> dict:
    if not SCIPY_AVAILABLE:
        return {}

    ner_file = data_dir / "ner_entities.json"
    if not ner_file.exists():
        logger.warning(
            "ner_entities.json no encontrado - ejecutar ner_analysis.py primero"
        )
        return {}

    data = load_json(ner_file)

    results = {}

    # Chi-squared: distribución de menciones por tipo de entidad
    # Fuente preferida: label_totals (conteo completo de ner_analysis).
    # Fallback: sumar 'count' sobre top_entities (solo si label_totals ausente),
    # con advertencia explícita de que es una aproximación del top-N truncado.
    label_totals = data.get("label_totals", {})
    fallback_note = None
    if not label_totals:
        entities = data.get("top_entities", [])
        if entities:
            agg = {}
            for e in entities:
                lbl = e.get("label", "?")
                agg[lbl] = agg.get(lbl, 0) + int(e.get("count", 1))
            label_totals = agg
            fallback_note = (
                "label_totals ausente en ner_entities.json: approx. desde "
                "top_entities (solo top-N, subestima tipos poco frecuentes). "
                "Re-ejecutar ner_analysis.py para obtener conteos completos."
            )
    if label_totals and len(label_totals) >= 2:
        types = list(label_totals.keys())
        counts = list(label_totals.values())
        total = sum(counts)
        expected = uniform_expected(counts)
        chi2, p_chi = stats.chisquare(counts, expected)

        cramers_v = compute_cramers_v(chi2, total, len(types))

        caveats = [
            "Baseline uniforme es una heurística, no una teoría sustantiva; los modelos NER tienen sesgos de anotación por tipo.",
            "Cramér's V > 0.3 sugiere efecto mediano, > 0.5 fuerte (regla de Cohen heurística).",
        ]
        if fallback_note:
            caveats.append(fallback_note)
        results["chi_squared_entity_types"] = {
            "test": "Chi-squared goodness of fit",
            "h0": "Las entidades se distribuyen uniformemente entre tipos",
            "chi2_statistic": round(chi2, 4),
            "p_value": round(p_chi, 6),
            "significant": bool(p_chi < 0.05),
            "observed_distribution": dict(label_totals),
            "degrees_freedom": len(types) - 1,
            "cramers_v": round(cramers_v, 4),
            "n_total": total,
            "caveats": caveats,
        }
        logger.info("Chi2: chi2=%.3f, p=%.4f, Cramér's V=%.3f", chi2, p_chi, cramers_v)

    # Convert all numpy types to Python native types
    results = _to_json_serializable(results)

    write_json(results, output_dir / "statistical_tests.json")
    return results


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    run_statistical_tests()
