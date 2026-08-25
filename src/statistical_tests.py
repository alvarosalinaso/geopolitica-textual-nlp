"""Tests estadisticos para analisis geopolitico."""

import json
from collections import Counter
from pathlib import Path

try:
    import numpy as np  # noqa: F401
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


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

    # Chi-squared: entity type distribution
    entities = data.get("top_entities", [])
    if entities:
        type_counts = Counter(e["label"] for e in entities)
        types = list(type_counts.keys())
        counts = list(type_counts.values())
        if len(types) >= 2:
            expected = [sum(counts) / len(types)] * len(types)
            chi2, p_chi = stats.chisquare(counts, expected)
            results["chi_squared_entity_types"] = {
                "test": "Chi-squared goodness of fit",
                "h0": "Las entidades se distribuyen uniformemente entre tipos",
                "chi2_statistic": round(chi2, 4),
                "p_value": round(p_chi, 6),
                "significant": p_chi < 0.05,
                "observed_distribution": dict(type_counts),
                "degrees_freedom": len(types) - 1,
            }
            print(f"[STATS] Chi2: chi2={chi2:.3f}, p={p_chi:.4f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results
