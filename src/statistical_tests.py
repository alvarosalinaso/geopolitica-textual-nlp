"""Tests estadisticos para analisis geopolitico."""

import json
from pathlib import Path

try:
    import numpy as np
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def _to_json_serializable(obj):
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
        print(
            "[STATS] ner_entities.json no encontrado - ejecutar ner_analysis.py primero"
        )
        return {}

    with open(ner_file, encoding="utf-8") as f:
        data = json.load(f)

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
        expected = [total / len(types)] * len(types)
        chi2, p_chi = stats.chisquare(counts, expected)

        # Cramér's V (corrección para muestras grandes)
        n = total
        k = len(types)
        cramers_v = (chi2 / (n * (k - 1))) ** 0.5 if n > 0 and k > 1 else 0.0

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
        print(
            f"[STATS] Chi2: chi2={chi2:.3f}, p={p_chi:.4f}, Cramér's V={cramers_v:.3f}"
        )

    # Convert all numpy types to Python native types
    results = _to_json_serializable(results)

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results
